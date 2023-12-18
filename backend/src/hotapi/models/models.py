import inspect
from typing import Optional, Annotated
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
