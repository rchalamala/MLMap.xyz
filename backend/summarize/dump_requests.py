import json
import os

schema = {
    "type": "object",
    "properties": {
        "ai_and_ml_features": {"type": "array", "items": {"type": "string"}}
    },
}

system = f"You are an expert who specializes in reading research papers and extracting key artificial intelligence (AI) and machine learning (ML) techniques, algorithms, features, and tasks. You always return results based on the following JSON schema:\n\n{json.dumps(schema, indent=4)}"


files = os.listdir("data/base")
files.sort()


jobs = []


for file_id, file_name in enumerate(files):
    print(f"{file_name}: {file_id+1}/{len(files)}")

    with open(f"data/base/{file_name}", "r") as f:
        papers = json.load(f)

    for paper_id, paper in enumerate(papers):
        print(f"{paper_id + 1}/{len(papers)}")

        if "features" not in paper or len(paper["features"]) == 0:
            user = f"Identify any key artificial intelligence (AI) and machine learning (ML) techniques, algorithms, features, and tasks present in the following research abstract: \n\n{paper['abstract']}\n\n Return the techniques, algorithms, features, and tasks in order of their prominence or significance as presented in the abstract. Return the results based on the following JSON schema:\n\n{json.dumps(schema, indent=4)}"

            jobs.append(
                {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "metadata": {
                        "file_id": file_name,
                        "paper_id": paper_id,
                    },
                    "top_p": 0.2,
                }
            )


with open("data/featuring_requests.jsonl", "w") as f:
    for job in jobs:
        json_string = json.dumps(job)
        f.write(json_string + "\n")
