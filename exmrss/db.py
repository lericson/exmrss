import datetime
from sqlalchemy import MetaData, Table, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import mapper

metadata = MetaData()
feed_entries = Table("entries", metadata,
    Column("entry_id", Integer, primary_key=True),
    Column("guid", String(128), unique=True, nullable=False),
    Column("title", String(64), nullable=False),
    Column("html", Text, nullable=False),
    Column("ref_url", String(128), nullable=False),
    Column("created", DateTime, nullable=False))

html_fmt = """<p>Explosm.net Comic Entry {title}</p>
<p><img src="{img_url}" alt="{title}"/></p>
<p><a href="{link}">{link}</a></p>
"""

class FeedEntry(object):
    def __init__(self, title, html, ref_url, created=None):
        self.title = title
        self.html = html
        self.ref_url = ref_url
        self.created = created if created else datetime.datetime.now()
        self.guid = ref_url + "#" + str(created)

    def __repr__(self):
        return "%s(ref_url=%r)" % (self.__class__.__name__, self.ref_url)

    @classmethod
    def latest(cls, db_sess):
        return db_sess.query(cls).order_by(cls.created.desc()).first()

    @classmethod
    def latest_created(cls, db_sess):
        qry = db_sess.query(feed_entries.c.created)
        qry = qry.order_by(cls.created.desc())
        for (created,) in qry:
            return created

    @classmethod
    def from_item(cls, item):
        title = u"%s: %s" % (item["title"], item["img_title"])
        html = html_fmt.format(**item)
        return cls(title, html, item["link"], created=item["touched"])

mapper(FeedEntry, feed_entries)
