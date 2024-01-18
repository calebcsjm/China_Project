'''given a url, scrape the article information'''

from newspaper import Article
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json

class QiuShiArticleParser:
    def __init__(self, url):
        # get the beautiful soup version
        page = urlopen(url)
        html = page.read().decode("utf-8")
        self.soup = BeautifulSoup(html, "html.parser")

        # get the newspaper article version
        self.article = Article(url, language='zh')
        self.article.download()
        self.article.parse()


    def get_author(self):
        span_els = self.soup.find_all("span", class_="appellation")
        # author is the second appel element
        author_el = span_els[1].text.strip()
        # remove the "Author:" piece
        author = author_el.split("：")[1]
        return author
    
    def get_title(self):
        return self.soup.find('h1').text.strip()
    
    def get_date(self):
        date_el = self.soup.find("span", class_="pubtime").text.strip()
        # remove the time piece
        date = date_el.split(" ")[0]
        return date
    
    def get_text(self):
        return self.article.text.replace('\n', "")
    
class QiuShiArticle:
    def __init__(self, article_parser):
        self.author = article_parser.get_author()
        self.title = article_parser.get_title()
        self.date = article_parser.get_date()
        self.text = article_parser.get_text()

    def toJson(self):
        return self.__dict__