# import os
# from pathlib import Path
from typing import TypedDict

import client_side_pb2
from common import stub, volume

from modal import Image, Mount, Secret, method


class Paper(TypedDict):
    title: str
    abstract: str
    published_location: str
    published_location_code: str
    published_location_year: int
    authors: list[str]
    external_links: list[dict[str, str]]
    features: list[str]
    embeddings: list[list[float]]
    hash: int


image = (
    Image.debian_slim(python_version="3.10")
    .apt_install(
        "libfftw3-dev",
        "libomp-dev",
        "zstd",
    )
    .pip_install(
        "rapidfuzz",
        "numpy",
        "openai",
        "umap-learn",
    )
)


@stub.function(network_file_systems={"/shared": volume})
def remove_locks():
    print("Removing locks")

    import os

    files = os.listdir("/shared")

    for file_name in files:
        if file_name.endswith(".lock"):
            os.remove(f"/shared/{file_name}")


@stub.function(network_file_systems={"/shared": volume})
def remove_protobuf():
    print("Removing protobuf")

    import os

    try:
        os.remove("/shared/client_side.protobuf")
    except FileNotFoundError:
        pass


@stub.function(network_file_systems={"/shared": volume})
def remove_knn():
    print("Removing KNN")

    import os

    try:
        os.remove("/shared/knn.pkl")
    except FileNotFoundError:
        pass


@stub.function(network_file_systems={"/shared": volume})
def remove_embeddings():
    print("Removing embeddings")

    import os

    try:
        os.remove("/shared/embedding.pkl")
    except FileNotFoundError:
        pass

    try:
        os.remove("/shared/client_side.protobuf")
    except FileNotFoundError:
        pass


@stub.function(network_file_systems={"/shared": volume})
def remove_non_data():
    print("Removing non-data")

    import os

    files = os.listdir("/shared")

    for file_name in files:
        if not file_name.startswith("embedded"):
            os.remove(f"/shared/{file_name}")


@stub.function()
def process_paper(paper):
    import numpy as np

    new_paper = {
        k: v for k, v in paper.items() if k not in ["embeddings", "features", "hash"]
    }

    return (
        np.array(paper["embeddings"]),
        np.full(len(paper["features"]), paper["published_location_code"]),
        np.array(paper["features"]),
        np.full(len(paper["features"]), paper["published_location_year"]),
        np.full(len(paper["features"]), paper["hash"]),
        {paper["hash"]: new_paper},
    )


@stub.function(network_file_systems={"/shared": volume}, timeout=1200)
def process_file(file_name):
    import json

    import numpy as np

    with open(f"/shared/embedded/{file_name}", "r") as f:
        papers: list[Paper] = json.load(f)

    results = list(process_paper.map(papers))

    return (
        np.concatenate([result[0] for result in results]),
        np.concatenate([result[1] for result in results]),
        np.concatenate([result[2] for result in results]),
        np.concatenate([result[3] for result in results]),
        np.concatenate([result[4] for result in results]),
        {k: v for result in results for k, v in result[5].items()},
    )


