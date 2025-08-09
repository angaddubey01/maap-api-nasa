import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session as _Session
from flask import has_request_context, request


class SafeCommitSession(_Session):
    """
    SQLAlchemy Session that guarantees a rollback on commit failure
    and adds contextual error logging. This centralizes transaction
    safety across the API without changing endpoint logic.
    """

    def commit(self):
        try:
            super().commit()
        except Exception as exc:
            try:
                self.rollback()
            finally:
                # Add contextual information to the log for easier debugging
                logger = logging.getLogger(__name__)
                if has_request_context():
                    try:
                        logger.exception(
                            "DB commit failed: method=%s path=%s endpoint=%s args=%s json_keys=%s",
                            request.method,
                            request.path,
                            request.endpoint,
                            dict(request.args),
                            list((request.get_json(silent=True) or {}).keys()),
                        )
                    except Exception:
                        logger.exception("DB commit failed (context logging error)")
                else:
                    logger.exception("DB commit failed (no request context)")
            raise


db = SQLAlchemy(session_options={"class_": SafeCommitSession})
