
import feedparser
import time
from datetime import datetime , timedelta
from dateutil.parser import parser , parse
from telegram.ext import Updater 
import logging
import telegram
import requests
import pytz

logging.basicConfig(level=logging.ERROR)

BOT_TOKEN = ''
CHANNEL_ID = '' 
bot = telegram.Bot(BOT_TOKEN)
FEED_URL = ['https://grahamcluley.com/feed/', 
            'https://threatpost.com/feed/',
            'https://krebsonsecurity.com/feed/', 
            'https://www.darkreading.com/rss.xml',
            'http://feeds.feedburner.com/eset/blog',
            'https://davinciforensics.co.za/cybersecurity/feed/',
            'https://blogs.cisco.com/security/feed', 
            'https://www.infosecurity-magazine.com/rss/news/', 
            'http://feeds.feedburner.com/GoogleOnlineSecurityBlog',
            'http://feeds.trendmicro.com/TrendMicroResearch',
            'https://www.bleepingcomputer.com/feed/',
            'https://www.proofpoint.com/us/rss.xml',
            'http://feeds.feedburner.com/TheHackersNews?format=xml', 
            'https://www.schneier.com/feed/atom/',
            'https://www.binarydefense.com/feed/',
            'https://securelist.com/feed/',
            'https://research.checkpoint.com/feed/',
            'https://www.virusbulletin.com/rss', 
            'https://modexp.wordpress.com/feed/',
            'https://www.tiraniddo.dev/feeds/posts/default',
            'https://blog.xpnsec.com/rss.xml',
            'https://msrc-blog.microsoft.com/feed/',
            'https://www.recordedfuture.com/feed',
            'https://www.sentinelone.com/feed/',
            'https://redcanary.com/feed/',
            'https://cybersecurity.att.com/site/blog-all-rss',
            'https://www.enisa.europa.eu/media/news-items/news-wires/RSS',
            'https://research.checkpoint.com/category/threat-research/feed/',
            'https://securityintelligence.com/category/x-force/feed/',
            'https://www.netskope.com/blog/category/netskope-threat-labs/feed',
            'https://www.kaspersky.co.in/blog/tag/threat-intelligence/feed/',
            'https://www.fireeye.com/blog/threat-research/_jcr_content.feed?format=xml',
            'https://www.securonix.com/analyst-resources/resources-by-topic/threat-research/',
            'https://www.mcafee.com/blogs/tag/advanced-threat-research/feed',
            'https://blogs.juniper.net/threat-research/feed',
            'https://www.paloaltonetworks.com/blog/category/threat-research/feed/']
 
RANSOMWATCH = "https://raw.githubusercontent.com/joshhighet/ransomwatch/main/posts.json"

updater = Updater(token=BOT_TOKEN, use_context=True)

def rans_feed (source):
    try:
        posts = requests.get(source).json()
        logging.debug('[+] Querying Ransomwatch\n')
    except Exception as e:
        logging.error('[!] Unable to reach Ransomwatch: ' + source)
    
    for post in posts:
        if datetime.utcnow() - parser().parse(post['discovered']) < timedelta(minutes=20):
            feed_title = 'Title: ' + post['post_title']
            feed_group_name = 'Group Name: ' + post['group_name']
            feed_discovered = 'Discovered: ' + post['discovered']
            message = feed_title + '\n' + feed_group_name + '\n' + feed_discovered
            updater.bot.send_message(chat_id=CHANNEL_ID, text=message)


def send_message(title, link):
    try:
        bot.send_message(chat_id=CHANNEL_ID, text=title + ": " + link)
    except Exception as e:
        print(f"An error occurred while sending message: {e}")

def check_and_send(url):
    try:
        feed = feedparser.parse(url)
        # Get the time of the most recent article in the feed
        latest_time = feed['entries'][0]['published']
        # Parse the time into a datetime object
        latest_datetime = parse(latest_time)
        # Convert the datetime object to a timestamp
        latest_timestamp = time.mktime(latest_datetime.timetuple())
        # Get the current time
        current_timestamp = time.time()

        # If the article was published in the last 20 minutes, send it to the Telegram chat
        if current_timestamp - latest_timestamp < 60 * 20:
            latest_title = feed['entries'][0]['title']
            latest_link = feed['entries'][0]['link']
            send_message(latest_title, latest_link)
    except Exception as e:
        print(f"An error occurred while checking feed {url}: {e}")

def main():
    first_iter = True
    while True:
        if first_iter:
            message= 'starting bot ...'
            bot.send_message(chat_id=CHANNEL_ID , text=message)
            first_iter = False
        rans_feed(RANSOMWATCH)
        # Check each feed every 20 minutes
        for url in FEED_URL:
            check_and_send(url)
        time.sleep(60 * 20)
        
if __name__ == "__main__":
    main()


