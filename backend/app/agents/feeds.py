"""RSS feed list for live ingest (LIVE_INGEST=1). Edit freely; failing feeds are skipped."""

FEEDS: list[tuple[str, str]] = [
    # (source name, feed url)
    # Global news
    ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml"),
    ("BBC Technology", "http://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("BBC Business", "http://feeds.bbci.co.uk/news/business/rss.xml"),
    ("BBC Science", "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml"),
    ("Reuters World", "http://feeds.reuters.com/reuters/worldNews"),
    ("Reuters Business", "http://feeds.reuters.com/reuters/businessNews"),
    # Pakistan
    ("Dawn", "https://www.dawn.com/feeds/home"),
    ("Dawn Business", "https://www.dawn.com/feeds/business"),
    ("Dawn Sport", "https://www.dawn.com/feeds/sport"),
    ("The News", "https://www.thenews.com.pk/rss/1/16"),  # Economy
    ("Geo News", "https://www.geo.tv/rss/1/index.xml"),
    # Tech
    ("The Guardian Technology", "https://www.theguardian.com/technology/rss"),
    ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
    ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ("Wired", "https://www.wired.com/feed/rss"),
    ("TechCrunch", "https://techcrunch.com/feed/"),
    # Science & Space
    ("NASA", "https://www.nasa.gov/feed/"),
    ("New Scientist", "https://www.newscientist.com/feed/home/"),
    # Cricket
    ("ESPNcricinfo", "https://www.espncricinfo.com/rss/content/story/feeds/0.xml"),
    # Finance & Markets
    ("FT", "https://www.ft.com/rss/home"),
    ("Bloomberg Markets", "https://feeds.bloomberg.com/markets/news.rss"),
    # Books & Ideas
    ("The Economist", "https://www.economist.com/the-world-this-week/rss.xml"),
    ("Aeon", "https://aeon.co/feed.rss"),
]

HN_TOP = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
