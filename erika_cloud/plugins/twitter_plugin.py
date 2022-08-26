from datetime import datetime
import time
from dataclasses import dataclass
import tweepy
import json
import logging


@dataclass
class TwitterResult:
    text:str = None
    username:str = None
    id:int = None
    created_at_iso:str = None


    def to_json(self):
        json.dumps(self.__dict__)


def get_new_tweet(query_str: str, bearer_token: str, since_id: int = None, get_username: bool = False) -> TwitterResult:

    client = tweepy.Client(bearer_token)

    query = f"{query_str} -is:retweet -is:quote -has:links"

    try:

        logging.info(f"Searching for {query}")
    
        response = client.search_recent_tweets(
            query,
            max_results=10,
            tweet_fields=[
                "created_at",
                "author_id"
            ],
            since_id=since_id)

        last_tweet = response.data[0]
        last_tweet_id = response.data[0].id

        if get_username:
            username = client.get_user(id=last_tweet.author_id).data.username
        else:
            username = None

        result = TwitterResult(
            text=last_tweet.text,
            id=last_tweet_id,
            created_at_iso= last_tweet.created_at.isoformat(),
            username=username
        )
        return result

    except TypeError as e:
        return 0  # no new tweets


if __name__ == "__main__":

    last_tweet_id = None
    import os

    query = "Trump"

    TWIITTER_BEARER_TOKEN =  os.environ.get("TWIITTER_BEARER_TOKEN")
    print(TWIITTER_BEARER_TOKEN)

    print("Starting twitter plugin: every 10 seconds")
    for i in range(10, 0, -1):
        tweet = get_new_tweet(
            query_str=query, 
            bearer_token=TWIITTER_BEARER_TOKEN,
            since_id=last_tweet_id)
        if tweet:
            print(
                f"username: @{tweet.username} - urL: https://twitter.com/random/status/{tweet.id} \n {tweet.text} \n\n")
        else:
            print("No new tweets")
        last_tweet_id = tweet.id
        time.sleep(10)
