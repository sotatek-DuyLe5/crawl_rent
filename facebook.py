import time
import csv
import os
import base64
import json
# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException


def login():
    
    return 

def extract_from_aria_posinset_element(el):
    """
    Nhận một WebElement có attribute aria-posinset và trích xuất toàn bộ raw_text.
    Trả về dict gồm: posinset, raw_text
    """
    try:
        pos = el.get_attribute("aria-posinset")
    except StaleElementReferenceException:
        return None

    try:
        raw_text = el.text or ""
    except Exception:
        raw_text = ""

    if not raw_text.strip():
        return None

    return {
        "aria-posinset": pos,
        "raw_text": raw_text,
    }


def get_response_body(driver, request_id):
    """Dùng CDP để lấy nội dung response của một request"""
    try:
        body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
        content = body.get("body", "")
        if body.get("base64Encoded"):
            content = base64.b64decode(content).decode("utf-8", errors="ignore")
        return content
    except Exception as e:
        return f"[error] {e}"

def get_response_body(driver, request_id):
    """Dùng CDP để lấy nội dung response của một request"""
    try:
        body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
        content = body.get("body", "")
        if body.get("base64Encoded"):
            content = base64.b64decode(content).decode("utf-8", errors="ignore")
        return content
    except Exception as e:
        return f"[error] {e}"


def page_facebook(link, driver, max_wait=10, scroll_times=3):
    """
    Mở link Facebook và:
    - Cào toàn bộ element có aria-posinset (text bài viết)
    - Ghi nhận toàn bộ request GraphQL qua CDP
    Trả về (results, graphql_data)
    """
    results = []
    graphql_data = {}

    try:
        print(f"[FB] Mở: {link}")
        driver.execute_cdp_cmd("Network.enable", {})  # bật network logging
        driver.get(link)

        # chờ trang load
        WebDriverWait(driver, max_wait).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)

        # cuộn để tải thêm nội dung
        for i in range(scroll_times):
            driver.execute_script("window.scrollBy(0, window.innerHeight * 0.9);")
            time.sleep(1.5)

        # === Lấy log performance (bao gồm network events) ===
        logs = driver.get_log("performance")

        for entry in logs:
            try:
                msg = json.loads(entry["message"])["message"]
                method = msg.get("method")
                params = msg.get("params", {})

                # Request GraphQL gửi đi
                if method == "Network.requestWillBeSent":
                    request = params.get("request", {})
                    req_id = params.get("requestId")
                    url = request.get("url", "")
                    if "graphql" in url:
                        graphql_data[req_id] = {
                            "url": url,
                            "postData": request.get("postData", ""),
                            "response_body": None,
                        }

                # Response GraphQL trả về
                elif method == "Network.responseReceived":
                    response = params.get("response", {})
                    url = response.get("url", "")
                    if "graphql" in url:
                        req_id = params.get("requestId")
                        body = get_response_body(driver, req_id)
                        if req_id in graphql_data:
                            graphql_data[req_id]["response_body"] = body
            except Exception:
                continue

        # === Lấy text thô từ bài viết ===
        elements = driver.find_elements(By.CSS_SELECTOR, "[aria-posinset]")
        for el in elements:
            data = extract_from_aria_posinset_element(el)
            if data:
                results.append(data)

        print(f"[+] Thu được {len(results)} bài viết/comment.")
        print(f"[+] Bắt được {len(graphql_data)} request GraphQL.")

    except Exception as e:
        print(f"[!] Lỗi khi xử lý link {link}: {e}")

    # Chuyển graphql_data thành list cho dễ dùng
    graphql_list = list(graphql_data.values())
    return results, graphql_list


