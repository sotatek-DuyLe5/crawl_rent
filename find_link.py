import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def find_links(driver, query: str, wait_time=15, csv_file="links.csv"):
    """
    Tìm kiếm Google và trả về list các href + lưu vào file CSV.
    """

    driver.get("https://www.google.com")

    # Nhập từ khóa tìm kiếm
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    # Đợi phần kết quả xuất hiện
    try:
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#search"))
        )
    except Exception:
        print("⚠️ Không tìm thấy phần kết quả.")
        driver.quit()
        return []

    # Lấy tất cả tiêu đề kết quả
    elements = driver.find_elements(By.CLASS_NAME, "DKV0Md")

    hrefs = []
    for el in elements:
        try:
            parent = el.find_element(By.XPATH, "./ancestor::a")
            href = parent.get_attribute("href")
            if href and href not in hrefs:
                hrefs.append(href)
        except:
            continue

    # Lưu kết quả ra CSV
    if hrefs:
        with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Link"])
            for link in hrefs:
                writer.writerow([link])
        print(f"✅ Đã lưu {len(hrefs)} link vào file: {csv_file}")
    else:
        print("⚠️ Không tìm thấy link nào.")

    return hrefs
