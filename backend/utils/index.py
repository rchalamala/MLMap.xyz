import json
import os

files = os.listdir("data/embedded")


all_papers = {}


for file_id, file_name in enumerate(files):
    print(f"{file_name}: {file_id+1}/{len(files)}")

    with open(f"data/embedded/{file_name}", "r") as f:
        papers = json.load(f)

    for paper_id, paper in enumerate(papers):
        print(f"{paper_id + 1}/{len(papers)}")

        hash_value = paper.pop("hash")

        assert hash_value not in all_papers, f"{paper}\n{all_papers[hash_value]}"

        all_papers[hash_value] = paper


with open("data/paper_dict.json", "w") as f:
    json.dump(all_papers, f)
