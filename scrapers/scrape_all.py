import simplejson
import os, sys
from datetime import datetime
import csv
import time
import pycurl


# Global variables -- these are used in all scraping scripts

API_KEY = ""     # REQUIRED - Fill this in
API_SECRET = ""  # REQUIRED - Fill this in  
USERNAME = ""    # REQUIRED - Fill this in

MAX_REQUESTS = 4
SCRAPE_TYPES = ["top_tracks", "top_artists"]
CURL_OPTIONS = {
    pycurl.SSL_VERIFYPEER: False,
    pycurl.SSL_VERIFYHOST: False,
    pycurl.USERAGENT: 'Identify yourself to lastfm with a message here (optional)',
    pycurl.FOLLOWLOCATION: True,
}
# End global variables

import scrape_tags
import get_times
import scrape_metros

def write_metros(request_tups, project_root):
    for scrape_type in SCRAPE_TYPES:
        for country, city, start_unixtime, end_unixtime in request_tups:
            start_time = datetime.fromtimestamp(start_unixtime)
            end_time = datetime.fromtimestamp(end_unixtime)
            rank_dict = {}
            parse_problem = False
            # Make sure write directory exists.  If outfile already exists, terminate
            out_dir = "/".join([project_root.rstrip("/"), "parsed", "charts", scrape_type, country + "_" + city])
            week_no = int(time.strftime("%U", start_time.timetuple()))
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir)
            write_filename = "%s/%d_%d_%d.csv" % (out_dir, start_time.year, week_no, start_unixtime)
            if os.path.isfile(write_filename):
                return
            
            # Read all ten pages for the week
            for page_no in range(1,11):
                filename = project_root + "raw_downloaded/"+scrape_type+"/"+country+"/"+city+"/" + str(start_unixtime) + "-" + str(end_unixtime) + "_page-" + str(page_no) + ".json"
                if not os.path.isfile(filename):
                    print "Warning---expected file does not exist:" + filename
                else:
                    # Parse json and check for errors
                    try:
                        json_dict = simplejson.loads(open(filename).read().strip())
                    except:
                        os.system("rm " + filename)
                        print "Could not parse " + filename
                        parse_problem = True
                        break
                    if scrape_type == "top_tracks":
                        try:
                            if json_dict["toptracks"].has_key("totalPages"):
                                if int(json_dict["toptracks"]["totalPages"]) < page_no:
                                    continue
                            else:
                                rank_list = json_dict["toptracks"]["track"]
                        except Exception, e:
                            parse_problem = True
                            print "Exception %s while parsing %s" % (str(e), str(json_dict))
                            break
                    elif scrape_type == "top_artists":
                        try:
                            if json_dict["topartists"].has_key("totalPages"):
                                if int(json_dict["topartists"]["totalPages"]) < page_no:
                                    continue
                            else:
                                rank_list = json_dict["topartists"]["artist"]
                        except Exception, e:
                            parse_problem = True
                            print "Exception %s while parsing %s" % (str(e), str(json_dict))
                            break
                    else:
                        raise ValueError, "Accepted scrape types are " + " ".join(scrape_types)
                    if type(rank_list) != list:
                        rank_list = [rank_list]
                        
                    for item in rank_list:
                        rank = int(item["@attr"]["rank"])
                        name = item["name"]
                        mbid = item["mbid"]
                        url = item["url"]
                        num_listeners = int(item["listeners"])
                        rank_dict[rank] = {"rank": rank, "name": name, "mbid": mbid, "num_listeners": num_listeners, "url": url}
                        if scrape_type == "top_tracks":
                            rank_dict[rank]["artist"] = item["artist"]["name"]
                            rank_dict[rank]["artist_mbid"] = item["artist"]["mbid"]
                            rank_dict[rank]["artist_url"] = item["artist"]["url"]
                            
            # Write results
            if parse_problem:
                print "\tParsing problem prevents creation of %s" % write_filename
                continue

            write_file = open(write_filename, "wb")
            csv_writer = csv.writer(write_file, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
            for rank in sorted(rank_dict.keys()):
                i = rank_dict[rank]
                if scrape_type == "top_tracks":
                    attributes = [str(i["rank"]), str(i["num_listeners"]), i["name"], i["artist"], i["url"], i["artist_url"]]
                elif scrape_type == "top_artists":
                    attributes = [str(i["rank"]), str(i["num_listeners"]), i["name"], i["mbid"], i["url"]]
                encoded_attributes = []
                for index, val in enumerate(attributes):
                    if type(val) == unicode:
                        val = val.encode("utf8")
                    encoded_attributes.append(val)
                csv_writer.writerow(encoded_attributes)
            write_file.close()
            print "\tSuccessfully created file %s" % write_filename

def main(project_root):
    request_tups = get_times.get_times(project_root)
    scrape_metros.scrape_all_charts(project_root, request_tups)
    write_metros(request_tups, project_root)
    tags_charts = scrape_tags.scrape_tags_charts(project_root)
