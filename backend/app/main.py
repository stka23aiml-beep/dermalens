from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import upload


app = FastAPI()


# --------------------------------------------------
# CORS
# --------------------------------------------------

FRONTEND_ORIGIN = (
    "https://super-dollop-pjqx9p6w4qv4h65rw-5173.app.github.dev"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_ORIGIN,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"https://.*\.app\.github\.dev",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Routes
# --------------------------------------------------

app.include_router(upload.router)