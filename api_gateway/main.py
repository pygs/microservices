from fastapi import FastAPI, Request, Response
import requests

app = FastAPI(title="API Gateway")

AUTH_URL = "http://localhost:8001"
CRUD_URL = "http://localhost:8002"
LOG_URL  = "http://localhost:8003"

async def forward(request: Request, target_url: str):
    method = request.method

    headers = {}
    for k, v in request.headers.items():
        if k.lower() not in ("host", "content-length"):
            headers[k] = v

    body = await request.body()

    resp = requests.request(
        method=method,
        url=target_url,
        headers=headers,
        data=body,
        params=request.query_params
    )

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type")
    )


@app.api_route("/auth/{path:path}", methods=["GET", "POST"])
async def auth_proxy(path: str, request: Request):
    return await forward(request, f"{AUTH_URL}/{path}")

@app.api_route("/crud/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def crud_proxy(path: str, request: Request):
    return await forward(request, f"{CRUD_URL}/{path}")

@app.api_route("/logs/{path:path}", methods=["POST", "GET"])
async def logs_proxy(path: str, request: Request):
    return await forward(request, f"{LOG_URL}/{path}")
