#!/usr/bin/env python3
import sequoia
import asyncio

async def retrieve():
  async with sequoia.Client(owner="metadata-dev-master", client_id="metadata-team-client", client_secret="metadataTeamRocks", registry_url="http://registry.internal.sandbox.eu-west-1.palettedev.aws.pikselpalette.com") as client:
    res = await client.metadata.contents.retrieve(pk="metadata-dev-master:sdk-test-1")
    print(res)

if __name__ == "__main__":
  asyncio.run(retrieve())    

