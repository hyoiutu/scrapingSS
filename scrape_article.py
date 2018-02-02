import lxml.html
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import re
from functools import reduce
import os
from time import sleep
import socket
from selenium.webdriver.chrome.options import Options

options = Options()
options.binary_location = "/usr/bin/google-chrome-stable"
options.add_argument("--headless")

driver = webdriver.Chrome(chrome_options=options)

def get_article(url):
    driver.get(url)
    root = lxml.html.fromstring(driver.page_source)
    law_articles = root.cssselect("div")
    if len(law_articles) == 0:
        with open("articles/problem_urls.csv", "a") as f:
            f.write(url)
        raise Exception("problem occured in {url}")
    articles = [article.text_content() for article in law_articles
                if article.text_content() is not None]
    return articles


def get_many_article():
    with open("links.dat", "r") as f:
        with open("checkpoint", "r") as g:
            cursor = int(g.readline())
            links = f.readlines()[cursor:]
    for current_elapsed, url in enumerate(links):
        url = url.replace("\n", "")
        while True:
            try:
                articles = get_article(url)
            except socket.error as serr:
                print(serr)
                with open("articles/problem_urls.dat", "a") as f:
                    f.write(url + "\n")
                    print(f"problem occured in {url}")
                break
            except TimeoutException as e:
                print(e)
                continue
            else:
                print(f"{url} ... scraping is done")
                print(f"elapsed...{current_elapsed}/{len(links)}")
                print("wait 10 seconds")
                sleep(10)
                break
        with open("checkpoint", "w") as f:
            f.write(f"{current_elapsed+cursor}")
        yield [url, reduce(lambda x, y: x + y, articles)]


get_article_gen = get_many_article()

for url, article in get_article_gen:
    domain = re.search(r"http://(.+)/", url).group(1)
    if ".html" not in url:
        file_name = re.search(r"(p=[0-9]+)", url).group(1)
    else:
        file_name = re.search(r".+/(.+)\.html", url).group(1)
    try:
        os.makedirs(f"articles/{domain}")
    except OSError:
        print("dir is already exist")
    print(f"dir_name={domain},file_name={file_name}")
    with open(f"articles/{domain}/{file_name}-articles.dat", "w") as f:
        f.write(article)
