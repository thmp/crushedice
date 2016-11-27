#!/usr/bin/python2.7

import sys
import re
import argparse
import fileinput
import requests
import codecs
from os import path, listdir, makedirs
from copy import deepcopy

from bs4 import BeautifulSoup, Comment, NavigableString
import urlparse

from collections import Counter

from autocues import *
from core import get_tag_with_max_score, get_total_score, style_all_tags


class Reporter(object):

    news_container = None

    def read(self, url=None, html=None, soup=None, autocue=default_autocue):

        self.autocue = autocue

        if soup is not None:
            self.soup = soup
        else:
            if html is not None:
                self.soup = self._get_soup(html)
            else:
                if url is not None:
                    html = requests.get(url).content
                    self.soup = self._get_soup(html)
                else:
                    self.soup = None

        self.make_urls_absolute(self.soup, url)

        self.autocue.execute(self.soup, PRE_TRAVERSAL)

        # We work our way up the DOM
        for tag in reversed(self.soup.find_all()):

            if tag.name == 'p':
                evaluate_as = EVAL_PARAGRAPH
            else:
                # If tag contains text of its own, evaluate it as a paragraph
                evaluate_as = EVAL_CONTAINER
                for child in tag.children:
                    if isinstance(child, NavigableString):
                        text = unicode(child).strip()
                        if len(text) > 10:
                            evaluate_as = EVAL_PARAGRAPH
                            continue

            self.autocue.execute(tag, evaluate_as)

        self.autocue.execute(self.soup, POST_TRAVERSAL)
        self.news_container = get_tag_with_max_score(self.soup)


    def report_styled_soup(self, background=True, margin=None, border=False, css=True, images=True, only_container=False):


        if only_container:
            self.soup = self.news_container

        style_all_tags(self.soup, self.news_container, background, margin, border, css, images, only_container)

        return self.soup


    def report_news(self):

        self.autocue.execute(self.news_container, NEWS_CONTAINER)
        text = self.news_container.get_text()
        text = self.autocue.execute(text, NEWS_TEXT)
        return text


    def _get_soup(self, html):

        html = self.autocue.execute(html, HTML)

        # Create a soup using the lxml parser
        soup = BeautifulSoup(html, "lxml")


        return soup

    def make_urls_absolute(self, soup, url):

        if url is None:
            url = self.guess_base_url(soup)


        for tag in soup.findAll('a', href=True):
            tag['href'] = urlparse.urljoin(url, tag['href'])

        for tag in soup.findAll('link', href=True):
            tag['href'] = urlparse.urljoin(url, tag['href'])

        for tag in soup.findAll('img', href=True):
            tag['src'] = urlparse.urljoin(url, tag['src'])


    def guess_base_url(self,soup):

        urls = []
        base_urls = []
        urls.extend([tag['href'] for tag in soup.findAll('a', href=True)])
        urls.extend([tag['href'] for tag in soup.findAll('link', href=True)])
        urls.extend([tag['src'] for tag in soup.findAll('img', href=True)])

        for url in urls:
            res = urlparse.urlparse(url)
            base_urls.append(res.scheme + "://" + res.netloc + "/")

        try:
            cnt = Counter(base_urls)
            url = cnt.most_common(1)[0][0]
        except IndexError:
            url = ""

        return url

def main():

    parser = argparse.ArgumentParser(description="Extract news from an HTML file", epilog="Specify either a url (--url) or a list of input files (--input).")
    parser.add_argument('--url', type=str)
    parser.add_argument('--input', metavar='FILE', nargs='+', type=str)
    parser.add_argument('--debug', action='store_true', help="Style the HTML based on scores and save to outputXX.html")
    parser.add_argument('--test', action='store_true', help="process every HTML file in test/input and store the output in test/ouput/")
    args = parser.parse_args()

    if (not args.test) and args.url is None and args.input is None:
        parser.error("Specify either --test, --url or --input.")

    my_reporter = Reporter()


    if args.test:
        test_path = 'test'

        for dirname in ['html_01','html_02','html_03','html_04','html_05','text']:
            try:
                makedirs(path.join(test_path, 'output', dirname))
            except:
                pass

        for name in sorted(listdir(path.join(test_path, 'input'))):

            print "Processing %s ..." % name

            if path.isfile(path.join(test_path, 'output', 'html_01', name)):
                continue


            #with codecs.open(path.join(test_path, 'input', name), 'r', encoding='utf-8') as f:


            with open(path.join(test_path, 'input', name), 'rb') as f:
                my_reporter.read(html=f.read())


            with codecs.open(path.join(test_path, 'output', 'html_01', name), 'w+', encoding='utf-8') as f:
                f.write(my_reporter.report_styled_soup(background=False).prettify(formatter="html"))

            with codecs.open(path.join(test_path, 'output', 'html_02', name), 'w+', encoding='utf-8') as f:
                f.write(my_reporter.report_styled_soup(background=True).prettify(formatter="html"))

            with codecs.open(path.join(test_path, 'output', 'html_03', name), 'w+', encoding='utf-8') as f:
                f.write(my_reporter.report_styled_soup(background=True, margin=2).prettify(formatter="html"))

            with codecs.open(path.join(test_path, 'output', 'html_04', name), 'w+', encoding='utf-8') as f:
                f.write(my_reporter.report_styled_soup(background=True, margin=5, border=True, css=False, images=False).prettify(formatter="html"))

            with codecs.open(path.join(test_path, 'output', 'text', path.splitext(name)[0]+'.txt'), 'w+', encoding='utf-8') as f:
                f.write(my_reporter.report_news())

            with codecs.open(path.join(test_path, 'output', 'html_05', name), 'w+', encoding='utf-8') as f:
                f.write(my_reporter.report_styled_soup(background=True, margin=5, border=True, css=False, images=False, only_container=True).prettify(formatter="html"))



    else:
        debug_counter = 0
        if args.url is not None:
            my_reporter.read(url=args.url)

            if args.debug:
                debug_counter += 1
                write_debug(my_reporter, debug_counter)
            else:
                print my_reporter.report_news()

        else:
            for filename in args.input:
                with codecs.open(filename, 'r', encoding='utf-8') as f:
                    my_reporter.read(html=f.read())

                    if args.debug:
                        debug_counter += 1
                        write_debug(my_reporter, debug_counter)
                    else:
                        print my_reporter.report_news()


def write_debug(reporter, debug_counter):

    with codecs.open('debug/output%02d.html' % debug_counter, 'w+', encoding='utf-8') as f:
        f.write(reporter.report_styled_soup(background=True).prettify(formatter="html"))

    with codecs.open('debug/output%02d.txt' % debug_counter, 'w+', encoding='utf-8') as f:
        f.write(reporter.report_news())


if __name__ == '__main__':
    sys.exit(main())
