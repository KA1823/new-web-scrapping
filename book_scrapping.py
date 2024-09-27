import csv
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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC


options = Options()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.maximize_window()

# Open the books to scrape website
driver.get('https://books.toscrape.com/')

# Prepare the CSV file to save the data
with open('books_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write the header row
    writer.writerow(['Title', 'UPC', 'Product Type', 'Price (excl. tax)', 'Price (incl. tax)', 'Tax', 'Availability', 'Number of Reviews'])

    # Loop through the pages of the website
    while True:
        # Get all book links on the current page
        book_links = driver.find_elements(By.CSS_SELECTOR, 'h3 > a')

        # Loop through each book link on the page
        for book_link in book_links:
            # Get the href attribute to click the link
            book_url = book_link.get_attribute('href')

            # Open the book page
            driver.get(book_url)

            try:
                # Wait for the title to load
                title_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'h1'))
                )
                title = title_element.text

                # Find the table and extract its data
                table_element = driver.find_element(By.CSS_SELECTOR, 'table.table-striped')
                table_rows = table_element.find_elements(By.TAG_NAME, 'tr')

                # Initialize a dictionary to hold the table data
                table_data = {}
                for row in table_rows:
                    columns = row.find_elements(By.TAG_NAME, 'th, td')
                    if len(columns) == 2:
                        table_data[columns[0].text] = columns[1].text

                # Write the data to the CSV file
                writer.writerow([
                    title,
                    table_data.get('UPC'),
                    table_data.get('Product Type'),
                    table_data.get('Price (excl. tax)'),
                    table_data.get('Price (incl. tax)'),
                    table_data.get('Tax'),
                    table_data.get('Availability'),
                    table_data.get('Number of reviews')
                ])

            except TimeoutException:
                print(f"Failed to load elements for {book_url}")

            # Go back to the book list page
            driver.back()

            # Wait for the page to load before continuing
            time.sleep(2)

        # Try to find and click the "next" button for pagination
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'li.next > a')
            next_button.click()
            time.sleep(2)  # Wait for the next page to load
        except:
            print("No more pages found. Scraping finished.")
            break

# Close the browser when done
driver.quit()
