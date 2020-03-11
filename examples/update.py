#!/usr/bin/env python3
import asyncio

import sequoia

content = """
    {
      "owner": "metadata-dev-master",
      "name": "sdk-test-1",
      "type": "episode",
      "title": "a new title",      
      "tags": [
         "agc_tests1"
       ]
    }
"""


async def update():
    async with sequoia.Client(
        owner="metadata-dev-master",
        client_id="tool-qa-automation",
        client_secret="testingisgoodforyou",
        registry_url="http://registry.internal.sandbox.eu-west-1.palettedev.aws.pikselpalette.com",
    ) as client:
        res = await client.metadata.contents.update(pk="metadata-dev-master:sdk-test-1", json=content)
        print(res)


if __name__ == "__main__":
    asyncio.run(update())
