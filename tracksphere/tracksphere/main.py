import socket
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from tracksphere.app.api import router as api_router
from tracksphere.app.infrastructure.database import init_db

app = FastAPI(
    title="TrackSphere",
    description="TrackSphere fleet and delivery management system.",
    version="0.1.0",
)

app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).resolve().parent / "app" / "static")),
    name="static",
)

app.include_router(api_router)


def _get_lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def _get_server_port() -> int:
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            try:
                return int(sys.argv[i + 1])
            except ValueError:
                pass
        elif arg.startswith("--port="):
            try:
                return int(arg.split("=")[1])
            except ValueError:
                pass
    return 8000


@app.on_event("startup")
def on_startup():
    init_db()
    lan_ip = _get_lan_ip()
    port = _get_server_port()
    print("\n" + "=" * 65)
    print(" 🚀 TrackSphere Server Started")
    print(f" 🌐 Local LAN Access: http://{lan_ip}:{port}")
    print(f" 📍 Device Update Endpoint: http://{lan_ip}:{port}/locations/update/BUS-001")
    print(" 💡 Note: Ensure server is launched with '--host 0.0.0.0' to accept LAN devices")
    print("=" * 65 + "\n")



@app.get("/")
def root():
    return RedirectResponse(url="/login")


@app.get("/health")
def health_check():
    return JSONResponse({"status": "ok", "service": "TrackSphere"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("tracksphere.main:app", host="0.0.0.0", port=8000, reload=True)

