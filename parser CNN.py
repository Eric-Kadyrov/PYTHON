import requests
from bs4 import BeautifulSoup

# URL of the website you want to scrape
url = 'https://edition.cnn.com/politics'

# Fetch the content from the URL
response = requests.get(url)

# Parse the content with Beautiful Soup
soup = BeautifulSoup(response.text, 'html.parser')

# Assuming headlines are stored in <h3> tags or you can adjust the tag or class based on the website's structure
headlines = soup.find_all('h2')

# Print each headline
for headline in headlines:
    print(headline.text.strip())