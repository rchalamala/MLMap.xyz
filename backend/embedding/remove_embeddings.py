import json
import os

files = os.listdir("data/embedded")

for file_id, file_name in enumerate(files):
    print(f"{file_name}: {file_id+1}/{len(files)}")

    if not file_name.startswith("acl_201"):
        continue

    with open(f"data/embedded/{file_name}", "r") as f:
        papers = json.load(f)

    for paper_id, paper in enumerate(papers):
        print(f"{paper_id + 1}/{len(papers)}")

        paper.pop("embeddings", None)

    with open(f"data/embedded/{file_name}", "w") as f:
        json.dump(papers, f, indent=4)
