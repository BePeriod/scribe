from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from hotapi.models.models import ToDo

# initialize the frontend router
router = APIRouter()

# configure the template engine
_templates = Jinja2Templates(directory="templates")


# define the home page route
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # render the template file in /templates/home.html
    # we are not currently using this request object
    return _templates.TemplateResponse(
        "pages/home.html.j2", {"request": request}
    )


_todos = []


@router.get("/todos", response_class=HTMLResponse)
async def home(request: Request):
    return _templates.TemplateResponse(
        "frames/todos.html.j2", {"request": request, "todos": _todos}
    )


@router.post("/todos", response_class=HTMLResponse)
async def add_todo(request: Request, todo: ToDo = Depends()):
    todo.id = len(_todos) + 1
    _todos.append(todo)
    return _templates.TemplateResponse(
        "streams/add_todo.html.j2", {"request": request, "todo": todo},
        headers={"Content-Type": "text/vnd.turbo-stream.html; charset=utf-8"}
    )


@router.put("/todos/{todo_id}", response_class=HTMLResponse)
async def update_todo(request: Request, todo: ToDo = Depends()):
    global _todos
    _todos = [todo if item.id == todo.id else item for item in _todos]
    return _templates.TemplateResponse(
        "frames/todo.html.j2", {"request": request, "todo": todo}
    )
