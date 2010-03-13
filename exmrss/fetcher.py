"""Explosm.net fetcher"""

import urllib2
import datetime
import posixpath
import feedparser
from BeautifulSoup import BeautifulSoup

error_thing = {"img_url": "http://http://pb.lericson.se/static/img/guard.png",
               "img_title": "COULD NOT PARSE"}

class ExplosmFetcher(object):
    feed_url = "http://feeds.feedburner.com/Explosm"

    def __init__(self, predicator, feed_url=None):
        self.predicator = predicator
        if feed_url is not None:
            self.feed_url = feed_url

    def __iter__(self):
        feed = self.retrieve()
        for entry in feed.entries:
            touched = datetime.datetime(*entry.updated_parsed[:6])
            if not self.is_comic_entry(entry):
                continue
            elif self.predicator(entry, touched=touched):
                try:
                    yield self.fetch(entry, touched=touched)
                except MalformedPage:
                    return dict(error_thing, link=entry.link,
                                title=entry.title, touched=touched)

    def retrieve(self):
        resp = urllib2.urlopen(self.feed_url)
        return feedparser.parse(resp)

    def fetch(self, entry, touched=None):
        resp = urllib2.urlopen(entry.link)
        soup = BeautifulSoup(resp)
        img = None
        for body in soup("div", {"id": "thebodycontent"}):
            img = body.img["src"]
        if img is None:
            raise RuntimeError("malformed explosm page")
        # Now this part is actually funkalicious.
        title = posixpath.splitext(posixpath.basename(img))[0]
        if title == title.lower():
            title = title.title()
        title = title.replace("-", " ")
        title = title.replace("_", " ")
        return {"img_url": img, "img_title": title, "link": entry.link,
                "title": entry.title, "touched": touched}

    def is_comic_entry(self, entry):
        for tag_desc in entry.tags:
            if tag_desc["term"].lower() == "comics":
                return True
        return False

# This funny section because urlopening on OS X 10.6 in a non-main thread makes
# the interpreter crash. This, funnily, is fixed by importing locale.
if __import__("sys").platform == "darwin":
    __import__("locale")
