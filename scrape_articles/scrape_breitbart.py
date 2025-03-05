import requests
from bs4 import BeautifulSoup

# try a Breitbart article 
url = "https://www.breitbart.com/politics/2013/08/13/hyperloop-could-travel-from-la-to-san-francisco-in-30-minutes/"

response = requests.get(url)
if response.status_code == 200:
    html_content = response.text
    # parse this html_content with BeautifulSoup
else:
    print("Error fetching page")

soup = BeautifulSoup(html_content, "html.parser")

# Extract the title:
title = soup.find("h1")
if title:
    article_title = title.get_text(strip=True)

# Extract the article body:
body_div = soup.find("div", class_="entry-content")
if body_div:
    article_body = body_div.get_text(strip=True)
