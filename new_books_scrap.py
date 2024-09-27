import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

# Initialize the WebDriver
options = Options()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.maximize_window()
driver.get('https://books.toscrape.com/')

# Lists to store the book data
book_titles = []
book_upcs = []
book_product_types = []
book_prices_excl_tax = []
book_prices_incl_tax = []
book_taxes = []
book_availability = []
book_reviews = []

# Loop through all pages until no "Next" button is found
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

        # Append the book data to the respective lists
        book_titles.append(title)
        book_upcs.append(data.get('UPC', "N/A"))
        book_product_types.append(data.get('Product Type', "N/A"))
        book_prices_excl_tax.append(data.get('Price (excl. tax)', "N/A"))
        book_prices_incl_tax.append(data.get('Price (incl. tax)', "N/A"))
        book_taxes.append(data.get('Tax', "N/A"))
        book_availability.append(data.get('Availability', "N/A"))
        book_reviews.append(data.get('Number of reviews', "N/A"))

        # Go back to the list of books
        driver.back()
        time.sleep(1)  # To avoid overwhelming the server, wait 1 second between requests

    # Check if there is a "Next" button and go to the next page using XPath
    try:
        next_button = driver.find_element(By.XPATH, '//li[@class="next"]/a')
        next_button.click()
        time.sleep(2)  # Wait for the next page to load
    except NoSuchElementException:
        print("No more pages to scrape.")
        break

# Close the WebDriver
driver.quit()

# Create a DataFrame from the lists
data = {
    'Title': book_titles,
    'UPC': book_upcs,
    'Product Type': book_product_types,
    'Price (excl. tax)': book_prices_excl_tax,
    'Price (incl. tax)': book_prices_incl_tax,
    'Tax': book_taxes,
    'Availability': book_availability,
    'Number of Reviews': book_reviews
}

books_df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
books_df.to_csv('all_books_data.csv', index=False)

print("Data has been successfully scraped and saved to all_books_data.csv")
