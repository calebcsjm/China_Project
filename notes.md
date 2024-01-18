Web crawling: 
- could use the scrapy package, with the CrawlSpider (it has rules for which links it can extract from the page and continue extracting) https://docs.scrapy.org/en/latest/topics/spiders.html

article_scraper.py has the core classes to scrape the Qiushi articles, which have already been tested

article_analysis.ipynb uses the article_scraper to get the articles and do some basic word count analysis and such

Issues: 
- some of the editions will basically have some doubled stuff, since they have an article that includes multiple articles, with links from the homepage to each of them as well, as seen here: http://www.qstheory.cn/dukan/qs/2014/2019-08/01/c_1124820140.htm 2019年第15期