from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import upload


app = FastAPI()


# --------------------------------------------------
# CORS
# --------------------------------------------------

FRONTEND_ORIGIN = (
    "https://bookish-acorn-jj4jxjqp7xjxc5xwx-5173.app.github.dev"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Routes
# --------------------------------------------------

app.include_router(upload.router)