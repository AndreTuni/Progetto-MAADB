from fastapi import FastAPI
from routers import connections_health, parametric_queries, analytical_queries


app = FastAPI(
    title="MAADB API",
    description="API for interacting with MAADB databases.",
    version="1.0.0"
)


app.include_router(connections_health.router, tags=["Health Checks"])
app.include_router(parametric_queries.router, tags=["Parametric Queries"])
app.include_router(analytical_queries.router, tags=["Analytical Queries"])


@app.get("/")
async def root():
    return {"message": "Welcome to MAADB API. Visit /docs for documentation."}