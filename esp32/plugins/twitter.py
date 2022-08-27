from mqtt_connection import ErikaMqqt
from plugins.erika_plugin_base import ErikaBasePlugin
import json
import mrequests as requests # type: ignore
import uasyncio as asyncio

class Twitter(ErikaBasePlugin):
    
    info = "Ein Plugin das Twitter Hashtags aboniert. ON/OFF"
    wait_between_requests = 45 # seconds

    def __init__(self, erika:Erika=None, erika_mqqt:ErikaMqqt=None): # type: ignore
        self.last_tweet_id = None
        self.hashtag = None

        super().__init__(
            erika=erika, 
            erika_mqqt=erika_mqqt,
            #active=True
            )

    async def activate(self, active:bool):
        await super().activate(active)
        print("I think Twitter was activated")
        if self.active:
            print("Twitter Plugin is ON")
            self.hashtag = await self.erika.ask("Hashtag")
            # self.hashtag = "Trump"
            print("Folge dem Hashtag '{}'".format(self.hashtag))
            
            while self.active:
            # This will ask the Cloud to send a tweet to the Typewriter
                print("Requesting new Tweet")
                await self.request_tweet()          
                await asyncio.sleep(self.wait_between_requests)
        else:
            print("Twitter Plugin was stopped.")


    def on_message(self, topic: str, msg: str):
        print(f"Twitter-Plugin received: {msg} on {topic}")
        if not "cmd" in msg:
            payload = json.loads(msg)
            text = payload["text"] + "\n --------- "
            id = payload["id"]
            self.last_tweet_id = id
            asyncio.create_task(self.erika.print_text(
                text, linefeed=True))
        else:
            print("Ignoring own cmd")
            


    async def request_tweet(self):
        if self.active:
            channel_name = self.erika_mqqt._get_channel_name(self.topic)
             
            payload = {
                "cmd": "get_tweets", 
                "query": self.hashtag,
                "last_tweet_id": self.last_tweet_id
                }
            
            print(f"Publishing {payload} to '{channel_name}'")
            await self.erika_mqqt.client.publish(channel_name, json.dumps(payload), qos=1)