@stub.function(image=image, secret=Secret.from_name("mlmap-openai-api-key"))
def process_abstract(abstract: str):
    import json

    import jsonschema
    import numpy as np
    import openai

    def parse_string(s):
        i = s.find('"', s.find('"', s.find('"') + 1) + 1)
        while i != -1:
            j = s.find('",', i + 1)
            if j == -1:
                j = s.find('"\n', i + 1)
            s = s[: i + 1] + s[i + 1 : j].replace('"', "'") + s[j:]
            i = s.find('"', j + 1)

        return s.replace("\\", "\\\\")

    schema = {
        "type": "object",
        "properties": {
            "ai_and_ml_features": {"type": "array", "items": {"type": "string"}}
        },
    }

    system = f"You are an expert who specializes in reading research papers and extracting key artificial intelligence (AI) and machine learning (ML) techniques, algorithms, features, and tasks. You always return results based on the following JSON schema:\n\n{json.dumps(schema, indent=4)}"

    user = f"Identify any key artificial intelligence (AI) and machine learning (ML) techniques, algorithms, features, and tasks present in the following research abstract: \n\n{abstract}\n\n Return the techniques, algorithms, features, and tasks in order of their prominence or significance as presented in the abstract. Return the results based on the following JSON schema:\n\n{json.dumps(schema, indent=4)}"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    features = None

    for _ in range(3):
        try:
            print("Trying feature extraction")

            response = (
                openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=150,
                    top_p=0.2,
                )
                .choices[0]
                .message.content.strip()
            )

            summary = json.loads(parse_string(response))

            jsonschema.validate(summary, schema)

            features = summary["ai_and_ml_features"]

            break

        except Exception as e:
            print(abstract)
            print(repr(e))
            print()

    if features is None:
        print("Failed to process abstract")
        return [], []

    for _ in range(3):
        try:
            print("Trying embedding extraction")

            embeddings = []

            for feature in features:
                response = (
                    openai.Embedding.create(
                        model="text-embedding-ada-002", input=feature + "\n"
                    )
                    .data[0]
                    .embedding
                )
                embeddings.append(np.array(response))

            if len(embeddings) == len(features):
                print("Processed abstract")
                return np.array(features), np.array(embeddings)

        except Exception as e:
            print(abstract)
            print(repr(e))
            print()

            print(response)
            print(parse_string(response))

    print("Failed to process abstract")
    return [], []


