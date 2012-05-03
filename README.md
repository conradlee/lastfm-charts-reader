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

What the script will do
====================
The script first queries the lastfm API for a list of all cities with charts.  Next, for each of those charts, it queries the API for the dates on which charts are available.  All this is done relatively quickly, in a few hundred API calls.  This check is made every time the script is called.

Next, the script scrapes all of the "top artists" charts (each city for each week).  It then repeats these queries for the "top tracks" charts.  This will take hundreds of thousands of API calls.  If the script is interrupted though, it will remember where it was and only make API calls for the data it doesn't yet have.  So if you've already downloaded all the data, then no API calls will be made (except for the initial check mentioned in the last paragraph).

The script uses pyparallelcurl.py (from Pete Warden) to make calls in parallel.  If the calls are being made too quickly or too slowly, modify the value of MAX_REQUESTS in scrapers/scrape_all.py
