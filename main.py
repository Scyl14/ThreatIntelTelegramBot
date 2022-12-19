
from datetime import timedelta, datetime
from dateutil import parser
from pprint import pprint
from time import sleep , gmtime
import urllib
import json
import logging
import requests
import feedparser

logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

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

def send_message(message):
    requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHANNEL_ID}&text={message}')

def rans_feed (source):
    try:
        posts = requests.get(source).json()
        logging.debug('[+] Querying Ransomwatch\n')
    except Exception as e:
        logging.warning('[!] Unable to reach Ransomwatch: ' + source)

    for post in posts:
        if datetime.utcnow() - parser.parse(post['discovered']) < timedelta(minutes=20):
            feed_title = 'Title: '+ post['post_title']
            feed_group_name = 'Group Name: '+ post['group_name']
            feed_discovered = 'Discovered: '+ post['discovered']
            send_message(feed_title+'\n'+feed_group_name+'\n'+feed_discovered)
        else:
            pass
    return 

def rss_feed (source):
    logging.debug('[+] Querying Urls: \n')
    for url in source:
        try:
            rss_feed = feedparser.parse(url)
        except Exception as e:
            logging.warning('[!] Unable to parse Url: ' + url)
        for entry in rss_feed.entries:
            try:
                parsed_date = parser.parse(entry.published)
            except:
                parsed_date = parser.parse(entry.updated)         
            parsed_date = parsed_date.replace(tzinfo=None) 
            now_date = datetime.utcnow()               
            published_20_minutes_ago = now_date - parsed_date < timedelta(minutes=20)
            published_today = now_date - parsed_date < timedelta(days=1)
            if published_today:
                logging.debug(f"[+] Checking if published 20' ago: {now_date - parsed_date} | {published_20_minutes_ago}")
                if published_20_minutes_ago:
                    send_message(entry.links[0].href)
                    

def main():
    rans_feed(RANSOMWATCH)
    rss_feed(FEED_URL)
 

if __name__ == "__main__":
    first_iter=True
    while(True):
        if first_iter == True:
            send_message('\U0001F916 Starting BOT')
            first_iter = False
        logging.debug("[+] Starting Iteration\n")
        main()
        sleep(20 * 60)
