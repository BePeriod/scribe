"""
This module manages API calls to Slack
"""
from typing import List

import slack_sdk
from slack_bolt import App
from slack_sdk.errors import SlackApiError

from scribe.config.settings import settings
from scribe.models.models import Channel, Team, User

__slack = App(
    token=settings.SLACK_USER_TOKEN, signing_secret=settings.SLACK_SIGNING_SECRET
)

redirect_uri = f"{ settings.SITE_URL }/auth/redirect"


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
    slack_token = __slack.client.openid_connect_token(
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

    def channels(self) -> List[Channel]:
        """
        Retrieves the channel information from Slack for the access_token

        :return: List[Channel]
        """
        channel_list = []
        next_cursor = None
        while True:
            response = self.client.conversations_list(
                exclude_archived=True, cursor=next_cursor
            )
            if not response.get("ok", False):
                raise SlackError(response.get("error"))
            channels = response.get("channels", [])
            channel_list += [
                Channel(id=channel.get("id", ""), name=channel.get("name", ""))
                for channel in channels
                if channel.get("is_channel", False) and channel.get("is_member", False)
            ]
            next_cursor = response.get("response_metadata", {}).get("next_cursor", None)
            if not next_cursor:
                break

        return channel_list

    def publish(self, html: str, target: str, pin_to_channel: bool) -> None:
        """
        Publishes a message to a Slack channel based on target language

        :param html: The raw message to publish
        :param target: The target code
        :param pin_to_channel: Flag for pinning the message

        :return: None
        """
        formatted = format_message(html)
        channel = settings.SLACK_CHANNEL_LANGUAGE_MAP.get(target, None)
        if not channel:
            raise SlackError(f"Channel not found for language: {target}")

        if settings.DEVELOPMENT_MODE:
            formatted = (
                f"TEST MESSAGE FOR: {target}"
                f"\n---------------------------------\n"
                f"{formatted}"
            )

        response = self.client.chat_postMessage(
            channel=channel, text=formatted, as_user=True
        )

        if response["ok"] and pin_to_channel:
            self.client.pins_add(channel=channel, timestamp=response["ts"])


def format_message(html: str) -> str:
    """
    Formats an HTML message into Slack markup.

    :param html: raw HTML message to format
    :return: markdown formatted message
    """
    html = html.replace("<p>", "\n\n")
    html = html.replace("</p>", "\n\n")
    html = html.replace("@channel", "<!channel>")
    html = html.replace("\n\n\n\n", "\n\n")
    html = html.replace("<strong>", "*")
    html = html.replace("</strong>", "*")
    html = html.replace("<em>", "_")
    html = html.replace("</em>", "_")

    return html.strip()
