import os
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
from selenium.common.exceptions import NoSuchElementException



options = Options()

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.maximize_window()

driver.get("https://www.amazon.in")
driver.delete_all_cookies()

search = driver.find_element(By.XPATH, "//input[@id = 'twotabsearchtextbox']")
search.clear()
search.send_keys("Dell Laptops")

search_button = driver.find_element(By.XPATH, "//input[@id = 'nav-search-submit-button']")
search_button.click()

time.sleep(3)

text = driver.find_element(By.XPATH, "//span[text() = 'Dell']")
text.click()

laptop_name = []
laptop_price = []
laptop_reviews = []

def extract_data_from_page():
    all_laptops = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")

    for laptop in all_laptops:

        names = laptop.find_elements(By.XPATH, ".//span[@class = 'a-size-medium a-color-base a-text-normal']")
        for name in names:
            laptop_name.append(name.text)

        prices = laptop.find_elements(By.XPATH, ".//span[@class = 'a-price-whole']")
        for price in prices:
            laptop_price.append(price.text)

        try:
            if len(laptop.find_elements(By.XPATH, ".//span[@class = 'a-size-base s-underline-text']"))>0:
                reviews = laptop.find_elements(By.XPATH, ".//span[@class = 'a-size-base s-underline-text']")
                for review in reviews:
                    laptop_reviews.append(review.text)
            else:
                laptop_reviews.append("0")
        except:
            pass
extract_data_from_page()

page_counter = 1

# Loop to handle pagination, limiting to 3 pages
while page_counter < 3:  # Limit to first 3 pages
    try:
        # Find and click the 'Next' button to go to the next page
        next_button = driver.find_element(By.XPATH, "//a[contains(@class,'s-pagination-next')]")
        
        # Check if the 'Next' button is enabled
        if 'disabled' not in next_button.get_attribute("class"):
            next_button.click()
            time.sleep(3)  # Wait for the next page to load
            extract_data_from_page()  # Extract data from the next page
            page_counter += 1  # Increment the page counter
        else:
            break  # If 'Next' button is disabled, exit the loop
    except NoSuchElementException:
        break

print("Name", len(laptop_name))
print("Price", len(laptop_price))
print("Review", len(laptop_reviews))

data = {
    'Laptop Name': laptop_name,
    'Price': laptop_price,
    'Reviews': laptop_reviews
}

df = pd.DataFrame(data)

# Save DataFrame to CSV file
df.to_csv('amazon_dell_laptops.csv', index=False)

print("Data has been saved to 'amazon_dell_laptops.csv'.")