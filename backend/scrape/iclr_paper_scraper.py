import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

desired_year = int(sys.argv[1])
print("Desired year: " + str(desired_year))

complete_json_obj = None
parent_directory = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + "/data/base/"
json_storage_path = parent_directory + "icml_" + str(desired_year) + "_papers.json"

# figured out how to locate volume #s from Github repos (https://github.com/mlresearch) - allows circumventing of
# restricted access to papers on the ICML website for current and upcoming conferences
plmr_access_codes = {
    2023: "v202",
    2022: "v162",
    2021: "v139",
    2020: "v119",
    2019: "v97",
    2018: "v80",
    2017: "v70",
    2016: "v48",
    2015: "v37",
    2014: "v32",
    2013: "v28",
}

base_plmr_url = (
    "https://proceedings.mlr.press/" + str(plmr_access_codes[desired_year]) + "/"
)
print(base_plmr_url)


def getAllPaperUrls(url):
    try:
        # send request to the webpage
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request was not successful

        # parse the HTML content of the webpage
        soup = BeautifulSoup(response.text, "html.parser")

        # find all the paper entries on the webpage
        paper_entries = soup.find_all("div", class_="paper")

        # scrape links for each paper entry
        papers = []
        for entry in paper_entries:
            links = entry.find_all("a")
            desired_url = links[0]["href"]
            papers.append(desired_url)

        return papers
    except (requests.exceptions.RequestException, ValueError, KeyError) as err:
        print(f"An error occurred: {err}")
        return []


def scrapePaper(url, total_entries, counter):
    try:
        # send request to the webpage
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request was not successful

        # parse the HTML content of the webpage
        soup = BeautifulSoup(response.text, "html.parser")

        # find all relevant metadata on the webpage
        title = soup.find_all("h1")[0].getText().strip()
        print(
            "- Scraping ("
            + str(counter)
            + "/"
            + str(total_entries)
            + "): "
            + str(title)
        )

        abstract_text = soup.find_all("div", class_="abstract")[0].getText()
        abstract_text = abstract_text.replace("\n", "").strip()

        authors = soup.find_all("span", class_="authors")[0].getText()
        authors = [item.strip() for item in authors.split(",")]
        authors_dict = []
        for a in authors:
            temp = {"author_name": str(a), "affiliations": ["unknown"]}
            authors_dict.append(temp)

        publication_location = (
            soup.find_all("div", id="info")[0].getText().strip().replace("\u00a0", "")
        )

        # get links to extra stuff
        extras = soup.find_all("div", id="extras")[0].find("ul").find_all("a")

        extra_links = []
        for extra in extras:
            link_text = extra.text.strip()
            href = extra["href"]
            extra_links.append({"href_text": link_text, "href": href})

        # paper representation
        paper = {
            "title": str(title),
            "abstract": str(abstract_text),
            "published_location": str(publication_location),
            "published_location_code": str("ICML"),
            "published_location_year": desired_year,
            "authors": authors,
            "external_links": extra_links,
        }
        json_obj = json.dumps(paper)

        return paper
    except (requests.exceptions.RequestException, ValueError, KeyError) as err:
        print(f"An error occurred: {err}")
        return []


paper_urls = getAllPaperUrls(base_plmr_url)

total_entries = len(paper_urls)

papers = []
counter = 0
for p in paper_urls:
    p_metadata = scrapePaper(p, total_entries, counter)
    papers.append(p_metadata)
    counter = counter + 1

# save json obj to file
with open(json_storage_path, "w") as json_file:
    json.dump(papers, json_file, indent=4)
