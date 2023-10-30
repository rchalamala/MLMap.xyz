from common import stub

import embedding
from modal import Mount, asgi_app


@stub.function(
    mounts=[
        Mount.from_local_python_packages("embedding"),
    ],
    container_idle_timeout=1200,
    timeout=2400,
)
@asgi_app()
def api():
    """Web API for interacting with the modal daemon."""
    from fastapi import FastAPI, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import Response

    app = FastAPI()
    data_embedding = embedding.Embedding()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    """
    @app.get("/api/get_data")
    async def get_data():
        return Response(
            data_embedding.get_data.call(), media_type="application/x-protobuf"
        )
    """

    @app.post("/api/search")
    async def post_search(request: Request):
        body = await request.json()

        return Response(
            data_embedding.post_search.call(body["searchTerm"]),
            media_type="application/json",
        )

    @app.post("/api/abstract")
    async def post_abstract(request: Request):
        body = await request.json()

        return Response(
            data_embedding.get_points.call(body["abstract"]),
            media_type="application/json",
        )

    @app.get("/api/get_paper/{paper_id}")
    async def get_paper(paper_id: str):
        return Response(
            data_embedding.get_paper.call(int(paper_id)),
            media_type="application/json",
        )

    return app
