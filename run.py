from find_link import find_links
from batdongsan import page_bds
from urllib.parse import urlparse
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

from facebook import page_facebook, save_fb_results_to_csv

CHROMEDRIVER_PATH = "chromedriver"  # sửa đường dẫn nếu cần
HEADLESS = False                     # True nếu muốn chạy headless
PAGE_LOAD_TIMEOUT = 30
IMPLICIT_WAIT = 5
options = Options()
options.add_argument("--incognito")
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)


stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
)

def main():
    query = input("Nhập nội dung bạn muốn tìm: ")
    links = find_links(driver, query)

    print(f"🔗 Tìm thấy {len(links)} link")

    for link in links:
        domain = urlparse(link).netloc
        if "batdongsan.com.vn" in domain:
            # print(f"🏠 Đang crawl Batdongsan: {link}")
            # page_bds(link,driver)
            pass

        elif "facebook.com" in domain or "fb.me" in domain:
            print(f"📘 Đang crawl Facebook: {link}")
            # open link and extract elements with aria-posinset
            fb_csv = page_facebook(link, driver, scroll_times=30)
            save_fb_results_to_csv(fb_csv)
    
if __name__ == "__main__":
    main()


