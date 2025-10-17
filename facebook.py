import os
import json
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from driver_factory import create_driver


driver = create_driver(for_facebook=True)
wait = WebDriverWait(driver, 20)  

FB_EMAIL = os.environ.get("FB_EMAIL", "nhanmangaytho99@gmail.com")
FB_PASS = os.environ.get("FB_PASS", "xxxxxx")
WAIT_TIME = 20


def try_find_and_click(driver, selector, by=By.CSS_SELECTOR, timeout=8):
    try:
        el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, selector)))
        el.click()
        return True
    except Exception:
        return False


def login_facebook(driver, wait, email=FB_EMAIL, password=FB_PASS):
    print("🔐 Bắt đầu đăng nhập Facebook...")
    driver.get("https://www.facebook.com/login")
    current_url = driver.current_url
    if "login" not in current_url and "checkpoint" not in current_url:
        print("✅ Đã đăng nhập sẵn vào Facebook, bỏ qua bước login.")
        return True
    
    try:
        email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_input.clear()
        email_input.send_keys(email)

        pass_input = wait.until(EC.presence_of_element_located((By.ID, "pass")))
        pass_input.clear()
        pass_input.send_keys(password)

        try_find_and_click(driver, "button[name='login']")

        try:
            WebDriverWait(driver, 20).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[aria-label='Trang chủ']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Account']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='navigation']")),
                )
            )
            print("✅ Có vẻ đã đăng nhập thành công.")
            return True
        except Exception:
            print("⚠ Không chắc đã đăng nhập — có thể bị checkpoint.")
            return False
    except Exception as e:
        print("❌ Lỗi đăng nhập:", e)
        return False


def collect_graphql_responses(driver, scroll_times=30, sleep_between=1.5):
    print("📡 Bắt đầu thu thập GraphQL...")
    seen, responses = set(), []


    for i in range(scroll_times):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(sleep_between)


        try:
            logs = driver.get_log("performance")
        except Exception:
            logs = []


        for entry in logs:
            try:
                msg = json.loads(entry["message"])["message"]
                if msg.get("method") != "Network.responseReceived":
                    continue


                params = msg.get("params", {})
                response = params.get("response", {})
                url = response.get("url", "")
                req_id = params.get("requestId")


                if "graphql" not in url.lower() or not req_id or req_id in seen:
                    continue
                seen.add(req_id)


                try:
                    body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": req_id}).get("body", "")
                except Exception:
                    body = ""


                responses.append({"body": body})
            except Exception:
                continue


        print(f"⤵ Scroll {i+1}/{scroll_times} — Tổng: {len(responses)} GraphQL responses")


    return responses


def parse_multiple_jsons(s):
    decoder = json.JSONDecoder()
    idx, results = 0, []
    while idx < len(s):
        s = s.lstrip()
        try:
            obj, end = decoder.raw_decode(s)
            results.append(obj)
            s = s[end:]
        except json.JSONDecodeError:
            break
    return results


def parse_graphql_responses(graphql_data):
    rows = []
    for item in graphql_data:
        body = item.get("body")
        if not body:
            continue


        for js in parse_multiple_jsons(body):
            try:
                node = js["data"]["node"]

                actors = node.get("actors", [])
                if actors:
                    name = actors[0].get("name", "")
                    url = actors[0].get("url", "")
                    poster = f"{name} - {url}" if name or url else None
                else:
                    poster = None

                msg = (
                    node.get("comet_sections", {})
                    .get("content", {})
                    .get("story", {})
                    .get("message", {})
                )
                msg_text = msg.get("text") if isinstance(msg, dict) else None
                permalink = node.get("permalink_url", None)


                rows.append({
                    "poster": poster,
                    "message": msg_text,
                    "permalink": permalink
                })
            except Exception:
                continue
    return rows



def save_fb_results_to_csv(rows, filename="facebook_posts.csv"):
    if not rows:
        print("⚠ Không có dữ liệu để lưu.")
        return
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"💾 Đã lưu {len(rows)} bài viết vào {filename}")



def page_facebook(group_url, driver, scroll_times=20):
    wait = WebDriverWait(driver, 20)
    if not login_facebook(driver,wait):
        print("🚫 Không thể đăng nhập — dừng crawl.")
        return []


    driver.get(group_url)
    time.sleep(5)


    graphql_data = collect_graphql_responses(driver, scroll_times)
    rows = parse_graphql_responses(graphql_data)


    print(f"✅ Trích xuất được {len(rows)} bài viết hợp lệ.")
    return rows

