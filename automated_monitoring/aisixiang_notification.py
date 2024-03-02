from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import logging
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime

page = urlopen("https://www.aisixiang.com/rss?type=1")
xml = page.read().decode("utf-8")
rss_soup = BeautifulSoup(xml, features='xml')

articles = rss_soup.find_all('item')
most_recent_time_string = articles[0].pubDate.text

filehandle = open("slackbot_token.txt", 'r')
SLACK_BOT_TOKEN = filehandle.read() 
filehandle.close()

client = WebClient(token=SLACK_BOT_TOKEN)
logger = logging.getLogger(__name__)


def notify(article):
    print(f"\nNew article: {article.title.text}")
    message = article.title.text + "\n" + article.link.text
    # determine where you want to send the message to
    # send_email_alert(message)
    client.chat_postMessage(
    channel="general", 
    text=message
)

def identify_new_articles(previous_most_recent_timestamp, articles):
    time_format = '%A, %d %B %Y %H:%M:%S %z'

    # convert the timestamp string to a datetime object
    reference_time = datetime.strptime(previous_most_recent_timestamp, time_format)
    print(f"\nReference time: {reference_time}")

    for article in articles:
        article_time = article.pubDate.text
        article_time = datetime.strptime(article_time, time_format)

        if article_time > reference_time:
            notify(article)

if not os.path.exists("previous_most_recent_timestamp.txt"):
    open("previous_most_recent_timestamp.txt", 'w+').close()

filehandle = open("previous_most_recent_timestamp.txt", 'r')
previous_most_recent_timestamp = filehandle.read() 
filehandle.close()

# in case this is the first run, set the timestamp to be the oldest in the rss file
if previous_most_recent_timestamp == "":
    previous_most_recent_timestamp = articles[-1].pubDate.text

print(f"Previous most recent timestamp: {previous_most_recent_timestamp}")

if most_recent_time_string == previous_most_recent_timestamp:
    # matches, no new info
    print(False)
else:
    # does not match, send notifications for new ones
    filehandle = open("previous_most_recent_timestamp.txt", 'w')

    identify_new_articles(previous_most_recent_timestamp, articles)

    filehandle.write(most_recent_time_string)
    filehandle.close()
    print(True)
