import os
import re
import time
import pandas as pd
import random
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException


# Random delay function
def random_delay():
    time.sleep(random.uniform(5, 10))

# Random mouse movement function
def random_mouse_movement():
    width, height = pyautogui.size()
    pyautogui.moveTo(random.randint(0, width), random.randint(0, height), duration=random.uniform(1, 3))

# Initialize Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Navigate to Amazon
driver.get("https://www.amazon.com/s?k=Dell+Laptop&rh=n%3A172282%2Cp_123%3A241862&dc&ds=v1%3AqzPBulz1AceDi2PT93%2BEQ5ZzlCgM85kX%2BKJ2%2Bz%2Bh2wc&qid=1727935866&rnid=85457740011&ref=sr_nr_p_123_1")
random_delay()

# Simulate human-like interaction
random_mouse_movement()

# Search for Dell Laptops
# search = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@id='twotabsearchtextbox']")))
# search.clear()
random_delay()  # Add delay between actions
# search.send_keys("Dell Laptops")

random_delay()
random_mouse_movement()

# search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='nav-search-submit-button']")))
# search_button.click()

random_delay()

# Filter to show only Dell brand products
# try:
#     dell_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'a-size-base a-color-base') and text()='Dell']")))
#     random_mouse_movement()
#     dell_element.click()
#     random_delay()
# except Exception as e:
#     print("Error clicking on Dell element:", e)

# Initialize lists to store the scraped data
laptop_name = []
laptop_price = []
laptop_ratings = []

# Scrape the price
def get_price():
    try:
        # First try the 'priceToPay' class
        price = driver.find_element(By.XPATH, "(//span[contains(@class, 'priceToPay')])[1]")
        
        # Get the currency symbol
        currency_symbol = price.find_element(By.XPATH, ".//span[contains(@class, 'a-price-symbol')]").text
        
        # Get the whole price part
        whole_price = price.find_element(By.XPATH, ".//span[contains(@class, 'a-price-whole')]").text
        
        # Combine currency symbol with whole price
        full_price = f"{currency_symbol}{whole_price}"
        
    except NoSuchElementException:
        # print("Price not found in 'priceToPay'. Trying 'a-offscreen'...")

        # Try to find the price in the 'a-offscreen' element (alternate price)
        try:
            # This XPath now focuses on finding the 'a-offscreen' span directly
            price_element = driver.find_element(By.XPATH, "(//span[contains(@class, 'apexPriceToPay')]//span[@aria-hidden='true'])[1]")
            
            # Get the text directly from the 'a-offscreen' element
            full_price = price_element.text.strip()  # Strip to remove any leading/trailing whitespace
            
            # Add a debug print to show the element's HTML
            # print(f"Price element HTML: {price_element.get_attribute('outerHTML')}")
            
            # print(f"Price found in 'a-offscreen': {full_price}")
        except NoSuchElementException:
            # print("Price not found in 'a-offscreen'.")
            full_price = "N/A"
    
    return full_price


# Call the get_price() function and print the result
full_price = get_price()
print(f"Final Price: {full_price}")





# Function to extract data from a single page
def extract_data_from_page():
    products = driver.find_elements(By.XPATH, "//a[@class='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal']")
    
    for product in products:
        try:
            product_link = product.get_attribute("href")
            random_mouse_movement()
            driver.execute_script("window.open(arguments[0]);", product_link)
            random_delay()
            
            # Switch to new tab
            driver.switch_to.window(driver.window_handles[1])
            
            # Simulate human-like interaction
            random_delay()
            random_mouse_movement()

            # Scrape the title
            try:
                title = driver.find_element(By.ID, "productTitle").text
                laptop_name.append(title)
            except NoSuchElementException:
                laptop_name.append("N/A")
            
            # Scrape the price using the new function
            full_price = get_price()
            laptop_price.append(full_price)
            
            # Scrape the ratings
            try:
                ratings = driver.find_element(By.XPATH, "(//a[contains(@class, 'a-popover-trigger a-declarative')]//span[contains(@class, 'a-size-base a-color-base')])[1]").text
                laptop_ratings.append(ratings)
            except NoSuchElementException:
                laptop_ratings.append("N/A")

            print(f"Title: {title}")
            print(f"Price: {full_price}")
            print(f"Ratings: {ratings}")
            print("-------------------------")
            
            # Close the tab
            driver.close()
            random_delay()
            
            # Switch back to the main window
            driver.switch_to.window(driver.window_handles[0])

        except NoSuchElementException:
            continue

# Handle pagination, limit to scraping 2 pages
page_counter = 1
total_pages = 2

while page_counter <= total_pages:
    print(f"Scraping page {page_counter}...")
    extract_data_from_page()
    
    # Simulate human-like interaction
    random_delay()
    random_mouse_movement()
    
    # Find and click the 'Next' button to go to the next page
    try:
        next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'s-pagination-next')]")))
        random_mouse_movement()
        next_button.click()
        time.sleep(5)
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
df.to_csv('amazon_official_dell_laptops.csv', index=False)

print("Data has been saved to 'amazon_official_dell_laptops.csv'.")
