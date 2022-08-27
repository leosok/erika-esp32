from mqtt_connection import ErikaMqqt
from plugins.erika_plugin_base import ErikaBasePlugin
import json
import mrequests as requests # type: ignore
import uasyncio as uasyncio

class Twitter(ErikaBasePlugin):
    
    info = "Ein Plugin das Twitter Hashtags aboniert. ON/OFF"
    wait_between_requests = 10 # seconds

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
            self.hashtag = await self.erika.ask("Welchem Hashtag soll ich folgen?")
            print("Folge dem Hashtag '{}'".format(self.hashtag))
            
            while self.active:
            # This will ask the Cloud to send a tweet to the Typewriter
                await self.request_tweet()          
                asyncio.sleep(self.wait_between_requests)
            print("Twitter Plugin was stopped.")


    def on_message(self, topic: str, msg: str):
        return super().on_message(topic, "Twitter-Plugin received: "+msg)


    async def request_tweet(self):
        if self.active:
            channel_name = self.erika_mqqt._get_channel_name(self.topic)
            print("sending {msg} to {channel_name}".format(msg=msg, channel_name=channel_name))
            
            payload = {
                "cmd": "twitter", 
                "query": self.hashtag,
                "last_tweet_id": self.last_tweet_id
                }

            await self.erika_mqqt.client.publish(channel_name, json.dumps(payload), qos=1)
