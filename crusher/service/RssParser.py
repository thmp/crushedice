import feedparser
from datetime import datetime
from time import mktime
import time


class RssParser(object):

    @staticmethod
    def parse(feed):
        items = []

        rss_url = feed['rss_url']
        language = feed['language']

        feed = feedparser.parse(rss_url)
        for item in feed["items"]:
            try:
                item['guid']
            except KeyError:
                try:
                    item['guid'] = item['link']
                except KeyError:
                    print "[rssp] could not find guid or link! "
                    continue

            try:
                item["title"]
            except KeyError:
                pass

            try:
                item["published_parsed"]
            except KeyError:
                item["published_parsed"] = time.localtime()

            dbitem = {
                "title": item['title'],
                "rss_guid": item['guid'],
                "rss_link": item['link'],
                "pubDate": datetime.fromtimestamp(mktime(item['published_parsed'])),
                "language": language
            }

            items.append(dbitem)

        return items
