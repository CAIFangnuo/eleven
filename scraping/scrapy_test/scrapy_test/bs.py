import requests
from bs4 import BeautifulSoup

r = requests.get(
    'https://www.airlinequality.com/airline-reviews/africa-world-airlines')


# Text
soup = BeautifulSoup(r.content, 'lxml')
reviews = soup.find_all("div", class_="text_content")

#for review in reviews:
    #print(review.text)
    #print("\n")

# Country of Origin and Date
author = soup.find_all("h3", class_=["text_sub_header", "userStatusWrapper"])

for i, auth in enumerate(author):
    # Review Counter
    counter = auth.find("span", class_="userStatusReviewCount")

    #Name
    name = auth.find("span", itemprop="name").text

    # Date
    date = auth.find("time", itemprop="datePublished").text
    
    # Country
    if counter:
        country = auth.text.replace(counter.text, "")
        country = country.replace(date, "")
        country = country.replace(name + " ", "")
    else:
        country = auth.text.replace(date, "")
        country = country.replace(name + " ", "")
    print(country)
    #print(name)
    #print(date)
    #print(country)

