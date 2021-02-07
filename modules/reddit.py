import aiohttp
import constants
import random
from snakecord.message import Embed

commands = constants.commands


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

    # Yes, I know this is terrible. I'll make a class for it.
    post = random.choice(data['data']['children'])['data']
    embed = Embed(title=post['title'], color=constants.BLUE, url=post['url'])
    embed.set_image(url=post['url'])
    description = [
        ':arrow_up: **%s**' % post.get('ups', 'N/A'),
        ':arrow_down: **%s**' % post.get('downs', 'N/A')
    ]

    if post.get('edited', False):
        description.append('edited')
    embed.description = '\n'.join(description)

    await message.channel.send(embed=embed)
