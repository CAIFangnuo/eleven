import time
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import re
import itertools
import pandas as pd
import numpy as np
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions





r = requests.get(
    'https://www.airlinequality.com/review-pages/a-z-airline-reviews/')

soup = BeautifulSoup(r.content, 'lxml')
driver = webdriver.Chrome()
driver.maximize_window()
driver.implicitly_wait(10)
driver.delete_all_cookies()
driver.get("https://www.airlinequality.com/review-pages/a-z-airline-reviews/")
driver.find_element_by_xpath('//*[@id="catapultCookie"]').click()

rows = []

column_collection = soup.find_all("div", class_="a_z_col_group")

for i, col_collect in enumerate(column_collection, start=1):
    if i%2 == 0:
        i = 2
    else:
        i = 1
    columns = col_collect.find_all("ul", class_="items")    
    for j, column in enumerate(columns, start=1):
        items = column.find_all("li")
        # TODO: change back to items
        for k, country in enumerate(items, start=1):
            xpath = f'//*[@id="a2z-ldr-A"]/div[{i}]/ul[{j}]/li[{k}]/a'

            #wait = WebDriverWait(driver, 2)
            #element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

            if driver.find_element_by_xpath(xpath):
                elem = driver.find_element_by_xpath(xpath)
                driver.execute_script("arguments[0].click();", elem)
            else:
                driver.back()
                continue
            window_after = driver.window_handles[0]
            driver.switch_to.window(window_after)
            new_url = driver.current_url + "/?sortby=post_date%3ADesc&pagesize=-1"
            new_r = requests.get(new_url)
            new_soup = BeautifulSoup(new_r.content, 'lxml')
            ## AIRLINE ##
            title = new_soup.find("h1", itemprop="name")
            articles = new_soup.find_all("article", itemprop="review")
            #author = new_soup.find_all("h3", class_=["text_sub_header", "userStatusWrapper"])
            text_and_rev = new_soup.find_all("div", class_="tc_mobile")

            # if i == 2:
            #     all_cols = [list(r.keys()) for r in rows]
            #     cols = list(set(itertools.chain.from_iterable(all_cols)))
            #     cols.append(cols.pop(cols.index('Message')))
            #     data = pd.DataFrame(rows, columns=cols)
            #     data.to_csv("/Users/mathieukremeth/Desktop/test.csv")
            #     print("Done")

            for art in articles:
                date = art.find("time", itemprop="datePublished").text
                if int(date[-4:]) > 2015:

                    row = {
                        "Review Counter": None,
                        "Name": None,
                        "Post Date": None,
                        "Country": None,
                        "Overall Rating": None,
                        "Message": None
                    }

                    # Author
                    author = art.find(
                        "h3", class_=["text_sub_header", "userStatusWrapper"])

                    # Review Counter
                    counter = art.find("span", class_="userStatusReviewCount")
                    if counter:
                        row['Review Counter'] = counter.text

                    # Name
                    name = art.find("span", itemprop="name").text
                    row['Name'] = name

                    ## DATE ##
                    row['Post Date'] = date

                    ## COUNTRY ##
                    if counter:
                        country = author.text.replace(counter.text, "")
                        country = country.replace(date, "")
                        country = country.replace(name + " ", "")
                    else:
                        country = author.text.replace(date, "")
                        country = country.replace(name + " ", "")
                    country = country.replace("\n", "")
                    country = country.replace("(", "")
                    country = country.replace(")", "")
                    row['Country'] = country

                    ## RATING ##
                    rating = art.find("span", itemprop="ratingValue")
                    row['Overall Rating'] = rating.text

                    table = art.find("table", class_="review-ratings")
                    specs = table.find_all("tr")
                    for spec in specs:
                        columns = spec.find_all("td")
                        key = columns[0].text
                        value = columns[1].find_all("span", class_="star fill")
                        if value:
                            value = len(value)
                        else:
                            value = columns[1].text
                        row[key] = value

                    ## MESSAGE ##
                    message = art.find("div", class_="text_content")
                    row['Message'] = message.text.split("| ")[-1]

                    rows.append(row)
                    print(len(rows))
                    if len(rows) % 10000:
                        all_cols = [list(r.keys()) for r in rows]
                        cols = list(set(itertools.chain.from_iterable(all_cols)))
                        cols.append(cols.pop(cols.index('Message')))
                        data = pd.DataFrame(rows, columns=cols)
                        data.to_csv(f"/Users/mathieukremeth/Desktop/skytrax-{int(len(rows)/1000)}k.csv")

                else:
                    break

            driver.back()


all_cols = [list(r.keys()) for r in rows]
cols = list(set(itertools.chain.from_iterable(all_cols)))
cols.append(cols.pop(cols.index('Message')))
data = pd.DataFrame(rows, columns=cols)
data.to_csv("/Users/mathieukremeth/Desktop/skytrax.csv")


driver.quit()
