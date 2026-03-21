"""
shared/schemas/__init__.py
-------------------------
Export all shared schemas.
"""

from .v1 import (
    APIResponse,
    BulkDeleteRequest,
    BulkDeleteResponse,
    DateRangeFilter,
    ErrorDetail,
    ErrorResponse,
    FileMetadata,
    HealthCheckResponse,
    IDOnly,
    PaginatedResponse,
    SearchFilter,
    SoftDeleteMixin,
    StudentID,
    TimestampMixin,
    ToggleRequest,
    ToggleResponse,
    UserID,
)

__all__ = [
    "PaginatedResponse",
    "TimestampMixin",
    "SoftDeleteMixin",
    "APIResponse",
    "ErrorDetail",
    "ErrorResponse",
    "HealthCheckResponse",
    "StudentID",
    "UserID",
    "IDOnly",
    "DateRangeFilter",
    "BulkDeleteRequest",
    "BulkDeleteResponse",
    "ToggleRequest",
    "ToggleResponse",
    "SearchFilter",
    "FileMetadata",
]
