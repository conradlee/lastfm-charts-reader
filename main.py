import os
from scrapers import scrape_all, get_times, scrape_tags, scrape_metros

def scrape(project_root):
    # Scrape data and record in sub-directory raw_downloaded/
    request_tups = get_times.get_times(project_root)
    scrape_metros.scrape_all_charts(project_root, request_tups)
    print "Done scraping charts data from lastfm, now parsing it"
    # Parse data into CSVs and record in sub-directory parsed/
    scrape_all.write_metros(request_tups, project_root)
    print "Done parsing data into csv files, now scraping tags"
    # Scrape to discover which songs and artists belong to the most popular tags
    tags_charts = scrape_tags.scrape_tags_charts(project_root)
    print "Done scraping tags"
    # Save tags charts in pickle
    cached_dir = project_root + "cached/"
    if not os.path.isdir(cached_dir):
        os.makedirs(cached_dir)
    with open(cached_dir + "music_by_tags.pickle", "w") as f:
        pickle.dump(tags_charts, f)

if __name__ == "__main__":
    project_root = os.getcwd() + "/"
    scrape(project_root)
