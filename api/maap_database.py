from flask_sqlalchemy import SQLAlchemy as BaseSQLAlchemy
from sqlalchemy.orm import Session as BaseSession
from flask import current_app
import logging


class _Session(BaseSession):
    def commit(self):
        try:
            super().commit()
        except Exception as exc:
            self.rollback()
            logger = getattr(current_app, "logger", logging.getLogger(__name__))
            logger.error(
                "Database commit failed. New: %s Dirty: %s Deleted: %s",
                list(self.new),
                list(self.dirty),
                list(self.deleted),
                exc_info=True,
            )
            raise


class SQLAlchemy(BaseSQLAlchemy):
    def __init__(self, **kwargs):
        session_options = kwargs.pop("session_options", {})
        session_options.setdefault("class_", _Session)
        super().__init__(session_options=session_options, **kwargs)


db = SQLAlchemy()
