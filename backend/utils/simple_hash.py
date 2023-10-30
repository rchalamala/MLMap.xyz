import json
import os

files = os.listdir("data/embedded")


hash_id = 0


for file_id, file_name in enumerate(files):
    print(f"{file_name}: {file_id+1}/{len(files)}")

    with open(f"data/embedded/{file_name}", "r") as f:
        papers = json.load(f)

    for paper_id, paper in enumerate(papers):
        print(f"{paper_id + 1}/{len(papers)}")

        paper["hash"] = hash_id

        hash_id += 1

    with open(f"data/embedded/{file_name}", "w") as f:
        json.dump(papers, f, indent=4)
