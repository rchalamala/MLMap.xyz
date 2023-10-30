import json
import os

files = os.listdir("data/base")
files.sort()

for file_id, file_name in enumerate(files):
    print(f"{file_name}: {file_id+1}/{len(files)}")

    with open(f"data/base/{file_name}", "r") as f:
        papers = json.load(f)

    for idx, paper in enumerate(papers):
        print(f"{idx + 1}/{len(papers)}")

        paper.pop("features", None)

    with open(f"data/base/{file_name}", "w") as f:
        json.dump(papers, f, indent=4)
