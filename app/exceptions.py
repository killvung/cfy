"""Domain and persistence errors for the review app."""


class DatabaseError(Exception):
    """Base class for data-layer failures."""


class DuplicateRecordError(DatabaseError):
    """Postgres UNIQUE constraint violation."""


class DuplicateFeedbackError(DuplicateRecordError):
    """Feedback already submitted for this session and task."""


class DuplicateSessionError(DuplicateRecordError):
    """Session already exists for this invite (concurrent create)."""
