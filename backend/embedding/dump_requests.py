import json
import os

files = os.listdir("data/base")
files.sort()

jobs = []

for file_id, file_name in enumerate(files):
    print(f"{file_name}: {file_id+1}/{len(files)}")

    with open(f"data/embedded/{file_name}", "r") as f:
        papers = json.load(f)

    for paper_id, paper in enumerate(papers):
        print(f"{paper_id + 1}/{len(papers)}")

        if "features" in paper:
            if "embeddings" not in paper:
                for feature_id, feature in enumerate(paper["features"]):
                    jobs.append(
                        {
                            "model": "text-embedding-ada-002",
                            "input": feature + "\n",
                            "metadata": {
                                "file_id": file_name,
                                "paper_id": paper_id,
                                "feature_id": feature_id,
                            },
                        }
                    )

with open("data/embedding_requests.jsonl", "w") as f:
    for job in jobs:
        json_string = json.dumps(job)
        f.write(json_string + "\n")
