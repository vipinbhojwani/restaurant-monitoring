from uuid import uuid4

from sqlalchemy import inspect


def generate_random_id():
    return str(uuid4())

def asdict(obj):
    """
    Converts a SQLAlchemy model instance into a dictionary.
    """
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}
