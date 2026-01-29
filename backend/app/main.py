from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router
from app.services.entity_maintainer import entity_maintainer

app = FastAPI(title="Glas Mail Sender API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {"status": "ok", "message": "Glas Mail Sender API is running"}


@app.get("/sync")
async def sync():
    await entity_maintainer.run_full_sync()
