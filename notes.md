article_scraper.py has the core classes to scrape the Qiushi articles, which have already been tested

article_analysis.ipynb uses the article_scraper to get the articles and do some basic word count analysis and such

Issues: 
- some of the editions will basically have some doubled stuff, since they have an article that includes multiple articles, with links from the homepage to each of them as well, as seen here: http://www.qstheory.cn/dukan/qs/2014/2019-08/01/c_1124820140.htm 2019年第15期
  - The comprehensive link and the sublinks all get scrapped from the main page
- Author names
  - Some of the names have spaces in them (if they only have two characters) - for the authors
  - Some articles have multiple authors
  - could I store the authors as a list? What do i want to use the authors for? Do I actually need them? Or do I want to see a change in authorship over time? Probably not...
  - I could throw the authors at ChatGPT... maybe the rule to use is if there are any spaces? 
  - first check if there are spaces, then if there is just one in the middle of two characters, remove it, and if not then throw it at ChatGPT?
  - ChatGPT prompt: Please give me the names of the authors included in this text, and remove any unnecessary spaces within names. Please give me the names, seperated by a space, and nothing else. For example, if the text was "求是》杂志记者 何雯雯 新县融媒体中心记者 韩 燕", I would want you to tell me "何雯雯 韩燕". The text is: {author}
  - that'll work 
  - RESOLVED


I am probably going to come up with additional queries that I want to do later... so I will need a way to do new analysis of the documents after they are stored

MongoDB:
- Use the calebh27@byu.edu login
- how to iterate over each document? and keep track of the ones that have already been done? And run a function again, so that it only runs on ones that haven't already been done? 

Next step: Add the articles to MongoDB, and then start practicing doing the operations on them