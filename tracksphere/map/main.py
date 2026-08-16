from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    # Example location
    latitude = 23.8103
    longitude = 90.4125

    return templates.TemplateResponse(
        "map.html",
        {
            "request": request,
            "latitude": latitude,
            "longitude": longitude,
        }
    )