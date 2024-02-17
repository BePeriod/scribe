"""
This module manages API calls to Slack
"""
import logging
import re
from typing import Dict, List, Optional, Tuple

import slack_sdk
from fastapi import UploadFile
from slack_bolt import App
from slack_sdk.errors import SlackApiError

from scribe.config.settings import settings
from scribe.models.models import Channel, Team, User

__slack = None
redirect_uri = f"{ settings.SITE_URL }/auth/redirect"


def __slack_app() -> App:
    global __slack
    if __slack is None:
        __slack = App(
            token=settings.SLACK_USER_TOKEN,
            signing_secret=settings.SLACK_SIGNING_SECRET,
        )
    return __slack


class SlackError(Exception):
    """
    Class used to indicate an error occurred in Slack API call.
    """

    pass


def access_token(code: str) -> str:
    """
    Use an authorization code to retrieve an access token.
    Code validation must occur prior to calling this function.

    :param code:
    :return:
    """
    slack_app = __slack_app()
    slack_token = slack_app.client.openid_connect_token(
        client_id=settings.SLACK_CLIENT_ID,
        client_secret=settings.SLACK_CLIENT_SECRET,
        redirect_uri=redirect_uri,
        code=code,
    )

    if not slack_token.get("ok", False):
        raise SlackError(slack_token.get("error"))

    return slack_token["access_token"]


