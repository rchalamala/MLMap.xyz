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
json_storage_path = parent_directory + "neurips_" + str(desired_year) + "_papers.json"

base_nips_url = "https://papers.nips.cc/paper_files/paper/" + str(desired_year)
print(base_nips_url)


def getAllPaperUrls(url):
    try:
        # send request to the webpage
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request was not successful

        # parse the HTML content of the webpage
        soup = BeautifulSoup(response.text, "html.parser")

        # find all the paper entries on the webpage
        if desired_year > 2021:
            paper_entries = soup.find_all("li", class_="conference")
        else:
            paper_entries = soup.find_all(
                "li", class_="none"
            )  # class is 'conference' only for 2022+, but 'none' otherwise

        # scrape links for each paper entry
        papers = []
        for entry in paper_entries:
            links = entry.find_all("a")
            desired_url = links[0]["href"]
            desired_url = "https://papers.nips.cc" + str(desired_url)
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
        title = soup.find_all("h4")[0].getText()
        title = title.replace("\n", "").strip()
        print(
            "- Scraping ("
            + str(counter)
            + "/"
            + str(total_entries)
            + "): "
            + str(title)
        )

        p_tags = soup.find_all("p")

        abstract_text = p_tags[2].getText()
        abstract_text = abstract_text.replace("\n", "").strip()

        authors = p_tags[1].getText()
        authors = [item.strip() for item in authors.split(",")]
        authors_dict = []
        for a in authors:
            temp = {"author_name": str(a), "affiliations": ["unknown"]}
            authors_dict.append(temp)

        publication_location = p_tags[0].getText()
        publication_location = publication_location.replace("\n", "").strip()

        # get links to extra stuff
        extras = soup.find_all("a", class_="btn")

        extra_links = []
        for extra in extras:
            link_text = extra.text
            href = extra["href"]
            href = "https://papers.nips.cc" + str(href)
            extra_links.append({"href_text": link_text, "href": href})

        # paper representation
        paper = {
            "title": str(title),
            "abstract": str(abstract_text),
            "published_location": str(publication_location),
            "published_location_code": str("NeurIPS"),
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


paper_urls = getAllPaperUrls(base_nips_url)
total_entries = len(paper_urls)

print(total_entries)

papers = []
counter = 0
for p in paper_urls:
    p_metadata = scrapePaper(p, total_entries, counter)
    papers.append(p_metadata)
    counter = counter + 1

# save json obj to file
with open(json_storage_path, "w") as json_file:
    json.dump(papers, json_file, indent=4)
