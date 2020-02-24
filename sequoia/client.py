import base64
import logging
import typing

import httpx

from sequoia.exceptions import ClientNotInitialized, UpdateTokenError
from sequoia.request import RequestBuilder
from sequoia.types import Resource, Service, ServicesRegistry

logger = logging.getLogger(__name__)

__all__ = ["Client"]


class Client:
    """
    Client to interact with Sequoia services.
    """

    request_builder = RequestBuilder

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        registry_url: str,
        owner: typing.Optional[str] = None,
        httpx_client: typing.Optional[httpx.AsyncClient] = None,
    ) -> None:
        """
        Client to interact with Sequoia services.

        :param client_id: Sequoia client ID.
        :param client_secret: Sequoia client secret.
        :param registry_url: URL for Registry service.
        :param owner: Owner.
        :param httpx_client: Httpx client, a mechanism to reuse an already created client.
        """
        self._registry_url = registry_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._httpx_client = httpx_client if httpx_client is not None else httpx.AsyncClient(verify=False)
        self._token: typing.Optional[str] = None
        self._owner = owner
        self._services: ServicesRegistry = ServicesRegistry()

    async def set_owner(self, owner: str):
        """
        Set owner and retrieve services list.

        :param owner: Owner.
        """
        self._owner = owner
        await self.update_services()

    def services(self) -> typing.Dict[str, Service]:
        """
        List the available services.

        :return: Available services.
        """
        return dict(self._services)

    async def resources(
        self, service: typing.Optional[str] = None
    ) -> typing.Union[typing.Dict[str, typing.Dict[str, Resource]], typing.Dict[str, Resource]]:
        """
        List the available resources for all services or the specified one.

        :param service: If specified, only shows resources for this service.
        :return: Available resources.
        """
        if service is None:
            return {k: dict(await v.resources) for k, v in self._services.items()}

        return dict(await self._services[service].resources)

    @property
    def _builder(self) -> RequestBuilder:
        """
        Create a new instance of request builder.

        :return: Request builder instance.
        """
        if not self._services:
            raise ClientNotInitialized

        return self.request_builder(
            httpx_client=self._httpx_client, available_services=self._services, owner=self._owner, token=self._token
        )

    async def update_services(self):
        """
        Update services registry and its resources using discovery methods.
        """
        await self._services.discover(self._registry_url, self._owner)

    async def update_token(self):
        """
        Request a new token from Identity to interact with Sequoia services.
        """
        encoded_auth = base64.b64encode(f"{self._client_id}:{self._client_secret}".encode()).decode()
        headers = {"Authorization": f"Basic {encoded_auth}"}
        data = {"grant_type": "client_credentials"}

        try:
            response = await self._httpx_client.post(
                f"{self._services['identity'].url}/oauth/token/", headers=headers, data=data
            )
            response.raise_for_status()
            response = response.json()
            token = response["access_token"]
        except KeyError:
            logger.exception("Wrong response retrieving token from 'identity': %s", str(response))
            raise UpdateTokenError()
        except (httpx.exceptions.HTTPError, OSError) as e:
            raise UpdateTokenError() from e

        self._token = token

    async def close(self) -> None:
        """
        Closes client connections.
        """
        self._token = None
        self._owner = None
        self._services.clear()
        await self._httpx_client.aclose()

    async def __aenter__(self) -> httpx.AsyncClient:
        await self.update_services()
        await self.update_token()
        return self

    async def __aexit__(
        self, exc_type: typing.Type[BaseException] = None, exc_value: BaseException = None, traceback=None
    ) -> None:
        await self.close()

    def __getattr__(self, item):
        return getattr(self._builder, item)
