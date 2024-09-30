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
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Navigate to Amazon India
driver.get("https://www.amazon.in")
time.sleep(3)

# Search for Dell Laptops
search = driver.find_element(By.XPATH, "//input[@id='twotabsearchtextbox']")
search.clear()
search.send_keys("Dell Laptops")

search_button = driver.find_element(By.XPATH, "//input[@id='nav-search-submit-button']")
search_button.click()

time.sleep(3)

# Filter to show only Dell brand products
text = driver.find_element(By.XPATH, "//span[text() = 'Dell']")
text.click()

# Initialize lists to store the scraped data
laptop_name = []
laptop_price = []
laptop_ratings = []

# Function to extract data from a single page
def extract_data_from_page():
    products = driver.find_elements(By.XPATH, "//a[@class='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal']")
    
    for product in products:
        try:
            product_link = product.get_attribute("href")  # Get the product link
            driver.execute_script("window.open(arguments[0]);", product_link)  # Open link in new tab
            time.sleep(3)
            
            # Switch to new tab
            driver.switch_to.window(driver.window_handles[1])
            
            # Scrape the title
            try:
                title = driver.find_element(By.ID, "productTitle").text
                laptop_name.append(title)
            except NoSuchElementException:
                laptop_name.append("N/A")
            
            # Scrape the price
            try:
                price = driver.find_element(By.XPATH, "//span[contains(@class, 'priceToPay')]").text
                numeric_price = re.sub(r'[^\d,]', '', price)  # Keep only digits
                laptop_price.append(numeric_price)
            except NoSuchElementException:
                laptop_price.append("N/A")
            
            # Scrape the ratings
            try:
                ratings = driver.find_element(By.XPATH, "(//a[contains(@class, 'a-popover-trigger a-declarative')]//span[contains(@class, 'a-size-base a-color-base')])[1]").text
                laptop_ratings.append(ratings)
            except NoSuchElementException:
                laptop_ratings.append("N/A")


            print(f"Title: {title}")
            print(f"Price: {price}")
            print(f"Ratings: {ratings}")
            print("-------------------------")
            # Close the tab
            driver.close()
            # Switch back to the main window
            driver.switch_to.window(driver.window_handles[0])

        except NoSuchElementException:
            continue

# Handle pagination, limit to scraping 2 pages
page_counter = 1
total_pages = 2

while page_counter <= total_pages:
    print(f"Scraping page {page_counter}...")
    extract_data_from_page()  # Extract data from the current page
    
    # Find and click the 'Next' button to go to the next page
    try:
        next_button = driver.find_element(By.XPATH, "//a[contains(@class,'s-pagination-next')]")
        next_button.click()
        time.sleep(5)  # Wait for the next page to load
        page_counter += 1
    except NoSuchElementException:
        print("No more pages to scrape.")
        break

# Close the browser after scraping
driver.quit()

# Create a DataFrame and save data to a CSV file
data = {
    'Laptop Name': laptop_name,
    'Price': laptop_price,
    'Ratings': laptop_ratings
}

df = pd.DataFrame(data)
df.to_csv('dell_laptops.csv', index=False)

print("Data has been saved to 'dell_laptops.csv'.")