class SlackClient:
    """
    Class used to interact with Slack API
    """

    def __init__(self, token: str):
        """
        Initializes the Slack Client

        :param token: The Slack OAuth access token
        """
        self.access_token = token
        self.client = slack_sdk.WebClient(token=token)

    def user(self) -> User:
        """
        Retrieves the user information from Slack for the access_token

        :return: User
        """

        try:
            info = self.client.openid_connect_userInfo()
            if not info.get("ok", False):
                raise SlackError(info.get("error"))

            user_id = info.get("sub")

            profile_res = self.client.users_profile_get()
            if not profile_res.get("ok", False):
                raise SlackError(profile_res.get("error"))

            profile = profile_res.get("profile", {})
            return User(
                id=user_id,
                real_name=profile.get("real_name", ""),
                real_name_normalized=profile.get("real_name_normalized", ""),
                first_name=profile.get("first_name", ""),
                last_name=profile.get("last_name", ""),
                display_name=profile.get(
                    "display_name",
                    profile.get("first_name", ""),
                ),
                image=profile.get("image_48", ""),
            )

        except SlackApiError:
            raise SlackError("invalid token")

    def team(self) -> Team:
        """
        Retrieves the team information from Slack for the access_token

        :return: Team
        """
        info = self.client.team_info()
        if not info.get("ok", False):
            raise SlackError(info.get("error"))
        team_id = info.get("team", {}).get("id", "")
        return Team(
            id=team_id,
            name=info.get("team", {}).get("name", ""),
            image=info.get("team", {}).get("icon", {}).get("image_68", ""),
        )

    def users(self) -> dict[str, User]:
        """
        Retrieves the channel information from Slack for the access_token

        :return: List[Channel]
        """

        users_list = {}
        next_cursor = None
        while True:
            response = self.client.users_list(cursor=next_cursor)
            if not response.get("ok", False):
                raise SlackError(response.get("error"))
            users = response.get("members", [])
            for user in users:
                if not user.get("is_bot", False):
                    profile = user.get("profile", {})
                    display_name = user.get("display_name", "")
                    if display_name == "":
                        display_name = (
                            f"{profile.get('first_name', '')} "
                            f"{profile.get('last_name', '')}"
                        ).strip()
                    if display_name == "":
                        display_name = profile.get("real_name", "")

                    if display_name != "":
                        users_list[user.get("id", "")] = User(
                            id=user.get("id", ""),
                            real_name=profile.get("real_name", ""),
                            real_name_normalized=profile.get(
                                "real_name_normalized", ""
                            ),
                            first_name=profile.get("first_name", ""),
                            last_name=profile.get("last_name", ""),
                            display_name=display_name,
                            image=profile.get("image_48", ""),
                        )

            next_cursor = response.get("response_metadata", {}).get("next_cursor", None)
            if not next_cursor:
                break

        return users_list

    def channels(self) -> List[Channel]:
        """
        Retrieves the channel information from Slack for the access_token

        :return: List[Channel]
        """

        users = self.users()
        channel_list = []
        next_cursor = None
        while True:
            response = self.client.conversations_list(
                exclude_archived=True,
                cursor=next_cursor,
                types="public_channel, private_channel, im",
            )
            if not response.get("ok", False):
                raise SlackError(response.get("error"))
            channels = response.get("channels", [])
            for channel in channels:
                if channel.get("is_im", False):
                    user = users.get(channel.get("user"), None)
                    if user:
                        channel_list.append(
                            Channel(id=channel.get("id", ""), name=user.display_name)
                        )
                else:
                    channel_list.append(
                        Channel(id=channel.get("id", ""), name=channel.get("name", ""))
                    )

            next_cursor = response.get("response_metadata", {}).get("next_cursor", None)
            if not next_cursor:
                break

        return sorted(channel_list, key=lambda x: x.name.lower())

    def publish(
        self,
        messages: dict[str, dict[str, str]],
        post_image: Optional[UploadFile],
        pin_to_channel: bool,
        notify_channel: bool,
    ) -> None:
        """
        Publishes a message to a Slack channel based on target language

        :param messages: map of target language and messages
        :param post_image: An image file to append to the post
               validation is expected before
        :param pin_to_channel: Flag for pinning the message
        :param notify_channel:Flag for Dear @channel

        :return: None
        """
        channel_messages = _prepare_messages(messages, notify_channel)
        if post_image:
            file_data = post_image.file.read()
            for channel, formatted_message in channel_messages:
                response = self.client.files_upload(
                    content=file_data,
                    initial_comment=formatted_message,
                    channels=channel,
                )
                if response["ok"] and pin_to_channel:
                    ts = None
                    try:
                        ts = response["file"]["shares"]["public"][channel][0]["ts"]
                    except KeyError:
                        try:
                            ts = response["file"]["shares"]["private"][channel][0]["ts"]
                        except KeyError:
                            logging.warning(
                                "could not find timestamp for channel %s", channel
                            )
                    if ts:
                        self.client.pins_add(channel=channel, timestamp=ts)
                else:
                    logging.warning(f"failed to post message: {response['error']}")
        else:
            for channel, formatted_message in channel_messages:
                response = self.client.chat_postMessage(
                    channel=channel, as_user=True, text=formatted_message
                )
                if response["ok"] and pin_to_channel:
                    ts = response["ts"]
                    self.client.pins_add(channel=channel, timestamp=ts)
                if not response["ok"]:
                    logging.warning(f"failed to post message: {response['error']}")


def _prepare_messages(
    messages: Dict[str, dict[str, str]], notify: bool
) -> List[Tuple[str, str]]:
    res = []
    for target, message in messages.items():
        channel = message.get("channel_id", None)
        if not channel:
            raise SlackError(f"Channel not found for language: {target}")
        res.append(
            (channel, format_message(message.get("message", ""), target, notify))
        )
    return res


def format_message(html: str, target: str, notify: bool) -> str:
    """
    Formats an HTML message into Slack markup.

    :param html: raw HTML message to format
    :param target: target language code
    :param notify:  flog for notifying the channel
    :return: markdown formatted message
    """
    html = html.replace("<p>", "\n\n")
    html = html.replace("</p>", "\n\n")
    html = html.replace("\n\n\n\n", "\n\n")
    html = html.replace("<strong>", "*")
    html = html.replace("</strong>", "*")
    html = html.replace("<em>", "_")
    html = html.replace("</em>", "_")
    html = re.sub("<img[^>]+>", "", html)
    html = html.strip()

    if notify:
        greeting = settings.LANGUAGE_GREETINGS[target]
        if not greeting:
            greeting = "Dear"

        html = f"{greeting} <!channel>,\n{html}"

    return html
