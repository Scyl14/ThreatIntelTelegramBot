
import feedparser
import time
from datetime import datetime , timedelta
from dateutil import parser
from telegram.ext import Updater, CommandHandler
import logging
import requests
import pytz

logging.basicConfig(level=logging.ERROR)

BOT_TOKEN = ''
CHANNEL_ID = '' 
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
        if datetime.utcnow() - parser.parse(post['discovered']) < timedelta(minutes=20):
            feed_title = 'Title: ' + post['post_title']
            feed_group_name = 'Group Name: ' + post['group_name']
            feed_discovered = 'Discovered: ' + post['discovered']
            message = feed_title + '\n' + feed_group_name + '\n' + feed_discovered
            updater.bot.send_message(chat_id=CHANNEL_ID, text=message)


def get_latest_article(feed):
    feed['entries'].sort(key=lambda entry: entry.published_parsed or entry.updated_parsed, reverse=True)

    if not feed['entries']:  
        return None  

    for entry in feed['entries']:
        date = entry.published_parsed or entry.updated_parsed
        if not hasattr(date, 'tzinfo'):  
            tz = pytz.timezone(feed.feed.get('tzinfo', 'UTC'))  
            date = tz.localize(datetime.datetime.fromtimestamp(time.mktime(date)))
        date = date.astimezone(pytz.utc)  
        entry.published_parsed = entry.updated_parsed = date

    return feed['entries'][0]  

def send_article(article, updater, sent_articles):
    if article.title not in sent_articles:
        message = f"{article.title}\n{article.link}"
        updater.bot.send_message(chat_id=CHANNEL_ID, text=message)
        sent_articles.add(article.title)
        time.sleep(5)  

def check_feeds(feed_urls, updater):
    sent_articles = set()
    for url in feed_urls:
        try:
            feed = feedparser.parse(url)
            article = get_latest_article(feed)
            if article is not None:
                send_article(article, updater, sent_articles)
        except Exception as e:
            logging.error(f"Error parsing feed {url}: {e}")
while True:
    check_feeds(FEED_URL, updater)
    rans_feed(RANSOMWATCH)
    time.sleep(60 * 20)  #
