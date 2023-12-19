import inspect
from typing import Annotated, Optional

from fastapi import Form
from pydantic import BaseModel


# since Hotwire deals mostly with form data instead of json,
# we will add this decorator function to convert Pydantic models
# taken from:
# https://stackoverflow.com/questions/60127234/how-to-use-a-pydantic-model-with-form-data-in-fastapi/77113651#77113651
# the accepted answer no longer works with FastAPI 0.103.1
def as_form(cls):
    new_params = [
        inspect.Parameter(
            field_name,
            inspect.Parameter.POSITIONAL_ONLY,
            default=model_field.default,
            annotation=Annotated[model_field.annotation, *model_field.metadata, Form()],
        )
        for field_name, model_field in cls.model_fields.items()
    ]

    cls.__signature__ = cls.__signature__.replace(parameters=new_params)

    return cls


@as_form
class ToDo(BaseModel):
    id: Optional[int] = None
    text: str
    is_done: Optional[bool] = False


class Team(BaseModel):
    id: str
    name: str
    image: Optional[str] = None


class User(BaseModel):
    id: str
    real_name: str
    real_name_normalized: str
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    image: Optional[str] = None


class Channel(BaseModel):
    id: str
    name: str


class Recording(BaseModel):
    id: str
    file_path: str
    transcription: Optional[str] = None
