"""
shared/schemas/v1.py
────────────────────
Shared Pydantic schemas dùng chung cho tất cả modules.
Dùng cho API versioning và schema reuse.
"""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


# ─── Generic paginated response ───────────────────────────────────────────────

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T] = Field(default_factory=list)
    total: int = Field(default=0, ge=0)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1)
    has_next: bool = Field(default=False)
    has_prev: bool = Field(default=False)

    model_config = {"from_attributes": True}


# ─── Common metadata ────────────────────────────────────────────────────────────

class TimestampMixin(BaseModel):
    """Mixin: thêm created_at / updated_at vào model."""

    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)


class SoftDeleteMixin(BaseModel):
    """Mixin: thêm soft delete fields."""

    deleted_at: datetime | None = Field(default=None)
    is_deleted: bool = Field(default=False)


# ─── API metadata ──────────────────────────────────────────────────────────────

class APIResponse(BaseModel):
    """Standard API response wrapper."""

    success: bool = Field(default=True)
    message: str | None = Field(default=None)
    data: Any = Field(default=None)
    request_id: str | None = Field(default=None, description="UUID để trace request")


class ErrorDetail(BaseModel):
    """Chi tiết lỗi trả về cho client."""

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    field: str | None = Field(default=None, description="Field gây lỗi (nếu có)")
    detail: Any = Field(default=None, description="Chi tiết bổ sung")


class ErrorResponse(BaseModel):
    """Standard error response."""

    success: bool = Field(default=False)
    error: ErrorDetail


class HealthCheckResponse(BaseModel):
    """Health check endpoint response."""

    status: str = Field(..., description="ok | degraded | down")
    version: str = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    database: str = Field(..., description="connected | disconnected")
    llm: str = Field(..., description="available | unavailable | timeout")
    uptime_seconds: float = Field(default=0.0)


# ─── ID wrapper ───────────────────────────────────────────────────────────────

class StudentID(BaseModel):
    """Wrapper cho student_id dùng chung."""

    student_id: str = Field(..., min_length=1, description="Student primary key")


class UserID(BaseModel):
    """Wrapper cho user_id dùng chung."""

    user_id: int = Field(..., gt=0, description="User primary key")


class IDOnly(BaseModel):
    """Chỉ trả về ID khi tạo resource thành công."""

    id: int = Field(..., gt=0)
    created: bool = Field(default=True)


# ─── Date range filter ────────────────────────────────────────────────────────

class DateRangeFilter(BaseModel):
    """Filter by date range — dùng chung cho nhiều endpoint."""

    start_date: datetime | None = Field(default=None, description="Từ ngày")
    end_date: datetime | None = Field(default=None, description="Đến ngày")

    def validate_range(self) -> None:
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("start_date must be <= end_date")


# ─── Bulk operations ─────────────────────────────────────────────────────────

class BulkDeleteRequest(BaseModel):
    """Request xóa nhiều items."""

    ids: list[int] = Field(..., min_length=1, max_length=100)
    soft_delete: bool = Field(default=True, description="True = soft delete, False = hard delete")


class BulkDeleteResponse(BaseModel):
    """Response xóa nhiều items."""

    deleted_count: int = Field(default=0)
    failed_ids: list[int] = Field(default_factory=list, description="IDs không xóa được")


# ─── Toggle / flag ───────────────────────────────────────────────────────────

class ToggleRequest(BaseModel):
    """Toggle một boolean flag."""

    value: bool = Field(..., description="Giá trị mới")


class ToggleResponse(BaseModel):
    """Response sau khi toggle."""

    field: str = Field(...)
    old_value: bool = Field(...)
    new_value: bool = Field(...)


# ─── Search / filter ─────────────────────────────────────────────────────────

class SearchFilter(BaseModel):
    """Filter dùng chung cho search endpoints."""

    query: str | None = Field(default=None, max_length=200)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str | None = Field(default=None, description="Field name to sort by")
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$")


# ─── File / upload metadata ──────────────────────────────────────────────────

class FileMetadata(BaseModel):
    """Metadata cho file upload."""

    filename: str = Field(...)
    content_type: str | None = Field(default=None)
    size_bytes: int = Field(..., ge=0)
    url: str | None = Field(default=None, description="URL sau khi upload")


# ─── Re-export từ modules (nếu cần dùng chung) ─────────────────────────────
# Nếu một schema được dùng ở nhiều modules, import vào đây:
#
# from modules.smart_parenting.schemas import StudentProfile
# from modules.etester.schemas import BadgeResponse
#
# __all__ = [
#     "PaginatedResponse",
#     "APIResponse",
#     "ErrorResponse",
#     "StudentProfile",
#     "BadgeResponse",
#     ...
# ]
