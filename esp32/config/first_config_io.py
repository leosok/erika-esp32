import uasyncio as asyncio
from erika import Erika


async def start_first_config(erika:Erika):
    if await erika.ask("Do you want to answer questions?", ask_bool=True):
        user_name = await erika.ask("Wie heißt du?")
        await erika.print_text("Hallo {}!".format(user_name))
    else:
        await erika.print_text("Ok, dann nicht.")