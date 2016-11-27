from twisted.internet import reactor
from twisted.internet.threads import deferToThread
from crusher.service.RssParser import *
from crusher.service.ImageExtractor import *
from crusher.service.TextExtractor import *
from crusher.service.CrushedIceSummarizer import *


class Worker(object):

    def __init__(self, datasource):
        self.datasource = datasource

    def parse_rss(self):
        reactor.callLater(60*12, self.parse_rss) # parse again after 12 minutes

        for feed in self.datasource.get_feeds_to_parse():
            wrapper = lambda f : (RssParser().parse(f), f)
            d = deferToThread(wrapper, feed)
            d.addCallback(self.parse_rss_callback)

    def parse_rss_callback(self, (items, feed)):
        self.datasource.insert_articles(items, feed)
        reactor.callLater(0, self.extract_text)
        reactor.callLater(0, self.extract_images)

    def extract_text(self):
        stillTodo = False
        for article in self.datasource.get_articles_to_extract():
            print 'Extracting ' + article['rss_link']
            text = TextExtractor().extract(article['rss_link'])
            article['text'] = text
            self.datasource.save_article(article)
            stillTodo = True

        reactor.callLater(0, self.summarize)

        print 'In text extraction queue: ' + str(self.datasource.count_articles_to_extract_text())

        if stillTodo:
            reactor.callLater(0, self.extract_text)

    def extract_images(self):
        stillTodo = False
        for article in self.datasource.get_articles_to_extract_images():
            print 'Extracting images ' + article['rss_link']
            imgurl = ImageExtractor().extract(article, self.datasource)
            if imgurl:
                article['image'] = imgurl
            else:
                article['image'] = ''  # so we do not visit again
            self.datasource.save_article(article)
            stillTodo = True

        print 'In image extraction queue: ' + str(self.datasource.count_articles_to_extract_images())

        if stillTodo:
            reactor.callLater(0, self.extract_images)

    def summarize(self):
        for article in self.datasource.get_articles_to_summarize():
            print 'Summarizing ' + article['rss_link']
            summary = CrushedIceSummarizer().summarize(article)
            article['summary'] = summary
            self.datasource.save_article(article)
