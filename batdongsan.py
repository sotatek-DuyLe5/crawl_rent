import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth  
from webdriver_manager.chrome import ChromeDriverManager
import os
import re


def page_bds(link, driver):
    """
    Crawl dữ liệu phòng trọ từ batdongsan.com.vn.
    Mỗi link sẽ lưu ra 1 file CSV riêng.
    """

    wait = WebDriverWait(driver, 10)
    driver.get(link)

    # 🔹 Tạo tên file CSV riêng cho từng link
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', link.strip())[:80]  # tránh quá dài
    csv_path = f"batdongsan_{safe_name}.csv"

    # Nếu file đã tồn tại thì xóa để tạo mới cho link này
    if os.path.exists(csv_path):
        os.remove(csv_path)
        print(f"🧹 Đã xóa file cũ: {csv_path}")

    results = []
    page = 1

    while True:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#product-lists-web > div")))
        cards = driver.find_elements(By.CSS_SELECTOR, "#product-lists-web > div")

        for card in cards:
            title = card.find_element(By.CSS_SELECTOR, "h3").text if card.find_elements(By.CSS_SELECTOR, "h3") else ""
            price = card.find_element(By.CSS_SELECTOR, "span.re__card-config-price").text if card.find_elements(By.CSS_SELECTOR, "span.re__card-config-price") else ""
            address = card.find_element(By.CSS_SELECTOR, "div.re__card-location > span:nth-child(2)").text if card.find_elements(By.CSS_SELECTOR, "div.re__card-location > span:nth-child(2)") else ""
            detail_link = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href") if card.find_elements(By.CSS_SELECTOR, "a") else ""
            
            results.append({
                "page": page,
                "title": title,
                "price": price,
                "address": address,
                "link": detail_link
            })

        # 🔹 Ghi dữ liệu nối tiếp vào file CSV riêng của link này
        df = pd.DataFrame(results)
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"💾 Đã lưu {len(results)} dòng vào {csv_path}")

        # Next page
        try:
            pagination_buttons = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR,
                 "body > div.re__main > div > div.re__main-content > div.re__srp-paging.js__srp-paging > div > a.re__pagination-icon")
            ))

            next_btn = pagination_buttons[-1]
            icon = next_btn.find_element(By.TAG_NAME, "i")
            icon_class = icon.get_attribute("class")

            if "re__icon-chevron-right--sm" in icon_class:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(4)
                page += 1
                print(f"➡️ Đã chuyển sang trang {page}.")

            elif "re__icon-chevron-left--sm" in icon_class:
                print("✅ Đã đến trang cuối cùng, dừng lại.")
                break

            else:
                print(f"⚠️ Class icon không xác định: {icon_class}")
                break

        except Exception as e:
            print("❌ Lỗi khi xử lý phân trang:", e)
            break

    return df