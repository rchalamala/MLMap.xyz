import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

# desired_year = 2022
desired_year = int(sys.argv[1])
print("Desired year: " + str(desired_year))

complete_json_obj = None
parent_directory = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + "/data/base/"
json_storage_path = parent_directory + "cvpr_" + str(desired_year) + "_papers.json"

cvpr_base_urls = {
    2023: ["https://openaccess.thecvf.com/CVPR2023?day=all"],
    2022: ["https://openaccess.thecvf.com/CVPR2022?day=all"],
    2021: ["https://openaccess.thecvf.com/CVPR2021?day=all"],
    2020: [
        "https://openaccess.thecvf.com/CVPR2020?day=2020-06-16",
        "https://openaccess.thecvf.com/CVPR2020?day=2020-06-17",
        "https://openaccess.thecvf.com/CVPR2020?day=2020-06-18",
    ],
    2019: [
        "https://openaccess.thecvf.com/CVPR2019?day=2019-06-18",
        "https://openaccess.thecvf.com/CVPR2019?day=2019-06-19",
        "https://openaccess.thecvf.com/CVPR2019?day=2019-06-20",
    ],
    2018: [
        "https://openaccess.thecvf.com/CVPR2018?day=2018-06-19",
        "https://openaccess.thecvf.com/CVPR2018?day=2018-06-20",
        "https://openaccess.thecvf.com/CVPR2018?day=2018-06-21",
    ],
    2017: [],
    2016: [],
    2015: [],
    2014: [],
    2013: [],
}

base_cvpr_url = cvpr_base_urls[desired_year]
print(base_cvpr_url)


def getAllPaperUrls(url):
    try:
        # send request to the webpage
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request was not successful

        # parse the HTML content of the webpage
        soup = BeautifulSoup(response.text, "html.parser")

        # find all the paper entries on the webpage
        paper_entries = soup.find_all("dt", class_="ptitle")

        # scrape links for each paper entry
        papers = []
        for entry in paper_entries:
            links = entry.find_all("a")
            desired_url = links[0]["href"]
            if desired_year < 2021:
                desired_url = "https://openaccess.thecvf.com/" + str(desired_url)
            else:
                desired_url = "https://openaccess.thecvf.com" + str(desired_url)
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
        title = soup.find_all("div", id="papertitle")[0].getText()
        title = title.replace("\n", "").strip()
        print(
            "- Scraping ("
            + str(counter)
            + "/"
            + str(total_entries)
            + "): "
            + str(title)
        )

        abstract_text = soup.find("div", id="abstract").text
        abstract_text = abstract_text.replace("\n", "").strip()

        authors_raw = soup.find("div", id="authors").text
        authors = authors_raw.split(";")[0].strip()
        authors = [item.strip() for item in authors.split(",")]
        authors_dict = []
        for a in authors:
            temp = {"author_name": str(a), "affiliations": ["unknown"]}
            authors_dict.append(temp)

        publication_location = authors_raw.split(";")[1].strip()
        publication_location = publication_location.replace("\n", "").strip()

        # get links to extra stuff
        if desired_year < 2021:
            extras = soup.find_all("dd")[0].find_all("a")
        else:
            extras = soup.find_all("dd")[1].find_all("a")

        extra_links = []
        for extra in extras:
            if extra.get("class") and extra.get("class")[0] == "fakelink":
                continue
            link_text = extra.text
            href = extra["href"]
            if link_text != "arXiv":
                if desired_year < 2021:
                    href = "https://openaccess.thecvf.com/" + str(href)
                else:
                    href = "https://openaccess.thecvf.com" + str(href)
            extra_links.append({"href_text": link_text, "href": href})

        # paper representation
        paper = {
            "title": str(title),
            "abstract": str(abstract_text),
            "published_location": str(publication_location),
            "published_location_code": str("CVPR"),
            "published_location_year": desired_year,
            "authors": authors,
            "external_links": extra_links,
        }
        json_obj = json.dumps(paper)

        return paper
    except (
        requests.exceptions.RequestException,
        ValueError,
        KeyError,
        IndexError,
    ) as err:
        print(f"An error occurred: {err}")
        return {}


paper_urls = []
for x in base_cvpr_url:
    paper_urls = paper_urls + getAllPaperUrls(x)
total_entries = len(paper_urls)

print(total_entries)

print(scrapePaper(paper_urls[0], total_entries, 1))


papers = []
counter = 0
for p in paper_urls:
    p_metadata = scrapePaper(p, total_entries, counter + 1)
    papers.append(p_metadata)
    counter = counter + 1

# save json obj to file
with open(json_storage_path, "w") as json_file:
    json.dump(papers, json_file, indent=4)
