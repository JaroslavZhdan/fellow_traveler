from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from core.config import settings
from routers import auth, cars, trips, requests, comments, ratings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(auth.router)
app.include_router(cars.router)
app.include_router(trips.router)
app.include_router(requests.router)
app.include_router(comments.router)
app.include_router(ratings.router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

