"""
This module contains all the Pydantic models for the app.
"""

from typing import Optional

from pydantic import BaseModel


class Team(BaseModel):
    """
    The Team class represents a Slack team.

    Attributes
    ----------
        id : str
            The id of the team
        name : str
            The name of the team
        image : str
            The url of the team image
    """

    id: str
    name: str
    image: Optional[str] = None


class User(BaseModel):
    """
    The User class represents a Slack user

    Attributes
    ----------
        id : str
            The id of the user
        real_name : str
            The name of the user
        real_name_normalized : str
            The name of the user with accents removed
        first_name : str
            The user's given name
        last_name : str
            The user's surname
        display_name : str
            The user's display name
        image : str
            The url of the user's avatar
    """

    id: str
    real_name: str
    real_name_normalized: str
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    image: Optional[str] = None


class Channel(BaseModel):
    """
    The Channel class represents a Slack channel

    Attributes
    ----------
        id : str
            The id of the channel
        name : str
            The name of the channel
    """

    id: str
    name: str


class Recording(BaseModel):
    """
    The Recording class represents an audio recording

    Attributes
    ----------
        id : str
            The id of the recording
        file_path : str
            The file location
        transcription : str
            The text transcription of the audio
    """

    id: str
    file_path: str
    transcription: Optional[str] = None
