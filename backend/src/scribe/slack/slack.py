from typing import List

import slack_sdk
from slack_bolt import App

from scribe.auth.auth import redirect_uri
from scribe.config.settings import settings
from scribe.models.models import Channel, Team, User

__slack = App(
    token=settings.SLACK_USER_TOKEN, signing_secret=settings.SLACK_SIGNING_SECRET
)


def access_token(code: str) -> str:
    slack_token = __slack.client.openid_connect_token(
        client_id=settings.SLACK_CLIENT_ID,
        client_secret=settings.SLACK_CLIENT_SECRET,
        redirect_uri=redirect_uri,
        code=code,
    )

    return slack_token["access_token"]


class SlackError(Exception):
    pass


class SlackClient:
    def __init__(self, token: str):
        self.access_token = token
        self.client = slack_sdk.WebClient(token=token)

    def user(self) -> User:
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

    def team(self) -> Team:
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
