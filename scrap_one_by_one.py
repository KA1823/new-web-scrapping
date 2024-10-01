import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up Chrome options and initialize WebDriver
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Open the main page
driver.get("https://www.daraz.pk/#?")  # Replace with the actual page URL

driver.find_element(By.XPATH, "//input[@class = 'search-box__input--O34g']").send_keys("Laptop")
driver.find_element(By.XPATH, "//a[@class = 'search-box__button--1oH7']").click()

# List to store the scraped data
items_data = []

# Get the initial product elements
products = driver.find_elements(By.CLASS_NAME, "RfADt")

# Iterate over the product elements by index
for index in range(len(products)):
    # Refetch the product elements to avoid stale element reference
    products = driver.find_elements(By.CLASS_NAME, "RfADt")

    # Click on each product link
    product_link = products[index].find_element(By.TAG_NAME, "a")
    driver.execute_script("arguments[0].click();", product_link)
    # product_link.click()

    # Allow time for the product page to load
    time.sleep(3)

    # Scrape the details
    try:
        title = driver.find_element(By.CLASS_NAME, "pdp-mod-product-badge-title").text
    except:
        title = "Title not found"

    try:
        price = driver.find_element(By.CLASS_NAME, "pdp-price").text
    except:
        price = "Price not found"
    
    try:
        ratings = driver.find_element(By.CLASS_NAME, "pdp-review-summary__link").text
    except:
        ratings = "No ratings"

    # Store the scraped data in a dictionary
    item_details = {
        "title": title,
        "price": price,
        "ratings": ratings
    }
    
    # Append the data to the list
    items_data.append(item_details)
    
    # Print or process the item details
    print(item_details)

    # Go back to the main page
    driver.back()

    # Wait for the main page to load before interacting again
    time.sleep(3)

# Close the browser after scraping
driver.quit()

# Convert the list of dictionaries to a pandas DataFrame
df = pd.DataFrame(items_data)

# Save DataFrame to CSV file
df.to_csv('daraz_laptops.csv', index=False)

print("Data has been saved to 'daraz_laptops.csv'.")

# Print final collected data
for item in items_data:
    print(item)




