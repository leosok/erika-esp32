import asyncio
import datetime
import json
import logging
import os

from twikit.client.client import Client

from typewriter.utils.mqtt_utils import send_print_message, send_mqtt_message
from .base import MQTTPlugin







class TwitterPlugin(MQTTPlugin):
    def __init__(self):
        super().__init__()
        self.client = Client('en-US')
        self.latest_tweet_time = {}

        # Run the login coroutine using the private _run_async method.
        self._run_async(self._login())

    async def _login(self):
        try:
            await self.client.login(
                auth_info_1=os.getenv('TWITTER_USERNAME'),
                auth_info_2=os.getenv('TWITTER_EMAIL'),
                password=os.getenv('TWITTER_PASSWORD'),
                cookies_file='twitter_cookies.json'
            )
            self.logger.info("Successfully logged in to Twitter")
        except Exception as e:
            self.logger.error(f"Failed to login to Twitter: {e}")

    def _run_async(self, coroutine) -> any:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coroutine)
        finally:
            loop.close()

    async def fetch_tweets(self, hashtag: str, last_tweet_id: str = "42") -> (str, int):
        """
        Fetch tweets with a given hashtag.
        :param hashtag: The hashtag to search for.
        :param last_tweet_id: The ID of the last tweet fetched.

        :return: A tuple containing the tweet text and the ID of the latest tweet.
        """
        tweets = await self.client.search_tweet(f"#{hashtag}", 'Latest', count=3)
        if not tweets:
            return None

        latest_tweet = tweets[0]
        if latest_tweet.id != last_tweet_id:
            return f"@{latest_tweet.user.name}: {latest_tweet.full_text}", latest_tweet.id
        else:
            logging.info(f"no new tweets for {hashtag}. Last tweet from: {latest_tweet.created_at}")


    def handle_message(self, typewriter_id: str, payload: dict) -> bool:
        try:
            hashtag = payload['query']
            last_tweet_id = payload.get('last_tweet_id')
            tweet_text, new_tweet_id = self._run_async(self.fetch_tweets(hashtag, last_tweet_id))

            if tweet_text:
                payload = json.dumps({
                    "text": tweet_text,
                    "id": new_tweet_id
                })

                logging.info(payload)
                # send_mqtt_message(
                #     typewriter_uuid=typewriter_id,
                #     topic=f'erika/twitter/{typewriter_id}',
                #     payload=payload
                # )
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error in handle_message: {e}")
            return False


if __name__ == '__main__':
    t= TwitterPlugin()
