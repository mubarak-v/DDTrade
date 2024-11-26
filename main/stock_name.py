import yfinance as yf
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import yfinance as yf
from .models import Stock

def save_stock_data_to_db(driver):
    saved_data = []  # List to store successfully saved stock names
    unsaved_data = []  # List to store stock names that failed to save

    try:
        # Wait for the initial elements to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.jsx-427622308.screener-cell.ellipsis"))
        )

        while True:
            # Locate and print current data
            parent_elements = driver.find_elements(By.CSS_SELECTOR, "span.jsx-427622308.screener-cell.ellipsis")
            for parent in parent_elements:
                try:
                    # Extract company name and stock ticker
                    try:
                        desktop_view = parent.find_element(By.CSS_SELECTOR, "span.jsx-427622308.desktop--only.pointer").text
                    except Exception:
                        desktop_view = None  # Handle cases where desktop_view is not found

                    try:
                        mobile_view = parent.find_element(By.CSS_SELECTOR, "span.jsx-427622308.stock-name.mob--only").text
                    except Exception:
                        mobile_view = None  # Handle cases where mobile_view is not found

                    # Ensure mobile_view is valid
                    if not mobile_view:
                        print("Invalid mobile_view; skipping this element.")
                        unsaved_data.append(desktop_view or "Unknown Stock")
                        continue

                    # Add '.NS' for Indian stock tickers if not already present
                    if not mobile_view.endswith('.NS'):
                        ticker_symbol = mobile_view + '.NS'
                    else:
                        ticker_symbol = mobile_view

                    # Fetch stock information using yfinance
                    stock = yf.Ticker(ticker_symbol)
                    stock_info = stock.info

                    # Extract Yahoo Finance data
                    yahoo_name = stock_info.get('longName', 'N/A')
                    yahoo_symbol = stock_info.get('symbol', 'N/A')

                    if yahoo_name == 'N/A' or yahoo_symbol == 'N/A':
                        print(f"Could not fetch valid data for ticker: {ticker_symbol}")
                        unsaved_data.append(mobile_view)
                        continue

                    print(f"Yahoo Finance Name: {yahoo_name}")
                    print(f"Yahoo Finance Symbol: {yahoo_symbol}")
                    print("-" * 40)

                    # Save the stock data to the database
                    if not Stock.objects.filter(yfinance_name=yahoo_symbol).exists():
                        stock_obj = Stock(name=yahoo_name, yfinance_name=yahoo_symbol)
                        stock_obj.save()
                        saved_data.append(yahoo_name)
                        print(f"Stock '{mobile_view}' saved to the database!")
                    else:
                        unsaved_data.append(yahoo_name)
                        print(f"Stock '{mobile_view}' already exists in the database!")

                except Exception as e:
                    unsaved_data.append(mobile_view or "Unknown")
                    print(f"Error processing element: {e}")

            # Scroll and handle "Load More" button
            try:
                scrollable_container = driver.find_element(By.CSS_SELECTOR, ".table-container.jsx-3695020")
                driver.execute_script("arguments[0].scrollBy(0, 900);", scrollable_container)
                time.sleep(2)  # Pause to allow dynamic content to load

                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Load More']"))
                )
                load_more_button.click()
                time.sleep(2)
            except Exception:
                print("No more 'Load More' button found or clickable.")
                break

    except Exception as e:
        print(f"Error in saving stock data: {e}")

    finally:
        # Print results
        print("\nSaved Data:")
        print(saved_data)
        print("\nUnsaved Data:")
        print(unsaved_data)
        return saved_data, unsaved_data
