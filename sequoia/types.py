import dataclasses
import logging
import typing

import httpx

from sequoia.exceptions import DiscoveryResourcesError, DiscoveryServicesError, ResourceNotFound, ServiceNotFound

logger = logging.getLogger(__name__)

__all__ = ["Resource", "ResourcesRegistry", "Service", "ServicesRegistry"]


@dataclasses.dataclass
class Resource:
    """
    Representation of a resource part of a Sequoia service.
    """

    name: str
    path: str


class ResourcesRegistry(dict):
    """
    Mapping of available resources by name.
    """

    def __getitem__(self, key: str) -> Resource:
        try:
            return super().__getitem__(key)
        except KeyError:
            raise ResourceNotFound(key)


@dataclasses.dataclass
class Service:
    """
    Representation of a Sequoia service.
    """

    name: str
    url: str
    title: typing.Optional[str] = dataclasses.field(default=None, hash=False, compare=False)
    description: typing.Optional[str] = dataclasses.field(default=None, hash=False, compare=False)

    async def discover(self):
        """
        Request a service description endpoint to discover its resources and metadata.
        """
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                response = await client.get(f"{self.url}/descriptor/raw/")
                response.raise_for_status()
                response = response.json()

                self.title = response["title"]
                self.description = response["description"]
                self._resources = ResourcesRegistry(
                    {
                        i["hyphenatedPluralName"].replace("-", "_"): Resource(
                            name=i["pluralName"], path=f"{i['path']}/{i['hyphenatedPluralName']}"
                        )
                        for i in response["resourcefuls"].values()
                    }
                )
            except KeyError:
                logger.exception("Wrong response retrieving description of service '%s': %s", self.name, str(response))
                raise DiscoveryResourcesError(service=self.name)
            except (httpx.exceptions.HTTPError, OSError):
                raise DiscoveryResourcesError(service=self.name)

    @property
    async def resources(self) -> ResourcesRegistry:
        """
        Return the registry containing all the resources that are part of this service. This registry will be loaded
        when requested, following lazy pattern.

        :return: Resources registry.
        """
        if not hasattr(self, "_resources"):
            await self.discover()

        return self._resources


class ServicesRegistry(dict):
    """
    Mapping of available services by name.
    """

    def __getitem__(self, item):
        try:
            value = super().__getitem__(item)
        except KeyError:
            raise ServiceNotFound(item)

        return value

    async def discover(self, registry_url: str, owner: typing.Optional[str] = None):
        """
        Request Registry service to update the list of all available services.

        :return: Services registry.
        """
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                response = await client.get(f"{registry_url}/services/{owner or 'root'}/")
                response.raise_for_status()
                response = response.json()

                self.clear()
                self.update(
                    sorted(
                        {i["name"]: Service(name=i["name"], url=i["location"]) for i in response["services"]}.items()
                    )
                )
            except KeyError:
                logger.exception("Wrong response retrieving list of services from 'registry': %s", str(response))
                raise DiscoveryServicesError()
            except (httpx.exceptions.HTTPError, OSError):
                raise DiscoveryServicesError()
