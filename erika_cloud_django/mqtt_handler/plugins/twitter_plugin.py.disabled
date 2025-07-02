import asyncio
import datetime
import json
import logging
import os
import re
import threading
from dataclasses import dataclass
from typing import Optional, Union

import pendulum
from django.conf.global_settings import TIME_ZONE
from twikit.client.client import Client

from typewriter.utils.mqtt_utils import send_print_message, send_mqtt_message
from .base import MQTTPlugin

#logger = logging.getLogger('twitter_plugin')

@dataclass
class TwitterResponse:
    text:str = None
    user_name:str = None
    id:str = None
    created_at: Optional[datetime] = None


    def to_json(self) -> str:
        json.dumps(self.__dict__)

    def as_json_payload(self) -> str:
        return json.dumps({
            "text": self.text,
            "id": self.id
        })


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

    async def fetch_tweets(self, hashtag: str, last_tweet_id: str = "42") -> TwitterResponse:
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
        ignore_tweet = False

        self.logger.info(f"Latest tweet for {hashtag}: {latest_tweet} {latest_tweet.text}")
        # remove all urls from tweet starting with " https://t.co". there might be multiple urls in a tweet
        tweet_text = re.sub(r' https://t.co\S+', '', latest_tweet.text)

        if all(word.startswith('#') for word in tweet_text.split()):
            # ignore if the tweet is only composed from hashtags as text like
            # '#poetry #literature #reading #queer #lesung #berlin #berlinliterature #berlinstories #berlinevents #berlinwriters #berlinreading'
            ignore_tweet = True
            self.logger.info(f"Ignoring tweet with only hashtags: {tweet_text}")

        if latest_tweet.id != last_tweet_id and not ignore_tweet:
            return TwitterResponse(
                text=tweet_text,
                user_name=latest_tweet.user.screen_name,
                id=latest_tweet.id,
                created_at=latest_tweet.created_at_datetime
            )
        else:
            self.logger.info(f"No new tweets for {hashtag}. Last tweet from: {latest_tweet.created_at}")
            return None

    def _format_tweet(self, tweet: TwitterResponse) -> TwitterResponse:
        """
        format tweet for printing.
        """
        nice_time = pendulum.instance(tweet.created_at).in_timezone(TIME_ZONE).format("D.M.Y HH:MM")
        template = f"""{nice_time} @{tweet.user_name}
        {tweet.text} 
        """
        tweet.text = template
        return tweet

    def handle_message(self, typewriter_id: str, payload: dict) -> bool:
        try:
            hashtag = payload['query']
            last_tweet_id = payload.get('last_tweet_id')

            # Execute fetch_tweets in the dedicated event loop
            result = self._run_async_in_loop(self.fetch_tweets(hashtag, last_tweet_id))
            logging.info(f"New tweet from {hashtag}: {result}")
            if result:
                # create a nice text to print
                payload = self._format_tweet(result).as_json_payload()

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