import json
import os

files = os.listdir("data/embedded")


for file_id, file_name in enumerate(files):
    print(f"{file_name}: {file_id+1}/{len(files)}")

    with open(f"data/embedded/{file_name}", "r") as f:
        papers = json.load(f)

    for paper_id, paper in enumerate(papers):
        print(f"{paper_id + 1}/{len(papers)}")

        if len(paper["features"]) != len(paper["embeddings"]):
            print(
                file_name,
                f"{paper_id + 1}/{len(papers)}",
                f"{len(paper['features'])} != {len(paper['embeddings'])}",
            )
            exit()

        if len(paper["features"]) == 0:
            print(
                file_name,
                f"{paper_id + 1}/{len(papers)}",
                f"{len(paper['features'])} == 0",
            )
            exit()

        embedding_lengths = [len(embedding) for embedding in paper["embeddings"]]

        if len(set(embedding_lengths)) != 1 or embedding_lengths[0] != 1536:
            print(file_name, f"{paper_id + 1}/{len(papers)}", f"{embedding_lengths}")
            exit()
