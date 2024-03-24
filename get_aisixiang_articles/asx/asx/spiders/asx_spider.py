from typing import Iterable
import scrapy
import pandas as pd

class ASXSpider(scrapy.Spider):

    name = 'articles'

    # handle_httpstatus_list = [404]

    def start_requests(self):
        # use the tag to specify which links to pull
        tag = getattr(self, "tag", None)
        
        if tag is None:
            # just a test
            file = 'test_links.csv'
        else:
            # load the next file
            file = 'split_links_' + tag + ".csv"

        basic_link_path = '/Users/calebharding/Documents/BYU/2023-2024/China_Project/get_aisixiang_articles/asx_article_links_split/'
        full_path = basic_link_path + file
        urls = pd.read_csv(full_path)['links']

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def get_authors_and_title(self, text):
        num_splits = len(text.split('：'))
        # has both
        if num_splits >= 2:
            return text.split('：', 1)
        # no authors, just title
        if num_splits == 1:
            return None, text

    def parse(self, response):
        url = response.request.url
        
        try:
            url = response.request.url
            title_author = response.css("h3::text").getall()[0]
            authors, title = self.get_authors_and_title(title_author)
            date = response.css('div.info').re("....-..-..")[0]
            paragraphs = response.css('div.article-content p::text').getall()
            text = "".join(paragraphs)
            text = text.replace('\n', '').replace('\t', '')

            yield {
                'title': title, 
                'authors': authors, 
                'date': date,
                'url': url,
                'text': text
            }
        except:
            yield {
                'title': "", 
                'authors': "", 
                'date': "",
                'url': url,
                'text': ""
            }