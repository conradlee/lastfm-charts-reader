import datetime,time
import simplejson as json
import pycurl
import pyparallelcurl
import glob
from collections import defaultdict
import os

from scrape_all import API_KEY, CURL_OPTIONS, MAX_REQUESTS

def on_request_done_get_metros(content, url, curl_handle, cookie):
    if content is None:
        print "Fetch error for "+url
        return
    
    httpcode = curl_handle.getinfo(pycurl.HTTP_CODE);    
    if httpcode != 200:
        print "Fetch error "+str(httpcode)+" for '"+url+"'"
        return
    out_filename = cookie["out_filename"]
    with open(out_filename,"w") as f:
        f.write(content + "\n")

def get_metros(project_root):
    out_dir = project_root + "raw_downloaded/"
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    parallel_curl = pyparallelcurl.ParallelCurl(MAX_REQUESTS, CURL_OPTIONS)
    requests = []
    request = "http://ws.audioscrobbler.com/2.0/?method=geo.getmetros&format=json&api_key=%s" % (API_KEY)
    parallel_curl.startrequest(request, on_request_done_get_metros, {"out_filename":out_dir + "valid_metros.json"})
    parallel_curl.finishallrequests()

def get_country_cities(project_root):    
    country_city_dict = defaultdict(set)
    metros_filename = project_root + "raw_downloaded/valid_metros.json"
    if not os.path.isfile(metros_filename):
        get_metros(project_root)
    line = open(metros_filename).readline()
    response_dict = json.loads(line.strip())
    if type(response_dict["metros"]) ==type({}):
        if response_dict["metros"].has_key("metro"):
            for d in response_dict["metros"]["metro"]:
                if type(d) == type({}):
                    country = d["country"]
                    city = d["name"]
                    
                    country_city_dict[country].add(city)
                else:
                    print "Oops: d=" + str(d)
                    print file
        else:
            pass
    return country_city_dict
