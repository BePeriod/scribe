# HotAPI - FastAPI, Hotwired

This repository is a skeleton project for integrating [FastAPI](https://fastapi.tiangolo.com/) with [Hotwire](https://hotwired.dev/).
It is the accompaniment to a tutorial article located [here](https://www.turtlestack.dev/articles/hotwiring-fast-api).

Please refer to the article for an in-depth explanation of the project.

## Project Structure

### Backend

The backend folder is where all the Python code is stored.
The `hotapi`
package contained therein has a `main.py` file to serve FastAPI.
The `routers` package contains a single `pages.py` module to serve HTML endpoints.
The `models` folder contains the Pydantic models.

### Frontend

The frontend folder houses the TypeScript files
as well as a `global.css` file for Tailwind.
There is also a controllers folder where [Stimulus Controllers](https://stimulus.hotwired.dev/reference/controllers) reside.

### Templates

All views are implemented as Jinja2 templates. These reside in the templates folder.
Within that are four additional folders.

- `layout`: This is where the structural markup lives.
- `pages`: This houses individual page view templates.
- `frames`: This is where the [Turbo Frame](https://turbo.hotwired.dev/handbook/frames) templates live.
- `streams`: This is where the [Turbo Stream](https://turbo.hotwired.dev/handbook/streams) templates live.

### Static Assets

The static folder is where all publicly served assets will go.
This is also where the frontend code gets built.

## Tooling

Poetry is used for Python package management.
pNPM manages the frontend dependencies.
Rollup is used as the frontend build tool.

## Building Frontend Assets

You can run `pnpm run build` to generate the frontend runtime files.
These are exported to `static/dist`.

`pnpm run dev` will start the build tools in watch-mode.
It also fires up browser-sync for live reloading.
This wraps the FastAPI server in a proxy running on port 3000.

## Running the project

To start the uvicorn server on port 8000 run the following.

```shell
$ poetry run uvicorn hotapi.main:app --reload
```

© 2023 TurtleStack Development
