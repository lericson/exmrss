import time
import datetime
from email.utils import formatdate

feed_header = """
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
  <channel>
    <title>Explosm.net/lericson</title>
    <link>http://google.com/</link>
    <description>Explosm.net wrapped up in a very nice way indeed.</description>
    <lastBuildDate>{last_build_date}</lastBuildDate>
    <generator>exmrss</generator>
""".lstrip()
feed_footer = "  </channel>\n</rss>\n"

entry_html = """
    <item>
      <title>{e.title}</title>
      <pubDate>{pub_date}</pubDate>
      <link>{e.ref_url}</link>
      <guid>{e.guid}</guid>
      <category>Comics</category>
      <description><![CDATA[{e.html}]]></description>
    </item>
"""

def datetime_to_rfc2822(d):
    return formatdate(time.mktime(d.timetuple()))

def build_feed(entries, html=None):
    if html is None:
        html = []
    last_build = datetime.datetime.min
    for entry in entries:
        last_build = max(last_build, entry.created)
    if not last_build:
        last_build  = datetime.datetime.now()
    last_build_date = datetime_to_rfc2822(last_build)
    html.append(feed_header.format(last_build_date=last_build_date))
    for entry in entries:
        build_entry(entry, html=html)
    html.append(feed_footer)
    return u"".join(html)

def build_entry(entry, html=None):
    if html is None:
        html = []
    pub_date = datetime_to_rfc2822(entry.created)
    html.append(entry_html.format(e=entry, pub_date=pub_date))
