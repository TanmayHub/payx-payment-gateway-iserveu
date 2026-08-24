from .api.transactions import router as transaction_router

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .database import Base, engine
from . import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="iSUpayX Payment Gateway",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    details = []

    for error in exc.errors():
        location = error.get("loc", [])
        field = str(location[-1]) if location else "unknown"

        details.append(
            {
                "field": field,
                "rule": error.get("type", "validation"),
                "message": error.get("msg", "Invalid value"),
            }
        )

    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": {
                "code": "SCHEMA_VALIDATION_ERROR",
                "message": "Request schema validation failed",
                "layer": "schema",
                "details": details,
            },
        },
    )


app.include_router(transaction_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}