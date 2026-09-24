from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from fastapi.staticfiles import (
    StaticFiles
)

from app.config import settings

from app.database import (
    init_db
)

from app.routes.api import (
    router as api_router
)

from app.routes.web import (
    router as web_router
)


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=
        settings.CORS_ORIGINS,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


app.mount(
    "/static",
    StaticFiles(
        directory="app/static"
    ),
    name="static"
)


app.include_router(
    api_router
)

app.include_router(
    web_router
)


@app.on_event("startup")
def startup():

    init_db()


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
