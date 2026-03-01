"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from contextlib import asynccontextmanager

from app.routers import market_data, fundamentals, portfolio, valuation
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Financial Analysis & DCF Valuation Dashboard", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(market_data.router)
app.include_router(fundamentals.router)
app.include_router(portfolio.router)
app.include_router(valuation.router)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
