from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from main.stock_name import save_stock_data_to_db

class Command(BaseCommand):
    help = "Fetch and save stock data to the database"

    def handle(self, *args, **kwargs):
        # Configure ChromeOptions for headless mode with custom screen size
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Enable headless mode
        chrome_options.add_argument("--disable-gpu")  # Disable GPU rendering
        chrome_options.add_argument("--window-size=375,812")  # Set screen size (mobile viewport)
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security restrictions
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome shared memory issues
        chrome_options.add_argument("--disable-extensions")  # Disable browser extensions
        chrome_options.add_argument("--log-level=3")  # Suppress unnecessary logs
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Suppress logs
        chrome_options.add_experimental_option("useAutomationExtension", False)

        # Initialize the Chrome driver with headless configuration
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        # Open the desired URL and fetch stock data
        driver.get("https://www.tickertape.in/screener/equity")
        try:
            save_stock_data_to_db(driver)
            self.stdout.write(self.style.SUCCESS("Stock data saved successfully!"))
        finally:
            driver.quit()