import asyncio
import elbus_async
import threading
import time
import random
from tqdm import tqdm

iters = 100_000
workers = 1

cnt = 0


async def on_frame(frame):
    global cnt
    cnt += 1


async def test(w, iters):
    try:
        global cnt
        payload = b'\x01' * 10
        name = f'test{random.randint(0,1000_000)}-{w}'
        path = '/tmp/elbus.sock'
        # path = 'localhost:9924'
        bus = elbus_async.client.Client(path, name)
        bus.on_frame = on_frame
        await bus.connect()
        print(f'Connected to {path}')
        for i in range(iters):
            frame = elbus_async.client.Frame(payload,
                                             tp=elbus_async.client.OP_MESSAGE)
            frame.qos = 0
            b = await bus.send('y', frame)
            if not await b.wait_completed(timeout=1):
                raise TimeoutError
            # await asyncio.sleep(0.0000001)
            cnt += 1
        # await bus.disconnect()
    except Exception as e:
        import traceback
        traceback.print_exc()


async def main():
    started = time.perf_counter()
    for w in range(workers):
        asyncio.ensure_future(test(w, int(iters / workers)))
    await asyncio.sleep(0.01)
    with tqdm(total=iters) as pbar:
        prev = 0
        while cnt < iters:
            await asyncio.sleep(0.01)
            pbar.update(cnt - prev)
            prev = cnt
    pbar.update(iters)
    elapsed = time.perf_counter() - started
    speed = round(iters / elapsed)
    print(speed, 'iters/s')
    print(f'{round(1_000_000/speed)} us per iter')


asyncio.run(main())
time.sleep(1)