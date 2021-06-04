import aiohttp
import command
import random
import constants
from typing import Optional
from snekcord import Message, EmbedBuilder
from snekcord.clients.wsevents import MessageCreateEvent
from snekcord.utils import JsonField, JsonObject, JsonTemplate

commands = constants.loader.get_global('commands')
client = constants.loader.get_global('client')


RedditPostTemplate = JsonTemplate(
    subreddit=JsonField('subreddit'),
    selftext=JsonField('selftext'),
    author=JsonField('author'),
    title=JsonField('title'),
    subreddit_name_prefixed=JsonField('subreddit_name_prefixed'),
    downs=JsonField('downs'),
    ups=JsonField('ups'),
    upvote_ratio=JsonField('upvote_ratio'),
    total_awards_received=JsonField('total_awards_received'),
    over_18=JsonField('over_18'),
    thumbnail=JsonField('thumbnail'),
    edited=JsonField('edited'),
    post_hint=JsonField('post_hint'),
    permalink=JsonField('permalink'),
    url=JsonField('url'),
    num_comments=JsonField('num_comments')
)

class RedditPost(JsonObject, template=RedditPostTemplate):
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


def form_embed(post: RedditPost) -> EmbedBuilder:
    builder = EmbedBuilder(
        title=post.title,
        color=constants.BLUE,
        url=RedditClient.BASE_URL + post.permalink,
        description=post.selftext
    )
    builder.set_author(name=post.author)
    builder.set_description(
        f':arrow_up: :arrow_down: **{post.ups}** '
        f'({post.upvote_ratio * 100}%)\n'
        f'**edited**: {str(bool(post.edited)).lower()}\n'
        f'**nsfw**: {str(post.over_18).lower()}\n'
        f':trophy: **{post.total_awards_received}**\n'
        f':speech_balloon: **{post.num_comments}**'
    )

    if post.post_hint == 'image':
        builder.set_image(url=post.url)
    elif post.thumbnail is not None and post.thumbnail.startswith('http'):
        builder.set_image(url=post.thumbnail)
    if post.post_hint in ('link', 'rich:video'):
        trunc = post.url[:40]
        builder.embed.description += '\n\n**[%s...](%s)**' % (trunc, post.url)
    elif post.post_hint in (None, 'self'):
        trunc = post.selftext[:min((len(post.selftext), 1000))]
        builder.embed.description += '\n\n' + trunc + '...'

    return builder


@command.invocation(
    f'{commands.prefix}reddit <subreddit> [post filter]'
)
@command.doc(
    'Sends a post from the subreddit'
)
@commands.command
async def reddit(
    evt: MessageCreateEvent,
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
            evt.message
        )
    except aiohttp.ClientError:
        raise command.CommandError('Sorry, that request failed', evt.message)
    finally:
        await client.close()

    try:
        post = random.choice(data['data']['children'])['data']
    except (IndexError, KeyError):
        raise commands.CommandError('Unable to parse that response', evt.message)
    post = RedditPost.unmarshal(post)

    if post.over_18 and not evt.message.channel.nsfw:
        raise command.CommandError(
            'That post is NSFW silly... try in an NSFW channel',
            evt.message
        )

    await form_embed(post).send_to(evt.channel)
