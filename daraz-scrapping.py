import os
import re
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

# Initialize Chrome WebDriver
options = Options()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.maximize_window()

# Navigate to AliExpress
driver.get("https://best.aliexpress.com/")
time.sleep(3)

# Close any pop-up if it appears
try:
    driver.find_element(By.XPATH, "//div[contains(@class, ' _1-SOk')]").click()
except NoSuchElementException:
    pass  # If no pop-up, continue

# Perform search
search = driver.find_element(By.ID, 'search-words')
search.clear()
search.send_keys("Laptop")
search_button = driver.find_element(By.XPATH, "//input[@class='search--submit--2VTbd-T']")
search_button.click()

def scroll_until_items_loaded(min_items=60):
    """Scrolls the page until at least `min_items` are loaded."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    current_items_count = 0
    attempts = 0

    while attempts < 10:  # Max number of attempts to load more items
        driver.execute_script("window.scrollBy(0, 1200);")  # Scroll down
        time.sleep(5)  # Wait for items to load

        # Get the current number of items
        all_laptops = driver.find_elements(By.XPATH, "//div[contains(@class, 'multi--content--11nFIBL')]")
        current_items_count = len(all_laptops)

        # print(f"Current items count: {current_items_count}")  # Debug statement

        # Break if we have loaded enough items
        if current_items_count >= min_items:
            break

        # Check if new content was loaded
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("No new items loaded.")  # Debug statement
            attempts += 1  # Increment attempts if no new items are loaded
        else:
            attempts = 0  # Reset attempts if new items are loaded

        last_height = new_height

laptop_name = []
laptop_price = []
laptop_sold = []

def extract_data_from_page():
    """Extracts product data from the current page in order."""
    all_laptops = driver.find_elements(By.XPATH, "//div[contains(@class, 'multi--content--11nFIBL')]")
    # print(f"Found {len(all_laptops)} items")

    for laptop in all_laptops:
        try:
            name = laptop.find_element(By.XPATH, ".//div[@class='multi--title--G7dOCj3']").text
            laptop_name.append(name)  # Append directly to maintain order

            # Extract price
            try:
                price = laptop.find_element(By.XPATH, ".//div[contains(@class, 'multi--price-sale--U-S0jtj')]").text
                # laptop_price.append(price)
                numeric_price = re.sub(r'[^\d.]', '', price)  # Keep only digits and decimals
                laptop_price.append(numeric_price)
            except NoSuchElementException:
                laptop_price.append("N/A")

            # Extract total sold
            try:
                total_sold = laptop.find_element(By.XPATH, ".//span[contains(@class, 'multi--trade--Ktbl2jB')]").text
                laptop_sold.append(total_sold)
            except NoSuchElementException:
                laptop_sold.append("N/A")
        except NoSuchElementException:
            continue  # Skip if there's an issue with finding elements

# Scroll and extract data from the first page
scroll_until_items_loaded(min_items=60)
extract_data_from_page()

# Loop to handle pagination, limit to first 3 pages
page_counter = 1
while page_counter < 4:  # Limit to first 3 pages
    try:
        # Find and click the 'Next' button to go to the next page
        next_button = driver.find_element(By.XPATH, "//span[contains(@class, 'comet-icon comet-icon-arrowleftrtl32 ')]")
        if 'disabled' not in next_button.get_attribute("class"):
            next_button.click()
            time.sleep(5)  # Wait for the next page to load
            
            # Scroll until enough items are loaded on the new page
            scroll_until_items_loaded(min_items=60)
            extract_data_from_page()  # Extract data from the next page
            page_counter += 1  # Increment page counter
        else:
            print("Next button is disabled.")  # Debug statement
            break  # Stop if 'Next' button is disabled
    except NoSuchElementException:
        print("Next button not found or other issue occurred.")  # Debug statement
        break

# Verify extracted data lengths
print("Name", len(laptop_name))
print("Price", len(laptop_price))
print("Sold", len(laptop_sold))

# Save data to a CSV file
data = {
    'Laptop Name': laptop_name,
    'Price': laptop_price,
    'Laptop Sold': laptop_sold
}

df = pd.DataFrame(data)
df.to_csv('laptop_list.csv', index=False)
print("Data has been saved to 'laptop_list.csv'.")

# Close the driver
driver.quit()
