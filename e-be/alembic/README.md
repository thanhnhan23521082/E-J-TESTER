# Alembic — Database Migrations

## Cách chạy

### Người mới vào project (setup lần đầu)

```bash
cd e-be

# 1. Cài dependencies (nếu chưa có)
pip install -r requirements.txt

# 2. Copy .env.example → .env, cấu hình DATABASE_URL
#    VD: DATABASE_URL=postgresql://postgres:postgres@localhost:5432/etest_one

# 3. Tạo database (nếu chưa có)
createdb etest_one

# 4. Chạy tất cả migrations từ đầu
alembic upgrade head
```

### Các lệnh thường dùng

```bash
# Xem migration hiện tại trên DB
alembic current

# Xem lịch sử migrations
alembic history --verbose

# Apply migrations mới nhất
alembic upgrade head

# Rollback 1 migration
alembic downgrade -1

# Rollback về base (xóa hết bảng)
alembic downgrade base

# Tạo migration mới (sau khi sửa model)
# Ví dụ: thêm cột mới vào model.py rồi chạy
alembic revision --autogenerate -m "005_add_new_column"

# Dùng Python trực tiếp (nếu không có alembic CLI)
python -m alembic upgrade head
python -m alembic downgrade -1
```

## Cấu trúc migration chain

```
001 →  002  →  003_seed_from_data_folder (HEAD)
001_schema       trigger_digest   seed_from_json
```

| Migration | Mô tả |
|-----------|--------|
| `001` | Tạo schema nền: users, mentors, parents, students, schools, courses, behavioral_logs, conversations, milestones |
| `002` | Tạo trigger `sync_student_digest_from_milestones` |
| `003_seed_from_data_folder` | Seed dữ liệu tự động từ `alembic/data/*.json` |

Lưu ý: Seed chạy idempotent (upsert), có thể chạy lại an toàn.

## Thêm migration mới

1. Sửa model ở `shared/model.py`
2. Chạy autogenerate:

   ```bash
   alembic revision --autogenerate -m "005_description"
   ```

3. Kiểm tra file migration trong `alembic/versions/`
4. Apply:

   ```bash
   alembic upgrade head
   ```

## Cài đặt Alembic CLI (nếu chưa có)

```bash
# Cài alembic package
pip install alembic

# Hoặc dùng qua Python module
python -m alembic
```

## Reset database (DEV only — KHÔNG làm ở production)

```bash
# Xóa hết, tạo lại từ đầu
alembic downgrade base
alembic upgrade head

# Hoặc drop DB rồi tạo lại
dropdb etest_one && createdb etest_one && alembic upgrade head
```
