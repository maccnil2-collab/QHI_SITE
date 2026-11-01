# QHI AUTO API

Run from the backend directory with the project environment:

```powershell
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Set `DATABASE_URL` privately before using database routes. Apply Alembic migrations before serving catalog and quote endpoints. `/api/v1/health` does not require a database. No sample inventory or pricing is bundled.

Order document upload is disabled unless `DOCUMENT_STORAGE_PATH` points to an absolute private writable filesystem mount outside the repository. Keep that directory backed up. This local adapter does not scan files for malware; production requires durable object storage, scanning, and a retention policy. Uploads are limited to 10 MiB PDF/JPEG/PNG files.

For the single-host container deployment starter and its release blockers, see [`../docs/DEPLOYMENT.md`](../docs/DEPLOYMENT.md).
