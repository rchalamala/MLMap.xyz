import json
import os
import re

import numpy as np

pattern = re.compile("[^a-zA-Z0-9]")
PRIME = 8030600951575441
POWER_MULTIPLIER = 37
powers = [1]


for _ in range(256):
    powers.append((POWER_MULTIPLIER * powers[-1]) % PRIME)


powers = np.array(powers)


def get_hash(paper):
    pattern = re.compile("[^a-zA-Z0-9]")

    target = re.sub(
        pattern,
        "",
        f"{paper['title']}{paper['published_location_code']}{paper['published_location_year']}",
    ).lower()

    hash_value = 0

    for c_id, c in enumerate(target):
        if c.isalpha():
            value = ord(c) - 97
        elif c.isnumeric():
            value = ord(c) - 48
        else:
            assert False, c

        hash_value += value * powers[c_id]
        hash_value %= PRIME

    return int(hash_value)


files = os.listdir("data/embedded")


used = set()


for file_id, file_name in enumerate(files):
    print(f"{file_name}: {file_id+1}/{len(files)}")

    with open(f"data/embedded/{file_name}", "r") as f:
        papers = json.load(f)

    for paper_id, paper in enumerate(papers):
        print(f"{paper_id + 1}/{len(papers)}")

        paper["hash"] = get_hash(paper)

        if paper["hash"] in used:
            print("hash collision")
            assert False

        used.add(paper["hash"])

    with open(f"data/embedded/{file_name}", "w") as f:
        json.dump(papers, f, indent=4)
