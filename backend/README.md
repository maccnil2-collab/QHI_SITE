# QHI AUTO API

Run from the backend directory with the project environment:

```powershell
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Set `DATABASE_URL` privately before using database routes. Apply Alembic migrations before serving catalog and quote endpoints. `/api/v1/health` does not require a database. No sample inventory or pricing is bundled.
