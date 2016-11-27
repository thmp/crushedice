from reporter.reporter import Reporter


class TextExtractor(object):

    def __init__(self):
        self.extractor = Reporter()

    def extract(self, url):
        self.extractor.read(url)
        return self.extractor.report_news()
