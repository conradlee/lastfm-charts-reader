import os
import pycurl
import pyparallelcurl
import simplejson as json
import urllib

from scrape_all import API_KEY, CURL_OPTIONS, MAX_REQUESTS, API_KEY, API_SECRET

MAX_REQUESTS = 5

curl_options = {
    pycurl.SSL_VERIFYPEER: False,
    pycurl.SSL_VERIFYHOST: False,
    pycurl.USERAGENT: '',
    pycurl.FOLLOWLOCATION: True,
}

CHART_TYPES = ["artists", "tracks"]

def on_request_done_save(content, url, curl_handle, cookie):
    if content is None:
        print "Fetch error for " + url
        return
    
    httpcode = curl_handle.getinfo(pycurl.HTTP_CODE);    
    if httpcode != 200:
        print "Fetch error "+str(httpcode)+" for '"+url+"'"
        return

    out_filename = cookie["out_filename"]

    with open(out_filename, "w") as f:
        f.write(content + "\n")
        f.close()

def scrape_popular_tags(project_root):
    parallel_curl = pyparallelcurl.ParallelCurl(MAX_REQUESTS, curl_options)
    out_path = "%sraw_downloaded/" % project_root
    if not(os.path.isdir(out_path)):
        os.makedirs(out_path)
    out_filename = out_path +"toptags.json"
    if not os.path.isfile(out_filename):
        url = "http://ws.audioscrobbler.com/2.0/?method=chart.getTopTags&api_key=%s&format=json&limit=500" % (API_KEY)
        parallel_curl.startrequest(url, on_request_done_save, {"out_filename": out_filename})
        parallel_curl.finishallrequests()
    with open(out_filename) as f:
        json_dict = json.loads(f.read().strip())
        lastfm_list = json_dict["tags"]["tag"]
        lastfm_list.sort(key = lambda d: int(d["reach"]), reverse=True)
        return [urllib.quote_plus(d["name"]) for d in lastfm_list]
    
def scrape_tags_charts(project_root):
    top_tags = scrape_popular_tags(project_root)
    parallel_curl = pyparallelcurl.ParallelCurl(MAX_REQUESTS, curl_options)
    return_dict = {"tracks":{}, "artists":{}}
    download_dir = project_root + "raw_downloaded/tags/"
    if not os.path.isdir(download_dir):
        os.makedirs(download_dir)
    for chart_type in CHART_TYPES:
        for tag in top_tags:
            for page_no in range(1,5):
                out_dir = "%stag-%s/" % (download_dir, chart_type)
                if not os.path.isdir(out_dir):
                    os.makedirs(out_dir)
                out_filename = "%s%s_page%d.json"% (out_dir, tag, page_no)
                if not os.path.isfile(out_filename):
                    print "Requesting top %s for tag %s from lastfm" % (chart_type, tag)
                    url = "http://ws.audioscrobbler.com/2.0/?method=tag.getTop%s&tag=%s&api_key=%s&format=json&limit=250&page=%d" % (chart_type ,tag, API_KEY, page_no)
                    parallel_curl.startrequest(url, on_request_done_save, {"out_filename":  out_filename, "chart_type":chart_type})
                else:
                    print "Already scraped chart for tag %s" % tag
        parallel_curl.finishallrequests()
        for tag in top_tags:
            members = []
            for page_no in range(1,5):
                out_filename = "%stag-%s/%s_page%d.json" % (download_dir, chart_type, tag, page_no)
                with open(out_filename) as f:
                    k1 = "top%s" % chart_type
                    k2 = chart_type.strip("s")
                    s = f.read().strip()
                    music_list = json.loads(s)[k1][k2]
                    members = members + [d["url"] for d in music_list]

                return_dict[chart_type][tag] = members
    return return_dict
    
                               
