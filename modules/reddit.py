import aiohttp
import constants
import command
import random
from typing import Optional
from snakecord import Message, Embed
from snakecord.utils import JsonStructure, JsonField

commands = constants.commands


class RedditPost(JsonStructure):
    __json_fields__ = {
        'subreddit': JsonField('subreddit'),
        'selftext': JsonField('selftext'),
        'author': JsonField('author'),
        'title': JsonField('title'),
        'subreddit_name_prefixed': JsonField('subreddit_name_prefixed'),
        'downs': JsonField('downs'),
        'ups': JsonField('ups'),
        'upvote_ratio': JsonField('upvote_ratio'),
        'total_awards_received': JsonField('total_awards_received'),
        'over_18': JsonField('over_18'),
        'thumbnail': JsonField('thumbnail'),
        'edited': JsonField('edited'),
        'post_hint': JsonField('post_hint'),
        'permalink': JsonField('permalink'),
        'url': JsonField('url'),
        'num_comments': JsonField('num_comments')
    }

    subreddit: str
    selftext: str
    author_fullname: str
    title: str
    subreddit_name_prefixed: str
    downs: int
    ups: int
    upvote_ratio: float
    total_awards_received: int
    over_18: bool
    thumbnail: str
    edited: bool
    post_hint: str
    permalink: str
    url: str
    num_comments: int


class RedditClientError(Exception):
    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data


class RedditClient:
    BASE_URL = 'https://reddit.com'

    def __init__(self):
        self.client_session = aiohttp.ClientSession()

    async def request(
        self,
        subreddit: str,
        post_filter: Optional[str] = None,
        count: int = 30
    ) -> RedditPost:
        if post_filter is None:
            post_filter = ''
        url = f'{self.BASE_URL}/r/{subreddit}/{post_filter}.json'

        resp = await self.client_session.request(
            'GET', url, params={'count': count}
        )
        data = await resp.json()
        if resp.status != 200:
            raise RedditClientError(resp.status, data)
        return data

    async def close(self):
        await self.client_session.close()


def form_embed(post: RedditPost) -> Embed:
    embed = Embed(
        title=post.title,
        color=constants.BLUE,
        url=RedditClient.BASE_URL + post.permalink,
        description=post.selftext
    )
    embed.set_author(name=post.author)
    embed.description = (
        f':arrow_up: :arrow_down: **{post.ups}** '
        f'({post.upvote_ratio}%)\n'
        f'**edited**: {str(bool(post.edited)).lower()}\n'
        f'**nsfw**: {str(post.over_18).lower()}\n'
        f':trophy: **{post.total_awards_received}**\n'
        f':speech_balloon: **{post.num_comments}**'
    )

    if post.post_hint == 'image':
        embed.set_image(url=post.url)
    elif post.thumbnail is not None and post.thumbnail.startswith('http'):
        embed.set_image(url=post.thumbnail)
    if post.post_hint in ('link', 'rich:video'):
        trunc = post.url[:40]
        embed.description += '\n\n**[%s...](%s)**' % (trunc, post.url)
    elif post.post_hint in (None, 'self'):
        trunc = post.selftext[:min((len(post.selftext), 1000))]
        embed.description += '\n\n' + trunc + '...'

    return embed


@commands.command
async def reddit(
    message: Message,
    subreddit: str,
    post_filter: str = 'new'
) -> None:
    if subreddit.startswith('r/'):
        subreddit = subreddit[2:]

    client = RedditClient()
    try:
        data = await client.request(subreddit, post_filter)
    except RedditClientError as e:
        raise command.CommandError(
            f'Sorry, that request failed `Status Code: {e.status_code}`',
            message
        )
    except aiohttp.ClientError:
        raise command.CommandError('Sorry, that request failed', message)
    finally:
        await client.close()

    try:
        post = random.choice(data['data']['children'])['data']
    except (IndexError, KeyError):
        raise commands.CommandError('Unable to parse that response', message)
    post = RedditPost.unmarshal(post)

    if post.over_18 and not message.channel.nsfw:
        raise command.CommandError(
            'That post is NSFW silly... try in an NSFW channel',
            message
        )

    await message.channel.send(embed=form_embed(post))
