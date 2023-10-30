import json
import os

import jsonschema


def parse_string(s):
    i = s.find('"', s.find('"', s.find('"') + 1) + 1)
    while i != -1:
        j = s.find('",', i + 1)
        if j == -1:
            j = s.find('"\n', i + 1)
        s = s[: i + 1] + s[i + 1 : j].replace('"', "'") + s[j:]
        i = s.find('"', j + 1)

    return s.replace("\\", "\\\\")


with open("data/featuring_responses.jsonl", "r") as f:
    response = list(f)


jobs = []
features = []


for object_id, object in enumerate(response):
    print(f"{object_id + 1}/{len(response)}")
    object = json.loads(object)

    if object[1]["choices"][0]["finish_reason"] != "stop":
        object[0]["metadata"] = object[2]
        jobs.append(object[0])
    else:
        try:
            schema = {
                "type": "object",
                "properties": {
                    "ai_and_ml_features": {"type": "array", "items": {"type": "string"}}
                },
            }

            summary = json.loads(
                parse_string(object[1]["choices"][0]["message"]["content"].strip())
            )

            jsonschema.validate(summary, schema)

            features.append((summary["ai_and_ml_features"], object[2]))
        except Exception as e:
            print(object[1]["choices"][0]["message"]["content"].strip())
            print(parse_string(object[1]["choices"][0]["message"]["content"].strip()))
            print(object[2])
            print(repr(e))
            print()

            object[0]["metadata"] = object[2]
            jobs.append(object[0])


with open("data/new_featuring_requests.jsonl", "w") as f:
    for job in jobs:
        json_string = json.dumps(job)
        f.write(json_string + "\n")


files = os.listdir("data/base")


for file_id, file_name in enumerate(files):
    print(f"{file_name}: {file_id+1}/{len(files)}")

    with open(f"data/base/{file_name}", "r") as f:
        papers = json.load(f)

    for paper_id, paper in enumerate(papers):
        print(f"{paper_id + 1}/{len(papers)}")

        if "features" not in paper or len(paper["features"]) == 0:
            for feature in features:
                if (
                    feature[1]["file_id"] == file_name
                    and feature[1]["paper_id"] == paper_id
                ):
                    paper["features"] = feature[0]
                    break

    with open(f"data/base/{file_name}", "w") as f:
        json.dump(papers, f, indent=4)
