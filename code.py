import sqlite3
import requests
import csv
from bs4 import BeautifulSoup
base = sqlite3.connect("base.db")
cur = base.cursor()
base.execute('CREATE TABLE IF NOT EXISTS authors_table(author text, quote text, about text, tegs text)')
page_html = requests.get("http://quotes.toscrape.com/").text
while True:
    try:
        soup = BeautifulSoup(page_html, "lxml")
        tegs = []
        authors = soup.find_all("small", class_="author")
        for i in authors:
            one = soup.find("small", text=i.text).find_parent().find_parent()
            one = one.find_all("a")
            tmp = []
            for a in one:
                sup = BeautifulSoup(str(a), "lxml")
                tmp.append(sup.find("a").text)
            tmp.pop(0)
            tmp_str = ", ".join(tmp)
            tegs.append(tmp_str)

        quotes = soup.find_all("span", class_="text")
        tmp_texts_about = soup.find_all("div", class_="quote")
        texts_about_authors_links = []
        texts_about_authors = []

        for i in tmp_texts_about:
            link = i.find("a").get("href")
            texts_about_authors_links.append(link)
        for i in texts_about_authors_links:
            text_about_author_page = requests.get(f"http://quotes.toscrape.com/{i}").text
            author_text_soup = BeautifulSoup(text_about_author_page, "lxml")
            text = author_text_soup.find("div", class_="author-description").text
            texts_about_authors.append(text)

        for author, quote, text, teg in zip(authors, quotes, texts_about_authors, tegs):
            cur.execute('INSERT INTO authors_table VALUES(?, ?, ?, ?)', (author.text, quote.text, text, str(teg)))
            base.commit()
            arr = [author.text, quote.text, text, str(teg)]
            with open("base.csv", "a", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file, delimiter=";")
                writer.writerow(arr)


        next_link = soup.find("li", class_="next").find("a").get("href")
        page_html = requests.get(f"http://quotes.toscrape.com{next_link}").text
    except:
        raise SystemExit