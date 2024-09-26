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
driver.get("https://www.daraz.pk/#?")
time.sleep(3)

search = driver.find_element(By.XPATH, "//input[@class = 'search-box__input--O34g']")
search.send_keys("Laptop")

search_btn = driver.find_element(By.XPATH, "//a[@class = 'search-box__button--1oH7']")
search_btn.click()

time.sleep(5)

laptop_name = []
laptop_price = []
laptop_sold = [] 



def extract_data_from_page():
    all_laptops = driver.find_elements(By.XPATH, "//div[@class = 'Bm3ON']")
    print(len(all_laptops))

    for laptop in all_laptops:
        try:
            name = laptop.find_element(By.XPATH, ".//div[@class = 'RfADt']").text
            # print("laptop Name:", name)
            laptop_name.append(name)
        except NoSuchElementException:
                laptop_name.append("N/A")

        try:
            price = laptop.find_element(By.XPATH, ".//span[@class = 'ooOxS']").text
            # print("laptop price:", price)
            # laptop_price.append(price)
            numeric_price = re.sub(r'[^\d,]', '', price)  # Keep only digits and decimals
            laptop_price.append(numeric_price)
        except NoSuchElementException:
                laptop_price.append("N/A")

        try:
            total_sold = laptop.find_element(By.XPATH, ".//span[@class = '_1cEkb']").text
            # print("laptop price:", total_sold)
            laptop_sold.append(total_sold)
        except NoSuchElementException:
                laptop_sold.append("N/A")




extract_data_from_page()

page_counter = 1

# Loop to handle pagination, limiting to 3 pages
while page_counter < 3:  # Limit to first 3 pages
    try:
        # Find and click the 'Next' button to go to the next page
        next_button = driver.find_element(By.XPATH, "//span[@aria-label='right']")
        
        # Check if the 'Next' button is enabled
        if 'disabled' not in next_button.get_attribute("class"):
            driver.execute_script("arguments[0].click();", next_button)
            # next_button.click()
            time.sleep(4)  # Wait for the next page to load
            extract_data_from_page()  # Extract data from the next page
            page_counter += 1  # Increment the page counter
        else:
            break  # If 'Next' button is disabled, exit the loop
    except NoSuchElementException:
        break

print("Name", len(laptop_name))
print("Price", len(laptop_price))
print("Sold", len(laptop_sold))

data = {
    'Laptop Name': laptop_name,
    'Laptop Price': laptop_price,
    'Laptop Sold': laptop_sold
}

df = pd.DataFrame(data)

# Save DataFrame to CSV file
df.to_csv('daraz_laptops_list.csv', index=False)

print("Data has been saved to 'daraz_laptops_list.csv'.")