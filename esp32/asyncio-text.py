# import uasyncio as asyncio
# from primitives.queue import Queue
# import random

# async def produce(queue, n):
#     for x in range(1, n + 1):
#         # produce an item
#         print('producing {}/{}'.format(x, n))
#         # simulate i/o operation using sleep
#         await asyncio.sleep(random.random())
#         item = str(x)
#         # put the item in the queue
#         await queue.put(item)

#     # indicate the producer is done
#     await queue.put(None)


# async def consume(queue):
#     while True:
#         # wait for an item from the producer
#         item = await queue.get()
#         if item is None:
#             # the producer emits None to indicate that it is done
#             break

#         # process the item
#         print('consuming item {}...'.format(item))
#         # simulate i/o operation using sleep
#         await asyncio.sleep(random.random())


# loop = asyncio.get_event_loop()
# queue = Queue()
# producer_coro = produce(queue, 10)
# consumer_coro = consume(queue)
# loop.run_until_complete(asyncio.gather(producer_coro, consumer_coro))
# loop.close()
import uasyncio as asyncio
from primitives.queue import Queue

async def slow_process():
    await asyncio.sleep(2)
    return 42

async def produce(queue):
    print('Waiting for slow process.')
    result = await slow_process()
    print('Putting result onto queue')
    await queue.put(result)  # Put result on queue

async def consume(queue):
    print("Running consume()")
    result = await queue.get()  # Blocks until data is ready
    print('Result was {}'.format(result))

async def queue_go(delay):
    queue = Queue()
    asyncio.create_task(consume(queue))
    asyncio.create_task(produce(queue))
    await asyncio.sleep(delay)
    print("Done")

asyncio.run(queue_go(4))