def save_fb_results_to_csv(results, filename="facebook_rawtext.csv"):
    """Lưu kết quả văn bản (aria-posinset) vào CSV"""
    headers = ["aria-posinset", "raw_text"]
    count = 0
    with open(filename, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        for r in results:
            if isinstance(r, dict):  # chỉ ghi nếu r là dict
                writer.writerow({h: r.get(h, "") for h in headers})
                count += 1
            elif isinstance(r, list):  # nếu r là list, thì ghi từng phần tử trong đó
                for item in r:
                    if isinstance(item, dict):
                        writer.writerow({h: item.get(h, "") for h in headers})
                        count += 1

    print(f"[+] Lưu {count} hàng vào {filename}")


def save_graphql_to_json(graphql_data, filename="facebook_graphql.json"):
    """Lưu các request GraphQL vào JSON"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(graphql_data, f, ensure_ascii=False, indent=2)
    print(f"[+] Lưu {len(graphql_data)} request GraphQL vào {filename}")
















# def extract_from_aria_posinset_element(el):
#     """
#     Nhận một WebElement có attribute aria-posinset và trích xuất toàn bộ raw_text.
#     Trả về dict gồm: posinset, raw_text
#     """
#     try:
#         pos = el.get_attribute("aria-posinset")
#     except StaleElementReferenceException:
#         return None

#     try:
#         raw_text = el.text or ""
#     except Exception:
#         raw_text = ""

#     if not raw_text.strip():
#         return None

#     return {
#         "aria-posinset": pos,
#         "raw_text": raw_text,
#     }


# def page_facebook(link, driver, max_wait=10, scroll_times=3):
#     """
#     Mở link Facebook và thu các element có attribute aria-posinset.
#     """
#     results = []

#     try:
#         print(f"[FB] Mở: {link}")
#         driver.get(link)

#         # Chờ body xuất hiện
#         WebDriverWait(driver, max_wait).until(
#             EC.presence_of_element_located((By.TAG_NAME, "body"))
#         )
#         time.sleep(2)

#         # Cuộn để tải nội dung thêm
#         for i in range(scroll_times):
#             driver.execute_script("window.scrollBy(0, window.innerHeight * 0.8);")
#             time.sleep(1.2)

#         # Lấy phần tử có aria-posinset
#         elements = driver.find_elements(By.CSS_SELECTOR, "[aria-posinset]")
#         for el in elements:
#             data = extract_from_aria_posinset_element(el)
#             if data:
#                 results.append(data)

#         print(f"[+] Thu được {len(results)} phần tử từ {link}")

#     except Exception as e:
#         print(f"[!] Lỗi khi xử lý link {link}: {e}")

#     return results, []

        ## tìm tất cả phần tử có attribute aria-posinset
    #     try:
    #         nodes = driver.find_elements(By.CSS_SELECTOR, "[aria-posinset]")
    #     except Exception:
    #         nodes = []

    #     print(f"[FB] Tìm thấy {len(nodes)} phần tử có aria-posinset")

    #     # duyệt từng node, extract
    #     for n in nodes:
    #         info = extract_from_aria_posinset_element(n)
    #         if info:
    #             results.append(info)

    #     # nếu muốn, ta có thể dedupe theo aria-posinset
    #     seen = set()
    #     uniq_results = []
    #     for r in results:
    #         key = (r.get("aria-posinset"), r.get("raw_text")[:80])

    #         if key in seen:
    #             continue
    #         seen.add(key)
    #         uniq_results.append(r)

    #     return uniq_results

    # finally:
    #     if created_driver:
    #         # giữ driver mở 2s để bạn nhìn kết quả nếu không headless, rồi đóng
    #         time.sleep(2)
    #         try:
    #             driver.quit()
    #         except Exception:
    #             pass


    







# def save_fb_results_to_csv(results, filename="facebook_rawtext.csv"):
#     headers = ["aria-posinset", "raw_text"]
#     count = 0
#     with open(filename, "w", encoding="utf-8-sig", newline="") as f:
#         writer = csv.DictWriter(f, fieldnames=headers)
#         writer.writeheader()

#         for r in results:
#             if isinstance(r, dict):  # chỉ ghi nếu r là dict
#                 writer.writerow({h: r.get(h, "") for h in headers})
#                 count += 1
#             elif isinstance(r, list):  # nếu r là list, thì ghi từng phần tử trong đó
#                 for item in r:
#                     if isinstance(item, dict):
#                         writer.writerow({h: item.get(h, "") for h in headers})
#                         count += 1

#     print(f"[+] Lưu {count} hàng vào {filename}")
