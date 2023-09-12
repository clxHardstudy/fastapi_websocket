import logging


# Dependency
def get_db():
    try:
        from app.models.database import SessionLocal
        db = SessionLocal()
        yield db
    finally:
        db.close()


async def get_page(
        page: int = 1, size: int = 10
):
    return {"page": page, "size": size}


def page_help(data, page: int, size: int, total: int = None):
    if total is None:
        total = len(data)
        data = data[(page - 1) * size:page * size]
    return {"item": data, "extra_data": {"page": page, "size": size, "total": total}}


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
