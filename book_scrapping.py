import time
import pandas as pd
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

while True:  # Loop indefinitely until there's no next button
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
        books_data.append({
            'Title': title,
            'UPC': data.get('UPC'),
            'Product Type': data.get('Product Type'),
            'Price (excl. tax)': data.get('Price (excl. tax)'),
            'Price (incl. tax)': data.get('Price (incl. tax)'),
            'Tax': data.get('Tax'),
            'Availability': data.get('Availability'),
            'Number of Reviews': data.get('Number of reviews')
        })

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

# Convert the data to a pandas DataFrame
books_df = pd.DataFrame(books_data)

# Save the DataFrame to a CSV file
books_df.to_csv('all_books_data.csv', index=False)

print("Data has been successfully scraped and saved to all_books_data.csv")
