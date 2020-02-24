<p align="center">
  <a href="https://piksel.com/product/piksel-palette/"><img src="https://pikselgroup.com/broadcast/wp-content/uploads/sites/3/2017/09/P-P.png" alt='Piksel Palette'></a>
</p>


# Sequoia Client SDK Async

Python asyncio based SDK for interacting with Piksel Palette services, providing a high level interface to ease the 
development of different pieces on top of this ecosystem.

Among other characteristics it provides the following:

* **Authentication** flow integrated and transparent.
* **Async** requests based on `asyncio` engine providing a high throughput.
* **Discovery** for Sequoia services, API resources and methods.
* **Lazy loading** to avoid use and discover not needed elements.
* **Pagination** automatically handled using continue-based pagination. It's completely transparent to client users.

## Requirements

* [Python] 3.6+

## Installation

```console
$ pip install sequoia-client-sdk-async
```

## Usage

The client understand three kind of elements:
* `Service`: Sequoia service against to the request will be performed.
* `Resource`: An specific resource of previous service.
* `Method`: Operation that will be performed (`create`, `retrieve`, `update`, `delete`, `list`).

The syntax to interact with the client is the following for a resource (`create`, `retrieve`, `update`, `delete`):

```python
await client.service.resource.method(params={}, headers={})
```

And the next one for interacting with collections (`list`):

```python
async for item in client.service.resource.method(params={}, headers={}):
    ...  # Do something
```


## Examples

Here is a list of some client usage examples.

### Iterate over a list of metadata offers filtered by availabilityStartAt
```python
import sequoia

async with sequoia.Client(client_id="foo", client_secret="bar", registry_url="https://foo.bar") as client:
    async for offer in client.metadata.offers.list(params={"withAvailabilityStartAt": "2000-01-01T00:00:00.000Z"}):
        ...  # Do fancy things with this offer
```

### Create a metadata offer
```python
import sequoia

async with sequoia.Client(client_id="foo", client_secret="bar", registry_url="https://foo.bar") as client:
    await client.metadata.offers.create(json={"foo": "bar"})
```

### Retrieve a metadata offer
```python
import sequoia

async with sequoia.Client(client_id="foo", client_secret="bar", registry_url="https://foo.bar") as client:
    offer = await client.metadata.offers.retrieve(pk="foo")
```

### Update a metadata offer
```python
import sequoia

async with sequoia.Client(client_id="foo", client_secret="bar", registry_url="https://foo.bar") as client:
    await client.metadata.offers.update(pk="foo", json={"foo": "bar"})
```

### Delete a metadata offer
```python
import sequoia

async with sequoia.Client(client_id="foo", client_secret="bar", registry_url="https://foo.bar") as client:
    await client.metadata.offers.delete(pk="foo")
```

[Python]: https://www.python.org
