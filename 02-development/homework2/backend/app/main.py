from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routers import boards, cards, comments
from .store import NotFoundError


app = FastAPI(
    title="Kanbits API",
    version="0.1.0",
    description="REST API for the Kanbits collaborative Kanban board.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NotFoundError)
async def handle_not_found(_: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"message": str(exc)})


@app.exception_handler(ValueError)
async def handle_bad_request(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"message": str(exc)})


@app.exception_handler(RequestValidationError)
async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"message": "Invalid request: " + str(exc.errors())})


app.include_router(boards.router)
app.include_router(cards.router)
app.include_router(comments.router)
