import datetime, time
import simplejson as json
import pycurl, pyparallelcurl
import glob
from collections import defaultdict
import get_times
import os, sys

from scrape_all import API_KEY, CURL_OPTIONS, MAX_REQUESTS, SCRAPE_TYPES

def on_request_done_save(content, url, curl_handle, cookie):
    # Check response
    if content is None:
        print "Fetch error for "+url
        return
    
    httpcode = curl_handle.getinfo(pycurl.HTTP_CODE);    
    if httpcode != 200:
        print "Fetch error "+str(httpcode)+" for '"+url+"'"
        return

    country = cookie["country"]
    city = cookie["city"]
    start = cookie["start"]
    end = cookie["end"]
    page = cookie["page"]    
    scrape_type = cookie["type"]
    project_root = cookie["project_root"]

    # Save json to file
    dir_name = "%sraw_downloaded/%s/%s/%s/" % (project_root, scrape_type, country, city)
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
    f = open(dir_name + str(start) + "-" + str(end) + "_page-" + str(page) + ".json","w")
    f.write(content + "\n")

def get_chart(chart_type, project_root, request_tups = None):
    parallel_curl = pyparallelcurl.ParallelCurl(MAX_REQUESTS, CURL_OPTIONS)
    if request_tups==None:
        request_tups = get_times.get_times()
    total_request_tups = len(request_tups)*10
    current_request_no = 1
    for request_tup in request_tups:
        for page_no in range(1,11):
            filename = project_root + "raw_downloaded/" + chart_type + "/"+request_tup[0]+"/"+request_tup[1]+"/" + str(request_tup[2]) + "-" + str(request_tup[3]) + "_page-" + str(page_no) + ".json"
            if not os.path.isfile(filename):
                print filename + "does not exist"
                if chart_type == "top_tracks":
                    api_method = "geo.getmetrotrackchart"
                elif chart_type == "top_artists":
                    api_method = "geo.getmetroartistchart"
                else:
                    raise Exception, "Valid scrape types are: top_tracks, top_artists"
                try:
                    params = tuple([api_method] + list(request_tup))
                    request = "http://ws.audioscrobbler.com/2.0/?method=%s&format=json&country=%s&metro=%s&start=%d&end=%d" % params
                except:
                    print params
                    raise Exception
                request = request + "&api_key="+API_KEY + "&page=" + str(page_no)
                print str(current_request_no) + "/" + str(total_request_tups) + ": " + request
                cookie = {"country": request_tup[0],
                          "city": request_tup[1],
                          "start": request_tup[2],
                          "end": request_tup[3],
                          "page": page_no,
                          "type": chart_type,
                          "project_root": project_root}
                try:
                    parallel_curl.startrequest(request, on_request_done_save, cookie)
                except TypeError:
                    parallel_curl.startrequest(request.encode("utf-8"), on_request_done_save, cookie)
            else:
                pass
            if (current_request_no % 5000) == 0:
                print str(current_request_no) + " of " + str(total_request_tups) + " complete."
            current_request_no += 1

def scrape_all_charts(project_root, request_tups=None):
    for scrape_type in SCRAPE_TYPES:
        get_chart(scrape_type, project_root, request_tups=request_tups)
        
