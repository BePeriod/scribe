# Scribe

## A Slack app for transcription and translation

Scribe is a simple browser app that takes a microphone recording,
translates it into many languages, and posts to different language channels on Slack.

## Project Structure

### Backend

The serverside of this project is written in Python using FastAPI.
The backend folder is where all the Python code is stored.
The project entrypoint is `src/scribe/main.py`.
The file `dependencies.py` contains FastAPI rout dependency functions.
The file `exceptions.py` contains custom error types.

The `config` package contains the environment variables and logging settings.
The `models` folder contains the Pydantic models.
The `routers` package contains a single `pages.py` module to serve HTML endpoints.
The `session` package contains simple in memory session management.
The `slack` package contains a client configured to make Slack API calls.

### Frontend

The frontend folder houses the TypeScript files
as well as a `global.css` file for Tailwind.
There is also a controllers folder where [Stimulus Controllers](https://stimulus.hotwired.dev/reference/controllers)
reside.

### Templates

All views are implemented as Jinja2 templates. These reside in the `templates` folder.
Within that are four additional folders.

- `layout`: This is where the structural markup lives.
- `pages`: This houses individual page view templates.
- `components`: This is where the [Turbo Frame](https://turbo.hotwired.dev/handbook/components) templates live.
- `streams`: This is where the [Turbo Stream](https://turbo.hotwired.dev/handbook/streams) templates live.

### Static Assets

The static folder is where all publicly served assets will go.
This is also where the frontend code gets built.
The `vendor` folder in here includes the `TinyMCE` text editor.
This is planned to be removed from the repo and pulled in through Rollup instead.

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
$ poetry run uvicorn scribe.main:app --reload
```

© 2023 TurtleStack Development
