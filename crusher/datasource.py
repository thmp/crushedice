from pymongo import MongoClient


class MongoDataSource(object):

    def __init__(self, mongourl, db):
        self.client = MongoClient(mongourl)
        self.db = self.client[db]

    def get_feeds_to_parse(self):
        return self.db.medias.find({'language': 'de'})

    def insert_articles(self, items, feed):
        for item in items:
            # Check if article already exists in storage
            if not self.db.articles.find_one({"rss_guid": item["rss_guid"]}):
                # save media name in article
                item["media"] = feed["title"]
                # otherwise save entry
                self.db.articles.insert(item)

    def get_articles_to_extract(self):
        return self.db.articles.find({"text": {"$exists": False}, "language": "de"}).sort("pubDate", -1).limit(5)

    def get_articles_to_extract_images(self):
        return self.db.articles.find({"image": {"$exists": False}}).sort("pubDate", -1).limit(5)

    def count_articles_to_extract_text(self):
        return self.db.articles.find({"text": {"$exists": False}, "language": "de"}).count()

    def count_articles_to_extract_images(self):
        return self.db.articles.find({"image": {"$exists": False}}).count()

    def save_article(self, article):
        self.db.articles.save(article)

    def get_articles_to_summarize(self):
        return self.db.articles.find({"summary": {"$exists": False}, "text": {"$exists": True}})\
            .sort("pubDate", -1).limit(25)

    def check_if_image_exists(self, url):
        return self.db.images.find_one({"url": url})

    def increment_image_count(self, url):
        document = self.db.images.find_one({"url": url})
        if document:
            try:
                document["count"] += 1
            except KeyError:
                document["count"] = 1
            self.db.images.save(document)

    def insert_image(self, url):
        document = {"url": url, "count": 1}
        self.db.images.save(document)
