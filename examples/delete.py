#!/usr/bin/env python3
import sequoia
import asyncio

async def delete():
  async with sequoia.Client(owner="metadata-dev-master", client_id="tool-qa-automation", client_secret="testingisgoodforyou", registry_url="http://registry.internal.sandbox.eu-west-1.palettedev.aws.pikselpalette.com") as client:
    await client.metadata.contents.delete(pk="metadata-dev-master:sdk-test-1")

if __name__ == "__main__":
  asyncio.run(delete())    

