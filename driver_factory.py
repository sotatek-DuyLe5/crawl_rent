from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.webdriver import WebDriver

def create_driver(headless=False, for_facebook=False) -> WebDriver:
    options = Options()
    options.add_argument("--incognito")
    
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1200,800")
    if headless:
        options.add_argument("--headless=new")

    service = Service(ChromeDriverManager().install())

    if for_facebook:
        # Bật logging để thu thập GraphQL
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_cdp_cmd("Network.enable", {})
    else:
        driver = webdriver.Chrome(service=service, options=options)

    return driver
