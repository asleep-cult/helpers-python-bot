import aiohttp
import constants
import random
from snakecord.message import Embed
from snakecord.utils import JsonStructure, JsonField

commands = constants.commands


class RedditPost(JsonStructure):
    __json_fields__ = {
        'subreddit': JsonField('subreddit'),
        'selftext': JsonField('selftext'),
        'author_fullname': JsonField('author_fullname'),
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

    async def request(self, subreddit, post_filter=None, count=30):
        if post_filter is None:
            post_filter = ''
        url = '%s/r/%s/%s/.json' % (self.BASE_URL, subreddit, post_filter)

        resp = await self.client_session.request(
            'GET', url, params={'count': count}
        )
        data = await resp.json()
        if resp.status != 200:
            raise RedditClientError(resp.status, data)
        return data

    async def close(self):
        await self.client_session.close()


@commands.command
async def reddit(message, subreddit, post_filter='new'):
    if subreddit.startswith('r/'):
        subreddit = subreddit[2:]

    client = RedditClient()
    data = await client.request(subreddit, post_filter)
    await client.close()

    try:
        post = random.choice(data['data']['children'])['data']
    except (IndexError, KeyError):
        await message.channel.send('Unable to parse that response')
        return
    post = RedditPost.unmarshal(post)

    if post.over_18 and not message.channel.nsfw:
        await message.channel.send(
            'That post is NSFW silly... try in an NSFW channel'
        )
        return

    embed = Embed(
        title=post.title,
        color=constants.BLUE,
        url='%s%s' % (RedditClient.BASE_URL, post.permalink),
        description=post.selftext
    )
    embed.set_author(name=post.author_fullname, icon_url=post.thumbnail)
    embed.description = (
        ':arrow_up: **%s** '
        ':arrow_down: **%s** '
        '(%s%%)\n'
        '**edited**: %s\n'
        '**nsfw**: %s\n'
        ':trophy: **%s**\n'
        ':speech_balloon: **%s**' % (
            post.ups, post.downs, post.upvote_ratio * 100,
            str(post.edited).lower(), str(post.over_18).lower(),
            post.total_awards_received, post.num_comments
        )
    )

    if post.post_hint == 'image':
        embed.set_image(url=post.url)
    elif post.post_hint == 'link':
        trunc = post.url[:40]
        embed.description += '\n\n**[%s...](%s)**' % (trunc, post.url)
    elif post.post_hint is None:
        trunc = post.selftext[:len(embed.description) -
                                min((len(post.selftext), 1500))] # noqa
        embed.description += '\n\n' + trunc + '...'

    await message.channel.send(embed=embed)
