import logging

from flask_sqlalchemy import SQLAlchemy, SignallingSession
from sqlalchemy import orm


class _Session(SignallingSession):
    def commit(self):
        try:
            super().commit()
        except Exception:
            try:
                self.rollback()
            finally:
                logging.getLogger(__name__).error(
                    "Session commit failed; rolled back (new=%s dirty=%s)",
                    list(self.new),
                    list(self.dirty),
                    exc_info=True,
                )
            raise


class _SQLAlchemy(SQLAlchemy):
    def create_session(self, options):
        return orm.sessionmaker(class_=_Session, db=self, **options)


db = _SQLAlchemy()
