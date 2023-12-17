from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# we will define this router in a moment
from hotapi.routers import pages

# initialize FastAPI
app = FastAPI()
# mount the static assets folder
app.mount("/static", StaticFiles(directory="static"), name="static")
# include our router
app.include_router(pages.router)
