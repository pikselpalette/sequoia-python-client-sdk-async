#!/usr/bin/env python3
import asyncio

import sequoia


async def get_offer():
    async with sequoia.Client(
        owner="metadata-dev-master",
        client_id="tool-qa-automation",
        client_secret="testingisgoodforyou",
        registry_url="http://registry.internal.sandbox.eu-west-1.palettedev.aws.pikselpalette.com",
    ) as client:
        async for res in client.metadata.contents.list(
            params={"withCreatedAt": "2020-03-02T14:00:00.000Z/", "perPage": "2"}
        ):
            print(res)


if __name__ == "__main__":
    asyncio.run(get_offer())
