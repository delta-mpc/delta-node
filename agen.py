import asyncio

async def agen():
    for _ in range(5):
        await asyncio.sleep(0.2)
        yield 1


async def main():
    count = 0
    gen = agen()
    while count < 6:
        try:
            count += await asyncio.wait_for(gen.asend(None), 0.1)
            print(count)
        except StopAsyncIteration:
            break
    await gen.aclose()


if __name__ == "__main__":
    asyncio.run(main())

