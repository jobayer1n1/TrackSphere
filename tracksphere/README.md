# TrackSphere

TrackSphere is a university software engineering project for fleet and delivery management.
This repository establishes the initial architecture and foundation for a layered Python/FastAPI application.

## Project Structure

- `tracksphere/` - application package
- `tests/` - unit and integration tests
- `docs/` - architectural and design pattern documentation

## Getting Started

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
python -m pip install -r tracksphere/requirements.txt
```

3. Start the app:

```bash
uvicorn tracksphere.main:app --reload
```

4. Verify health:

```bash
curl http://127.0.0.1:8000/health
```
