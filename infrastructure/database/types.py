from sqlalchemy.types import TypeDecorator, CHAR
import uuid


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type when available, otherwise stores as CHAR(36).
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import UUID as PG_UUID

            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        # If the driver already returned a uuid.UUID, return it directly
        if isinstance(value, uuid.UUID):
            return value

        # If bytes were returned, construct from bytes
        if isinstance(value, (bytes, bytearray)):
            return uuid.UUID(bytes=bytes(value))

        # Fall back to string conversion; catch failures and return raw value
        try:
            return uuid.UUID(str(value))
        except Exception:
            return value
