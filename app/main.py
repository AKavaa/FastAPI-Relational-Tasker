from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.db.database import Base, engine

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Project & Task API", version="1.0.0", lifespan=lifespan)

@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(router)