@stub.cls(
    image=image,
    # cpu=14,
    # memory=122880,
    network_file_systems={"/shared": volume},
    mounts=[
        # Mount.from_local_file(
        #   os.path.join(Path(__file__).parent.parent, "data/data.tar.zst"),
        #   remote_path="/data/data.tar.zst",
        # ),
        Mount.from_local_python_packages("client_side_pb2"),
    ],
    timeout=86400,
    container_idle_timeout=1200,
    keep_warm=1,
)
class Embedding:
    def __enter__(self):
        print("Embedding entered")

        import time

        start_time = time.time()

        """
        import os
        import subprocess
        from pathlib import Path

        import numpy as np
        import umap
        from umap.umap_ import nearest_neighbors

        years_map = {
            2013: 0,
            2014: 1,
            2015: 2,
            2016: 3,
            2017: 4,
            2018: 5,
            2019: 6,
            2020: 7,
            2021: 8,
            2022: 9,
            2023: 10,
        }

        conferences_map = {
            "ACL": 0,
            "CVPR": 1,
            "ICCV": 2,
            "ICML": 3,
            "NeurIPS": 4,
        }

        if not len(self.check_path(["extracting.lock"])):
            Path("/shared/extracting.lock").touch()

            if not len(self.check_path(["embedded"])):
                print("Data extracting")

                try:
                    subprocess.run(
                        [
                            "pzstd",
                            "/data/data.tar.zst",
                            "-o",
                            "/data/data.tar",
                            "-d",
                        ],
                        check=True,
                    )
                except Exception as e:
                    print(repr(e))
                    exit()

                print("Data extracted")

                print("Files extracting")

                try:
                    subprocess.run(
                        ["tar", "-xvf", "/data/data.tar", "-C", "/shared"],
                        check=True,
                    )
                except Exception as e:
                    print(repr(e))
                    exit()

                print("Files extracted")

            os.remove("/shared/extracting.lock")

        while len(self.check_path(["extracting.lock"])):
            print("Waiting for data and files extracting")
            time.sleep(5)

        if not len(self.check_path(["processing.lock"])):
            Path("/shared/processing.lock").touch()

            if not len(
                self.check_path(
                    [
                        "coordinates",
                        "conferences",
                        "features",
                        "years",
                        "hashes",
                        "papers",
                    ]
                )
            ):
                print("Data processing")

                files = os.listdir("/shared/embedded")

                results = list(process_file.map(files))

                self.coordinates = np.concatenate([result[0] for result in results])
                self.conferences = np.concatenate([result[1] for result in results])
                self.features = np.concatenate([result[2] for result in results])
                self.years = np.concatenate([result[3] for result in results])
                self.hashes = np.concatenate([result[4] for result in results])
                papers_dict = {k: v for result in results for k, v in result[5].items()}

                self.papers = [
                    papers_dict.get(paper_id, None)
                    for paper_id in range(len(papers_dict))
                ]

                print("Data processed")

                self.save_data(
                    [
                        "coordinates",
                        "conferences",
                        "features",
                        "years",
                        "hashes",
                        "papers",
                    ]
                )

            os.remove("/shared/processing.lock")

        while len(self.check_path(["processing.lock"])):
            print("Waiting for data processing")
            time.sleep(5)

        if not len(self.check_path(["knn.lock"])):
            Path("/shared/knn.lock").touch()

            if not len(self.check_path(["knn"])):
                print("KNN computing")

                self.load_data(["coordinates"])

                self.knn = nearest_neighbors(
                    self.coordinates,
                    n_neighbors=500,
                    metric="cosine",
                    metric_kwds={},
                    angular=True,
                    random_state=False,
                    verbose=True,
                )

                print("KNN computed")

                self.save_data(["knn"])

            os.remove("/shared/knn.lock")

        while len(self.check_path(["knn.lock"])):
            print("Waiting for KNN computing")
            time.sleep(5)

        if not len(self.check_path(["embedding.lock"])):
            Path("/shared/embedding.lock").touch()

            if not len(self.check_path(["embedding"])):
                print("Embedding computing")

                self.load_data(["coordinates", "knn"])

                self.embedding = umap.UMAP(
                    n_neighbors=300,
                    precomputed_knn=self.knn,
                    verbose=True,
                ).fit(self.coordinates)

                print("Embedding computed")

                self.save_data(["embedding"])

            os.remove("/shared/embedding.lock")

        while len(self.check_path(["embedding.lock"])):
            print("Waiting for embedding computing")
            time.sleep(5)

        if not len(self.check_path(["protobuf.lock"])):
            Path("/shared/protobuf.lock").touch()

            if not len(self.check_path(["client_side"])):
                print("protobuf generating")

                self.load_data(
                    ["embedding", "conferences", "features", "years", "hashes"]
                )

                self.client_side = client_side_pb2.Data()

                for conference_id in range(len(conferences_map)):
                    conference = client_side_pb2.Conference()

                    for year_id in range(len(years_map)):
                        conference.years.append(client_side_pb2.Year())

                    self.client_side.conferences.append(conference)

                for index in range(len(self.hashes)):
                    paper = client_side_pb2.Paper(
                        x=float(self.embedding.embedding_[index, 0]),
                        y=float(self.embedding.embedding_[index, 1]),
                        hash=int(self.hashes[index]),
                        feature=str(self.features[index]),
                    )

                    self.client_side.conferences[
                        conferences_map[self.conferences[index]]
                    ].years[years_map[self.years[index]]].papers.append(paper)

                self.save_data(["client_side"])

                self.client_side = self.client_side.SerializeToString()

                print("protobuf generated")

            os.remove("/shared/protobuf.lock")

        while len(self.check_path(["protobuf.lock"])):
            print("Waiting for protobuf generating")
            time.sleep(5)
        """

        self.load_data(["papers", "embedding"])

        print(f"Initialization done in {time.time() - start_time:.2f} seconds")

    @method()
    def check_path(self, fields: list[str]):
        import os

        extensions = {
            "coordinates": ".npy",
            "conferences": ".npy",
            "features": ".npy",
            "years": ".npy",
            "hashes": ".npy",
            "papers": ".json",
            "embedding": ".pkl",
            "knn": ".pkl",
            "client_side": ".protobuf",
        }

        return [
            field
            for field in fields
            if os.path.exists(f"/shared/{field}{extensions.get(field, '')}")
        ]

    @method()
    def check_data(self, fields: list[str]):
        return all(hasattr(self, field) for field in fields)

    @method()
    def load_data(self, fields: list[str]):
        print("Data fields loading")

        import json
        import pickle

        import numpy as np

        extensions = {
            "coordinates": ".npy",
            "conferences": ".npy",
            "features": ".npy",
            "years": ".npy",
            "hashes": ".npy",
            "papers": ".json",
            "embedding": ".pkl",
            "knn": ".pkl",
            "client_side": ".protobuf",
        }

        for field in fields:
            if not hasattr(self, field):
                print(f"{field}{extensions[field]} loading")

                if extensions[field] == ".npy":
                    setattr(self, field, np.load(f"/shared/{field}{extensions[field]}"))

                elif extensions[field] == ".json":  # specific to papers.json
                    setattr(
                        self,
                        field,
                        json.load(open(f"/shared/{field}{extensions[field]}", "r")),
                    )

                elif extensions[field] == ".pkl":
                    with open(f"/shared/{field}{extensions[field]}", "rb") as f:
                        setattr(self, field, pickle.load(f))

                elif extensions[field] == ".protobuf":
                    with open(f"/shared/{field}{extensions[field]}", "rb") as f:
                        setattr(self, field, f.read())

                print(f"{field}{extensions[field]} loaded")

        print("Data fields loaded")

    @method()
    def save_data(self, fields: list[str]):
        import json
        import pickle

        import numpy as np

        extensions = {
            "coordinates": ".npy",
            "conferences": ".npy",
            "features": ".npy",
            "years": ".npy",
            "hashes": ".npy",
            "papers": ".json",
            "embedding": ".pkl",
            "knn": ".pkl",
            "client_side": ".protobuf",
        }

        for field in fields:
            if hasattr(self, field):
                print(f"{field}{extensions[field]} saving")

                if extensions[field] == ".npy":
                    np.save(f"/shared/{field}{extensions[field]}", getattr(self, field))

                elif extensions[field] == ".json":  # specific to papers.json
                    with open(f"/shared/{field}{extensions[field]}", "w") as f:
                        json.dump(getattr(self, field), f)

                elif extensions[field] == ".pkl":
                    with open(f"/shared/{field}{extensions[field]}", "wb") as f:
                        pickle.dump(
                            getattr(self, field), f, protocol=pickle.HIGHEST_PROTOCOL
                        )

                elif extensions[field] == ".protobuf":
                    with open(f"/shared/{field}{extensions[field]}", "wb") as f:
                        f.write(getattr(self, field).SerializeToString())

                print(f"{field}{extensions[field]} saved")

    """
    @method()
    def get_data(self):
        self.load_data(["client_side"])
        return self.client_side
    """

    @method()
    def get_paper(self, paper_id: int):
        print("Paper loading")

        import json

        return json.dumps(self.papers[paper_id])

    @method()
    def post_search(self, search_term: str):
        import json

        from rapidfuzz import fuzz, utils

        matches = []

        processed_search_term = utils.default_process(search_term)

        for paper_hash, paper_data in enumerate(self.papers):
            fuzzy_score = max(
                [
                    fuzz.ratio(processed_search_term, author)
                    for author in paper_data["authors"]
                ]
                + [
                    fuzz.ratio(
                        processed_search_term,
                        utils.default_process(paper_data["title"]),
                    )
                ]
            )

            if fuzzy_score > 10:
                matches.append(
                    {
                        "score": fuzzy_score,
                        "paper_data": (paper_data["title"], paper_hash),
                    }
                )

        matches.sort(key=lambda x: x["score"], reverse=True)

        return json.dumps([match["paper_data"] for match in matches[:100]])

    @method()
    def get_points(self, abstract: str):
        print("Points loading")

        import json

        features, embeddings = process_abstract.call(abstract)

        return json.dumps(
            {
                "features": features.tolist(),
                "embeddings": self.embedding.transform(embeddings).tolist(),
            }
        )


@stub.local_entrypoint()
def main():
    remove_locks.call()
    # remove_knn.call()
    # remove_embeddings.call()
    # remove_non_data.call()
    # return

    embedding = Embedding()

    print("Embedding created")

    print(embedding.get_paper.call(100))
