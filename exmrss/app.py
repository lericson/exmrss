import datetime
from werkzeug import Request, Response
from werkzeug.exceptions import HTTPException, NotFound
from sqlalchemy import create_engine, func
from sqlalchemy.orm import create_session
from exmrss.db import FeedEntry
from exmrss.fetcher import ExplosmFetcher
from exmrss.feed import build_feed
from exmrss.utils import parse_delta
import os

env_convs = [("EXPLOSM_URL", "explosm_url", str),
             ("EXPLOSM_DB_URI", "db_engine", create_engine),
             ("EXPLOSM_INTERVAL", "fetch_interval", parse_delta)]

explosm_url = "http://feeds.feedburner.com/Explosm"

class NewChecker(object):
    def __init__(self, last=None):
        self.last = last
    def __call__(self, entry, touched=None):
        if not self.last or not touched:
            return True
        return self.last < touched

class ExplosmRSSApp(object):
    defaults = dict(db_engine="sqlite://", explosm_url=explosm_url,
                    fetch_interval="3h")
    default_interval = parse_delta(defaults["fetch_interval"])

    def __init__(self, db_engine, explosm_url, fetch_interval=default_interval):
        self.db_engine = db_engine
        self.explosm_url = explosm_url
        self.fetch_interval = fetch_interval

    @Request.application
    def __call__(self, request):
        db_sess = create_session(self.db_engine)
        try:
            if request.path != "/explosm.rss":
                resp = NotFound(request.path)
            else:
                resp = self.feed_generator(db_sess)
        except HTTPException, e:
            resp = e
        finally:
            db_sess.close()
        return resp

    @classmethod
    def from_environ(cls, environ=None):
        if environ is None:
            environ = os.environ
        kwds = cls.defaults.copy()
        for envvar, kw, conv in env_convs:
            if envvar in environ:
                kwds[kw] = conv(environ[envvar])
            else:
                kwds[kw] = conv(kwds[kw])
        return cls(**kwds)

    def feed_generator(self, db_sess):
        created = FeedEntry.latest_created(db_sess)
        if self.should_refetch(last=created):
            for entry in self.refetch(last=created):
                db_sess.add(entry)
            db_sess.flush()
        qry = db_sess.query(FeedEntry)
        qry = qry.order_by(FeedEntry.created.desc())
        qry = qry.limit(10)
        return build_feed(qry).encode("utf-8")

    def should_refetch(self, last=None):
        if not last:
            return True
        refetch_at = last + self.fetch_interval
        return refetch_at <= datetime.datetime.now()

    def refetch(self, last=None):
        fetcher = ExplosmFetcher(NewChecker(last=last), self.explosm_url)
        for item in fetcher:
            yield FeedEntry.from_item(item)
