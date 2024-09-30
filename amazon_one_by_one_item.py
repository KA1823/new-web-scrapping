from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# Set up Chrome options and initialize WebDriver
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Open the main page
driver.get("https://www.amazon.in")

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

# Store scraped data
laptop_name = []
laptop_price = []
laptop_ratings = []

# Define how many pages to scrape (2 in this case)
total_pages = 2
current_page = 1

while current_page <= total_pages:
    print(f"Scraping page {current_page}...")

    # Scrape links to product details on the current page
    products = driver.find_elements(By.XPATH, "//a[@class='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal']")

    # Iterate over products
    for index, product in enumerate(products):
        main_window = driver.current_window_handle  # Store the main window handle

        product_link = product.get_attribute("href")  # Get the product link
        driver.execute_script("window.open(arguments[0]);", product_link)  # Open link in new tab

        time.sleep(5)

        # Switch to new tab
        driver.switch_to.window(driver.window_handles[1])

        # Scrape the title
        try:
            title = driver.find_element(By.ID, "productTitle").text
        except:
            title = "Title not found"

        # Scrape the price
        try:
            price = driver.find_element(By.XPATH, "//span[contains(@class, 'priceToPay')]").text
        except:
            price = "Price not found"

        # Scrape the ratings
        try:
            ratings = driver.find_element(By.XPATH, "(//a[contains(@class, 'a-popover-trigger a-declarative')]//span[contains(@class, 'a-size-base a-color-base')])[1]").text
        except:
            ratings = "No ratings"

        # Append data to the list
        laptop_name.append(title)
        laptop_price.append(price)
        laptop_ratings.append(ratings)

        # print(f"Title: {title}")
        # print(f"Price: {price}")
        # print(f"Ratings: {ratings}")
        # print("-------------------------")

        # Close the current tab
        driver.close()

        # Switch back to the main window
        driver.switch_to.window(main_window)

        # Wait for the main page to load before interacting again
        time.sleep(3)

    # Check if there is a "Next" button and move to the next page
    try:
        next_button = driver.find_element(By.XPATH, "//a[contains(@class,'s-pagination-next')]")
        next_button.click()
        current_page += 1
        time.sleep(5)  # Wait for the next page to load
    except:
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
