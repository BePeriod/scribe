from typing import List

from slack_sdk.web import SlackResponse

from scribe.models.models import Channel, Team, User
from scribe.slack.slack import SlackError

code_tokens = {}
token_resources = {}


def mock_access_token(code: str) -> str:
    if code in code_tokens:
        return code_tokens[code]

    # create a dummy response to test the type of error that will happen.
    bad_response = SlackResponse(
        client=None,
        data={"ok": False},
        http_verb="POST",
        api_url="https://slack.com/api",
        req_args={},
        headers={},
        status_code=401,
    )

    if not bad_response.get("ok", False):
        raise SlackError("Invalid token code")

    # unreachable
    return bad_response["access_token"]


class MockSlackClient:
    def __init__(self, token: str):
        self.access_token = token
        self.resources = token_resources.get(token, {})

    def user(self) -> User:
        if "user" not in self.resources:
            raise SlackError("Could not find user")

        return self.resources["user"]

    def team(self) -> Team:
        if "team" not in self.resources:
            raise SlackError("Could not find team")

        return self.resources["team"]

    def channels(self) -> List[Channel]:
        if "channels" not in self.resources:
            raise SlackError("Could not find channels")

        return self.resources["channels"]

    def publish(self, html: str, target: str, pin_to_channel: bool) -> None:
        pass
