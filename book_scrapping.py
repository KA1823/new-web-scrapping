import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Initialize the WebDriver
options = Options()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.maximize_window()
driver.get('https://books.toscrape.com/')

# Initialize an empty list to store the book data
books_data = []

# Loop through all pages
while True:  
    # Get all book links on the current page using XPath
    books = driver.find_elements(By.XPATH, '//h3/a')

    for book in books:
        # Open the book page using XPath to get the href attribute
        book_url = book.get_attribute('href')
        driver.get(book_url)

        # Get the book title using XPath
        title = driver.find_element(By.XPATH, '//h1').text

        # Get the table rows using XPath
        table = driver.find_elements(By.XPATH, '//table[@class="table table-striped"]//tr')
        data = {}
        for row in table:
            # Find the header and value for each row using XPath
            header = row.find_element(By.XPATH, './/th').text
            value = row.find_element(By.XPATH, './/td').text
            data[header] = value

        # Append the book data to the list
        books_data.append([
            title,
            data.get('UPC'),
            data.get('Product Type'),
            data.get('Price (excl. tax)'),
            data.get('Price (incl. tax)'),
            data.get('Tax'),
            data.get('Availability'),
            data.get('Number of reviews')
        ])

        # Go back to the list of books
        driver.back()
        time.sleep(1)  # To avoid overwhelming the server, wait 1 second between requests

    # Check if there is a "Next" button and go to the next page using XPath
    try:
        next_button = driver.find_element(By.XPATH, '//li[@class="next"]/a')
        next_button.click()
        time.sleep(2)  # Wait for the next page to load
    except:
        print("No more pages to scrape.")
        break

# Close the WebDriver
driver.quit()

# Save the data to a CSV file
with open('all_books_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write header for CSV file
    writer.writerow(['Title', 'UPC', 'Product Type', 'Price (excl. tax)', 'Price (incl. tax)', 'Tax', 'Availability', 'Number of Reviews'])
    
    # Write all the book data at once
    writer.writerows(books_data)

print("Data has been successfully scraped and saved to all_books_data.csv")
