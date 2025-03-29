import asyncio
import datetime
import json
import logging
import os
import threading

from twikit.client.client import Client

from typewriter.utils.mqtt_utils import send_print_message, send_mqtt_message
from .base import MQTTPlugin

#logger = logging.getLogger('twitter_plugin')


class TwitterPlugin(MQTTPlugin):
    def __init__(self):
        super().__init__()
        self.client = Client('en-US')
        self.latest_tweet_time = {}
        self.loop = None
        self.thread = None

        self._start_event_loop()
        self._run_async_in_loop(self._login())

    def _start_event_loop(self):
        """Start a new event loop in a dedicated thread."""
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(
            target=self._run_event_loop,
            args=(self.loop,),
            daemon=True
        )
        self.thread.start()

    @staticmethod
    def _run_event_loop(loop):
        """Run the event loop indefinitely."""
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def _run_async_in_loop(self, coroutine):
        """
        Run a coroutine in the dedicated event loop and wait for its result.
        """
        #Bugfix because logger somehow is set to WARNING in the new thread
        self.logger.setLevel(logging.INFO)
        future = asyncio.run_coroutine_threadsafe(coroutine, self.loop)
        return future.result()

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

    async def fetch_tweets(self, hashtag: str, last_tweet_id: str = "42"):
        """
        Fetch tweets with a given hashtag.
        :return: Tuple of (tweet_text, new_tweet_id) or None if no new tweets
        """
        self.logger.info("Fetching tweets for hashtag " + hashtag)
        tweets = await self.client.search_tweet(f"#{hashtag}", 'Latest', count=3)
        if not tweets:
            self.logger.info(f"No new tweets for {hashtag}")
            return None

        latest_tweet = tweets[0]
        self.logger.info(f"Latest tweet for {hashtag}: {latest_tweet}")
        if latest_tweet.id != last_tweet_id:
            return f"@{latest_tweet.user.name}: {latest_tweet.full_text}", latest_tweet.id
        else:
            self.logger.info(f"No new tweets for {hashtag}. Last tweet from: {latest_tweet.created_at}")
            return None

    def handle_message(self, typewriter_id: str, payload: dict) -> bool:
        try:
            hashtag = payload['query']
            last_tweet_id = payload.get('last_tweet_id')

            # Execute fetch_tweets in the dedicated event loop
            result = self._run_async_in_loop(self.fetch_tweets(hashtag, last_tweet_id))
            logging.info(f"New tweet from {hashtag}: {result}")
            if result:
                tweet_text, new_tweet_id = result
                payload = json.dumps({
                    "text": tweet_text,
                    "id": new_tweet_id
                })

                # Uncomment to send MQTT message
                send_mqtt_message(
                    typewriter_uuid=typewriter_id,
                    topic=f'erika/twitter/{typewriter_id}',
                    payload=payload
                )
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error in handle_message: {e}", exc_info=True)
            return False

if __name__ == '__main__':
    t = TwitterPlugin()