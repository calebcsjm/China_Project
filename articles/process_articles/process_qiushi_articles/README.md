# Explanation of Files:

## validate_articles.ipynb

This is the first step in the process after scraping all the Qiushi articles. I drop any articles that are missing the year and compute which quarter of the year the article belongs to. I drop articles that have no text (these are usually images of economic performance or event attendees) and remove top-level links (when 2-3 articles are grouped together and included in the text of a super article, causing them to be double counted). Finally, I drop articles from 2024 and any duplicate articles. 

## process_articles.ipynb

Using the csv of validated articles generated above, I do a number of different things to clean the text and prepare it for future analysis. 