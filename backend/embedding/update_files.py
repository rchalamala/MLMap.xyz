import json
import os
import sys

files = os.listdir("data/base")


file_dict = {file_name: file_id for file_id, file_name in enumerate(files)}


def get_embeddings():
    with open("data/embedding_responses.jsonl", "r") as f:
        response = list(f)

    with open("data/embedding_requests.jsonl", "r") as f:
        requests = list(f)

    # change file_name to file_id (doesn't really matter what file_id is, as long as it's unique and small)

    base = 23523

    def get_hash(metadata):
        return (
            file_dict[metadata["file_id"]] * base * base
            + metadata["paper_id"] * base
            + metadata["feature_id"]
        )

    def symmetric_difference(list1, list2):
        set1 = set(list1)
        set2 = set(list2)
        return sorted(list(set1.symmetric_difference(set2)))

    request_hashes = [get_hash(json.loads(request)["metadata"]) for request in requests]
    response_hashes = []

    jobs = []
    embeddings = []

    for object_id, object in enumerate(response):
        print(f"{object_id + 1}/{len(response)}")
        object = json.loads(object)

        try:
            embeddings.append((object[1]["data"][0]["embedding"], object[2]))

            response_hashes.append(get_hash(object[2]))

            for job_id, job in enumerate(jobs):
                if job["metadata"] == object[2]:
                    del jobs[job_id]
                    break

        except Exception as e:
            print(object)
            print(repr(e))
            print()

            object[0]["metadata"] = object[2]
            jobs.append(object[0])
            response_hashes.append(get_hash(object[2]))

    needed = symmetric_difference(request_hashes, response_hashes)

    for request in requests:
        if get_hash(json.loads(request)["metadata"]) in needed:
            jobs.append(json.loads(request))

    with open("data/new_embedding_requests.jsonl", "w") as f:
        for job in jobs:
            json_string = json.dumps(job)
            f.write(json_string + "\n")

    return embeddings, len(jobs)


embeddings, job_count = get_embeddings()

assert job_count == 0, f"{job_count} jobs left"

for file_id, file_name in enumerate(files):
    print(f"{file_name}: {file_id+1}/{len(files)}")

    with open(f"data/embedded/{file_name}", "r") as f:
        papers = json.load(f)

    for paper_id, paper in enumerate(papers):
        print(f"{paper_id + 1}/{len(papers)}")

        if "embeddings" not in paper:
            paper["embeddings"] = []

            for feature_id, feature in enumerate(paper["features"]):
                for embedding in embeddings:
                    if (
                        embedding[1]["file_id"] == file_name
                        and embedding[1]["paper_id"] == paper_id
                        and embedding[1]["feature_id"] == feature_id
                    ):
                        paper["embeddings"].append(embedding[0])
                        break

    with open(f"data/embedded/{file_name}", "w") as f:
        json.dump(papers, f, indent=4)
