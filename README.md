lastfm-charts-reader
====================

Reads data from lastfm&#39;s API, specifically, charts on metropolitan areas

Dependencies
====================
* pycurl
* simplejson


Usage
====================
To use this script, first open the file scrapers/scrape_all.py,
and look at the following lines:

```python
API_KEY = ""     # REQUIRED - Fill this in
API_SECRET = ""  # REQUIRED - Fill this in  
USERNAME = ""    # REQUIRED - Fill this in
```

You need to fill these in with information from your own lastfm API account.

Next, simply run the command

```bash
python main.py
```

This will first download all data from last.fm's api into a folder called
raw_downloaded/, and will then parse it into CSV files in a folder called
parsed/
