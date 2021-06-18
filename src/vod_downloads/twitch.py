"""
Twitch API access.
"""

import requests

from src.vod_downloads import CLIENT_ID
from src.vod_downloads.exceptions import ConsoleError


class GQLError(Exception):
    def __init__(self, errors):
        super().__init__("GraphQL query failed")
        self.errors = errors


def authenticated_get(url, params={}, headers={}):
    headers['Client-ID'] = CLIENT_ID

    response = requests.get(url, params, headers=headers)
    if 400 <= response.status_code < 500:
        data = response.json()
        # TODO: this does not look nice in the console since data["message"]
        # can contain a JSON encoded object.
        raise ConsoleError(data["message"])

    response.raise_for_status()

    return response


def authenticated_post(url, data=None, json=None, headers={}):
    headers['Client-ID'] = CLIENT_ID

    response = requests.post(url, data=data, json=json, headers=headers)
    if response.status_code == 400:
        data = response.json()
        raise ConsoleError(data["message"])

    response.raise_for_status()

    return response


def kraken_get(url, params={}, headers={}):
    """
    Add accept header required by kraken API v5.
    see: https://discuss.dev.twitch.tv/t/change-in-access-to-deprecated-kraken-twitch-apis/22241
    """
    headers["Accept"] = "application/vnd.twitchtv.v5+json"
    return authenticated_get(url, params, headers)


def gql_post(query):
    url = "https://gql.twitch.tv/gql"
    response = authenticated_post(url, data=query).json()

    if "errors" in response:
        raise GQLError(response["errors"])

    return response


def gql_query(query):
    url = "https://gql.twitch.tv/gql"
    response = authenticated_post(url, json={"query": query}).json()

    if "errors" in response:
        raise GQLError(response["errors"])

    return response


def get_video_legacy(video_id):
    """
    https://dev.twitch.tv/docs/v5/reference/videos#get-video
    """
    url = "https://api.twitch.tv/kraken/videos/{}".format(video_id)

    return kraken_get(url).json()


VIDEO_FIELDS = """
    id
    title
    publishedAt
    broadcastType
    lengthSeconds
    game {
        name
    }
    creator {
        login
        displayName
    }
"""


def get_video(video_id):
    query = """
    {{
        video(id: "{video_id}") {{
            {fields}
        }}
    }}
    """

    query = query.format(video_id=video_id, fields=VIDEO_FIELDS)

    response = gql_query(query)
    return response["data"]["video"]


def get_channel_videos(channel_id, limit, sort, type="archive", game_ids=[], after=None):
    query = """
    {{
        user(login: "{channel_id}") {{
            videos(
                first: {limit},
                type: {type},
                sort: {sort},
                after: "{after}",
                options: {{
                    gameIDs: {game_ids}
                }}
            ) {{
                totalCount
                pageInfo {{
                    hasNextPage
                }}
                edges {{
                    cursor
                    node {{
                        id
                        title
                        publishedAt
                        broadcastType
                        lengthSeconds
                        game {{
                            name
                        }}
                        creator {{
                            login
                            displayName
                        }}
                    }}
                }}
            }}
        }}
    }}
    """

    query = query.format(**{
        "channel_id": channel_id,
        "game_ids": game_ids,
        "after": after if after else "",
        "limit": limit,
        "sort": sort.upper(),
        "type": type.upper(),
    })

    response = gql_query(query)

    if not response["data"]["user"]:
        raise ConsoleError("Channel {} not found".format(channel_id))

    return response["data"]["user"]["videos"]


def channel_videos_generator(channel_id, limit, sort, type, game_ids=None):
    cursor = ""
    while True:
        videos = get_channel_videos(
            channel_id, limit, sort, type, game_ids=game_ids, after=cursor)

        if not videos["edges"]:
            break

        has_next = videos["pageInfo"]["hasNextPage"]
        cursor = videos["edges"][-1]["cursor"] if has_next else None

        yield videos, has_next

        if not cursor:
            break


def get_access_token(video_id):
    query = """
    {{
        videoPlaybackAccessToken(
            id: {video_id},
            params: {{
                platform: "web",
                playerBackend: "mediaplayer",
                playerType: "site"
            }}
        ) {{
            signature
            value
        }}
    }}
    """

    query = query.format(video_id=video_id)

    response = gql_query(query)
    return response["data"]["videoPlaybackAccessToken"]


def get_playlists(video_id, access_token):
    """
    For a given video return a playlist which contains possible video qualities.
    """
    url = "http://usher.twitch.tv/vod/{}".format(video_id)

    response = requests.get(url, params={
        "nauth": access_token['value'],
        "nauthsig": access_token['signature'],
        "allow_source": "true",
        "player": "twitchweb",
    })
    response.raise_for_status()
    return response.content.decode('utf-8')


def get_game_id(name):
    query = """
    {{
        game(name: "{}") {{
            id
        }}
    }}
    """

    response = gql_query(query.format(name.strip()))
    game = response["data"]["game"]
    if game:
        return game["id"]
