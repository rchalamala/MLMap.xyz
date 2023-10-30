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
parent_directory = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + "/data/"
json_storage_path = parent_directory + "acl_" + str(desired_year) + "_papers.json"

acl_base_urls = {
    2023: [
        "https://aclanthology.org/2023.acl-long.?/",
        "https://aclanthology.org/2023.acl-short.?/",
    ],
    2022: [
        "https://aclanthology.org/2022.acl-long.?/",
        "https://aclanthology.org/2022.acl-short.?/",
    ],
    2021: [
        "https://aclanthology.org/2021.acl-long.?/",
        "https://aclanthology.org/2021.acl-short.?/",
    ],
    2020: ["https://aclanthology.org/2020.acl-main.?/"],
}

base_acl_url = acl_base_urls[desired_year]
print(base_acl_url)


def scrapePaper(url, counter):
    try:
        # send request to the webpage
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request was not successful

        # parse the HTML content of the webpage
        soup = BeautifulSoup(response.text, "html.parser")

        # check if 404 not found --> all papers for url have been scraped
        indicator = soup.find_all("div", class_="alert alert-danger")
        if len(indicator) > 0:
            return "retracted_paper"

        # find all relevant metadata on the webpage
        title = soup.find_all("h2", id="title")[0].getText()
        title = title.replace("\n", "").strip()
        print("- Scraping (" + str(counter) + "): " + str(title))

        abstract_text = (
            soup.find("div", class_="card-body acl-abstract").find("span").text
        )
        abstract_text = abstract_text.replace("\n", "").strip()

        authors_raw = soup.find("p", class_="lead").text
        authors = authors_raw
        authors = [item.strip() for item in authors.split(",")]
        authors_dict = []
        for a in authors:
            temp = {"author_name": str(a), "affiliations": ["unknown"]}
            authors_dict.append(temp)

        publication_location = soup.find_all("span", id="citeACL")[0].text
        publication_location = publication_location[
            (publication_location.find("Proceedings")) :
        ]
        publication_location = publication_location.replace("\n", "").strip()

        extra_links = []
        extra_links.append(
            # FIXME: should be in same format as other scrapers (with href_text and stuff)
            {"PDF": str(soup.find_all("h2", id="title")[0].find("a")["href"])}
        )

        # paper representation
        paper = {
            "title": str(title),
            "abstract": str(abstract_text),
            "published_location": str(publication_location),
            "published_location_code": str("ACL"),
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
        return None


papers = []
counter = 1
for x in base_acl_url:
    counter = 1
    while True:
        p_metadata = scrapePaper(x.replace("?", str(counter)), counter)
        if p_metadata == "retracted_paper":
            counter = counter + 1
            continue
        if p_metadata == None:
            # done scraping this url
            break
        else:
            papers.append(p_metadata)
        counter = counter + 1


# save json obj to file
with open(json_storage_path, "w") as json_file:
    json.dump(papers, json_file, indent=4)
