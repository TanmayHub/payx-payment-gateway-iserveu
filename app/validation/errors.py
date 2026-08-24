from typing import Any


def validation_error(
    code: str,
    message: str,
    layer: str,
    details: list[dict[str, Any]] | None = None,
):
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "layer": layer,
            "details": details or [],
        },
    }