from find_link import find_links
from batdongsan import page_bds
from urllib.parse import urlparse
from driver_factory import create_driver
from facebook import page_facebook, save_fb_results_to_csv


def main():
    # Tạo driver chung (cho website)
    driver = create_driver(headless= False, for_facebook=True)

    query = input("Nhập nội dung bạn muốn tìm: ")
    links = find_links(driver, query)
    print(f"🔗 Tìm thấy {len(links)} link")
    all_fb_posts =[]
    try:
        for link in links:
            domain = urlparse(link).netloc.lower()
            if "facebook.com" in domain or "fb.me" in domain:
                print(f"📘 Đang crawl Facebook: {link}")
                fb_posts = page_facebook(link, driver, scroll_times=30)
                all_fb_posts.extend(fb_posts)   
                save_fb_results_to_csv(all_fb_posts)
            elif "batdongsan.com.vn" in domain:
                print(f"🏠 Đang crawl Batdongsan: {link}")
                page_bds(link, driver)
                pass
    finally:
        driver.quit()


if __name__ == "__main__":
    main()


