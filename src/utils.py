from loguru import logger

STATUS = {200: "success", 400: "error"}


def return_json(
    status: STATUS, message: str = None, data: list = None, details: str = None
) -> dict:
    return {
        "status": status,
        "message": message,
        "data": data,
        "details": details,
    }


logger.add(
    "../app.log",
    format="{time}\t|\t{level}\t|\t{message}",
    level="INFO",
    rotation="10MB",
    compression="zip",
)
