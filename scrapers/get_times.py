import get_cities
import datetime, time
import simplejson as json
import pycurl
import pyparallelcurl
import glob
from collections import defaultdict
import os

from scrape_all import API_KEY, CURL_OPTIONS, MAX_REQUESTS

def on_request_done_get_times(content, url, curl_handle, cookie):
    if content is None:
        print "Fetch error for "+url
        return    
    httpcode = curl_handle.getinfo(pycurl.HTTP_CODE);    
    if httpcode != 200:
        print "Fetch error "+str(httpcode)+" for '"+url+"'"
        return

    country = cookie["country"]
    city = cookie["city"]
    out_path = cookie["out_path"]

    out_filename = out_path + city.replace(" ","+")+"_"+country.replace(" ","+")+".json"
    with open(out_filename, "w") as f:
        print "Saving to " + out_filename
        f.write(content + "\n")

def get_times(project_root):
    out_path = project_root + "raw_downloaded/times/"
    if not os.path.isdir(out_path):
        os.makedirs(out_path)

    get_cities.get_metros(project_root)
    country_city_dict = get_cities.get_country_cities(project_root)
    parallel_curl = pyparallelcurl.ParallelCurl(MAX_REQUESTS, CURL_OPTIONS)

    for country in country_city_dict:
        for city in country_city_dict[country]:
            request = "http://ws.audioscrobbler.com/2.0/?method=geo.getmetroweeklychartlist&format=json&metro=%s&country=%s&api_key=%s" % (city, country, API_KEY)
            request = request.replace(" ","+")
            cookie = {"country":country, "city":city, "out_path":out_path}
            print request
            try:
                parallel_curl.startrequest(request, on_request_done_get_times, cookie)
            except TypeError:
                parallel_curl.startrequest(request.encode("utf-8"), on_request_done_get_times, cookie)
    parallel_curl.finishallrequests()
    return read_times_from_file(project_root)

def read_times_from_file(project_root):
    out_path = project_root + "raw_downloaded/times/"
    time_filenames = glob.glob(out_path + "*.json")
    return_tups = []
    for time_filename in time_filenames:
        f = open(time_filename)
        line = f.read()
        f.close()
        
        response_dict = json.loads(line.strip())
        city, country = f.name.split("/")[-1].replace(".json","").split("_")
        try:
            for d in response_dict["weeklychartlist"]["chart"]:
                return_tups.append((country, city, int(d["from"]), int(d["to"])))
        except KeyError:
            raise KeyError, str(response_dict) + "\n" + time_filename
    return return_tups
