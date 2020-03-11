#!/usr/bin/env python3
import sequoia
import asyncio

content = """
    {
      "owner": "metadata-dev-master",
      "name": "sdk-test-2",
      "type": "episode",
      "title": "OD movie 10",
      "longSynopsis": "Long Synopsis content-10",
      "localisedLongSynopsis": {
        "en": "The long synopsis of the content",
        "it": "Sinopsi lunga del maldito contenuto",
        "es": "La sysnopsis larga de este contenido"
      }, 
      "mediumSynopsis": "Medium synopsis for Interstellar1...",
      "shortSynopsis": "Short synopsis for Interstellar...",
      "releaseYear": 2018,
      "duration": "PT1H20M",
      "availabilityStartAt": "2019-01-01T12:00:00.000Z",
      "availabilityEndAt": "2022-01-01T12:00:00.000Z",
      "ratings": {
        "BBFC": "PG"
      },
      "tags": [
         "agc_tests1"
       ],
      "active": true,
      "categoryRefs": [
        "metadata-dev-master:category-1",
        "metadata-dev-master:category-2",
        "metadata-dev-master:category-5"
      ],
      "custom": {
         "guidanceText": "My guidance text in english",
         "anotherLocalisedCustomField": "in english",
         "anotherKey": "anotherValue"
      },
      "productionLocations":["GB", "CH", "CH"]
    }
"""

async def create():
  async with sequoia.Client(owner="metadata-dev-master", client_id="tool-qa-automation", client_secret="testingisgoodforyou", registry_url="http://registry.internal.sandbox.eu-west-1.palettedev.aws.pikselpalette.com") as client:
    res = await client.metadata.contents.create(json=content)
    print(res)

if __name__ == "__main__":
  asyncio.run(create())    

