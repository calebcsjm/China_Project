'''given a url, scrape the article information'''

from newspaper import Article
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import openai

def process_complicated_author(author):

    with open('./openai_auth.json', 'r') as json_file:
        json_load = json.load(json_file)

    openai.api_key = json_load["api_key"]

    prompt = f"""
    Please give me the names of the authors included in this text, and remove any unnecessary spaces within names. Please give me the names, seperated by a space, and nothing else. For example, if the text was "求是》杂志记者 何雯雯 新县融媒体中心记者 韩 燕", I would want you to tell me "何雯雯 韩燕". The text is: {author}
    """

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[{
            "role":"user",
            "content":prompt
        }]
    )

    return response.choices[0].message.content


class QiuShiArticleParser:
    def __init__(self, url):
        # get the beautiful soup version
        self.url = url
        try:
            page = urlopen(url)
            html = page.read().decode("utf-8")
            self.soup = BeautifulSoup(html, "html.parser")

            # get the newspaper article version
            self.article = Article(url, language='zh')
            self.article.download()
            self.article.parse()
        except:
            print(f"Article with URL: {url} failed to parse")
            self.soup = None
            self.article = None

    def get_authors(self):
        if self.soup == None:
            return None
        span_els = self.soup.find_all("span", class_="appellation")
        try:
            # author is the second appel element
            author_el = span_els[1].text.strip()
            # remove the "Author:" piece
            author = author_el.split("：")[1]

            # see if it needs additional processing
            # no spaces, should be good to go. Or if None, return
            if author == None:
                return [author]
            elif " " not in author:
                return [author]
            # spaces, but length three - a 2 char name with a space
            elif len(author) == 3:
                return [author[0] + author[2]]
            # something more complicated is going on - could be multiple authors, could have additional info 
            else:
                print("Calling ChatGPT...")
                try:
                    author = process_complicated_author(author)
                    print(f"Author returned by ChatGPT: {author}")
                    # split the result in case there is more than one author
                    return author.split(" ")
                except:
                    print("ChatGPT call failed")
                return "CHATGPT" + author

        except:
            return None
    
    def get_title(self):
        if self.soup == None:
            return None
        return self.soup.find('h1').text.strip()
    
    def get_year_edition(self):
        if self.soup == None:
            return None, None
        
        span_els = self.soup.find_all("span", class_="appellation")
        # year/edition is the first appel element
        ye_text = span_els[0].text.strip()
        # get the last piece with the date
        cleaned_ye_text = ye_text[-7:]

        year = cleaned_ye_text[:4]
        edition = cleaned_ye_text[-2:]

        return year, edition
    
    def get_date(self):
        if self.soup == None:
            return None

        date_el = self.soup.find("span", class_="pubtime").text.strip()
        # remove the time piece
        date = date_el.split(" ")[0]
        return date
    
    def get_url(self):
        return self.url
    
    def get_text(self):
        if self.article == None:
            return None

        return self.article.text.replace('\n', "")
    
class QiuShiArticle:
    def __init__(self, article_parser):
        self.authors = article_parser.get_authors()
        self.title = article_parser.get_title()
        self.date = article_parser.get_date()
        self.year, self.edition = article_parser.get_year_edition()
        self.url = article_parser.get_url()

        try:
            self.text = article_parser.get_text()
        except:
            self.text = None
        

    def toJson(self):
        return self.__dict__