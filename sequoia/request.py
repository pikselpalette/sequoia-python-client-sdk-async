import json as jsonlib
import logging
import typing
from functools import wraps
from json import JSONDecodeError
from urllib.parse import parse_qsl, urljoin, urlparse, urlunparse

import httpx
import httpx.content_streams

from sequoia.codecs import JSONEncoder
from sequoia.exceptions import RequestAlreadyBuilt, RequestNotBuilt
from sequoia.response import Response
from sequoia.types import Resource, Service, ServicesRegistry

logger = logging.getLogger(__name__)

__all__ = ["Request", "RequestBuilder"]


class JSONStream(httpx.content_streams.JSONStream):
    def __init__(self, json: typing.Any) -> None:
        self.body = jsonlib.dumps(json, cls=JSONEncoder).encode("utf-8")


class Request(httpx.Request):
    """
    Low level request interface for interact with Sequoia services.
    """

    def __init__(self, *args, json: typing.Any = None, **kwargs):
        if json is not None:
            kwargs["stream"] = JSONStream(json)

        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:
        params = {
            "method": self.method,
            "url": str(self.url),
            "headers": dict(self.headers),
        }
        try:
            params["content"] = repr(self.content.decode("utf-8"))
        except httpx.exceptions.RequestNotRead:
            pass

        formatted_params = ", ".join([f"{k}={v}" for k, v in params.items()])
        return f"<{self.__class__.__name__}({formatted_params})>"


def built(service: bool = False, resource: bool = False) -> typing.Callable:
    """
    Decorator to check if the request is fully built, raising exceptions if it isn't.

    :param service: Check the service is defined.
    :param resource: Check the resource is defined.
    :raise RequestNotBuilt: If the request build is not finished yet.
    """

    def _built(f: typing.Callable) -> typing.Callable:
        @wraps(f)
        def _wrapper(self, *args, **kwargs):
            if (service or resource) and self._service_name is None:
                raise RequestNotBuilt("service")

            if resource and self._resource_name is None:
                raise RequestNotBuilt("resource")

            return f(self, *args, **kwargs)

        return _wrapper

    return _built


class RequestBuilder:
    """
    Helper for building requests to Sequoia services.
    """

    def __init__(
        self,
        httpx_client: httpx.AsyncClient,
        available_services: ServicesRegistry,
        service: typing.Optional[str] = None,
        resource: typing.Optional[str] = None,
        owner: typing.Optional[str] = None,
        token: typing.Optional[str] = None,
    ):
        """
        Helper for building requests to Sequoia services.

        :param httpx_client: Httpx client, a mechanism to reuse an already created client.
        :param available_services: Mapping of available services by name.
        :param service: Sequoia service name.
        :param resource: Sequoia resource name.
        :param owner: Owner.
        :param token: Sequoia authentication token.
        """
        self._owner = owner
        self._token = token
        self._httpx_client = httpx_client
        self._available_services = available_services
        self._service_name = service
        self._resource_name = resource

    @property
    @built(service=True)
    def _service(self) -> Service:
        """
        Return the service object referenced by self._service property.

        :return: Service object.
        """
        return self._available_services[self._service_name]

    @property
    @built(service=True, resource=True)
    async def _resource(self) -> Resource:
        """
        Return the resource object referenced by self._resource property.

        :return: Resource object.
        """
        return (await self._service.resources)[self._resource_name]

    def _build_service(self, service: str) -> "RequestBuilder":
        """
        Add service into the builder.

        :param service: Service name to add into request.
        :return: New instance of RequestBuilder including the service.
        """
        return RequestBuilder(
            httpx_client=self._httpx_client,
            available_services=self._available_services,
            service=service,
            resource=self._resource_name,
            owner=self._owner,
            token=self._token,
        )

    def _build_resource(self, resource: str) -> "RequestBuilder":
        """
        Add resource into the builder.

        :param resource: Sequoia resource name to add into request.
        :return: New instance of RequestBuilder including the path.
        """

        return RequestBuilder(
            httpx_client=self._httpx_client,
            available_services=self._available_services,
            service=self._service_name,
            resource=resource,
            owner=self._owner,
            token=self._token,
        )

    async def custom(self, path: str, method: str = "GET", **kwargs) -> typing.Dict[typing.Any, typing.Any]:
        """
        Build a request using a custom path.

        :param path: Custom path.
        :param method: HTTP method.
        :param kwargs: Request keyword arguments.
        :return: Response from custom request.
        """
        return (await self._request(method=method, url=urljoin(self._service.url, path), **kwargs)).json()

    def __getattr__(self, item) -> typing.Union[Request, "RequestBuilder"]:
        if self._service_name is None:
            # First step: Service is not defined yet
            return self._build_service(item)
        elif self._resource_name is None:
            # Second step: Service is defined but path is not
            return self._build_resource(item)

        raise RequestAlreadyBuilt

    # HTTP Methods
    async def create(self, json, **kwargs) -> typing.Dict[typing.Any, typing.Any]:
        """
        Create a new resource.

        :param json: JSON body to send.
        :return: Response.
        """
        resource_name = (await self._resource).name
        kwargs["json"] = {resource_name: [json]}

        return (await self._request(method="POST", url=await self._build_url(), **kwargs)).json()[resource_name][0]

    async def retrieve(self, pk: str, **kwargs) -> typing.Dict[typing.Any, typing.Any]:
        """
        Retrieve a resource given its primary key.

        :param pk: Resource primary key.
        :return: Response
        """
        return (await self._request(method="GET", url=await self._build_url(pk), **kwargs)).json()[
            (await self._resource).name
        ][0]

    async def update(self, pk: str, json, **kwargs) -> typing.Dict[typing.Any, typing.Any]:
        """
        Update a resource given its primary key.

        :param pk: Resource primary key.
        :param json: JSON body to send.
        :return: Response
        """
        resource_name = (await self._resource).name
        kwargs["json"] = {resource_name: [json]}

        return (await self._request(method="PUT", url=await self._build_url(pk), **kwargs)).json()[resource_name][0]

    async def delete(self, pk: str, **kwargs) -> None:
        """
        Delete a resource given its primary key.

        :param pk: Resource primary key.
        """
        await self._request(method="DELETE", url=await self._build_url(pk), **kwargs)

    async def list(self, **kwargs) -> typing.AsyncGenerator[typing.Dict[typing.Any, typing.Any], None]:
        """
        Retrieve a collection.

        :return: Response
        """
        url = await self._build_url()
        kwargs["params"] = {**kwargs.get("params", {}), **{"continue": True}}
        while url:
            response = (await self._request(method="GET", url=url, **kwargs)).json()

            for item in response[(await self._resource).name]:
                yield item

            if response["meta"].get("continue"):
                parsed_url = urlparse(urljoin(self._service.url, response["meta"].get("continue")))

                # Update url and params
                kwargs["params"] = {**kwargs.get("params", {}), **dict(parse_qsl(parsed_url.query))}
                url = urlunparse([parsed_url.scheme, parsed_url.netloc, parsed_url.path, None, None, None])
            else:
                url = None

    async def _request(
        self, method: str, url: str, *args, owner: bool = True, token: bool = True, **kwargs
    ) -> Response:
        """
        Default request proxy method.

        :param method: HTTP method.
        :param url: Request url.
        :param kwargs: Request keyword arguments.
        :param owner: If true the owner param will be injected.
        :param token: If true the authorization token will be injected.
        :return: JSON-serialized response.
        :raise httpx.exceptions.HTTPError: Request error.
        """
        self.method = method.upper()
        self.url = url

        # Add owner if necessary
        if owner and self._owner is not None:
            kwargs["params"] = {"owner": self._owner, **kwargs.get("params", {})}

        # Content-Type
        kwargs["headers"] = {
            **kwargs.get("headers", {}),
            **{"Content-Type": "application/vnd.piksel+json", "Accept-Encoding": "identity"},
        }

        # Authorization token
        if token and self._token:
            kwargs["headers"]["Authorization"] = f"Bearer {self._token}"

        try:
            request = Request(method=self.method, url=self.url, **kwargs)
            logger.debug("Request: %r", request)
            response = await self._httpx_client.send(request=request)
            response.raise_for_status()
            response = Response(response=response)
            response.json()  # Parse immediately to check there is no error and cache json
        except httpx.exceptions.ResponseNotRead:
            pass
        except httpx.exceptions.HTTPError as e:
            logger.error(
                "Error %d requesting (%s) '%s': %s", e.response.status_code, self.method, self.url, e.response.content
            )
            raise
        except JSONDecodeError:
            logger.error("Wrong response from service '%s': %r", self._service.name, response)
            raise
        else:
            logger.debug("Response: %r", response)

        return response

    async def _build_url(self, pk: str = None) -> str:
        """
        Build request url by joining service base url, resource path and, if specified, the primary key.

        :param pk: Resource primary key.
        :return: Full URL.
        """
        # Build path
        path = (await self._resource).path
        if pk is not None:
            path += f"/{pk}"

        return urljoin(self._service.url, path)

    def __repr__(self):
        params = ", ".join([f"{i}={getattr(self, i)}" for i in ("service", "resource")])
        return f"RequestBuilder({params})"

    def __eq__(self, other):
        return (
            isinstance(other, RequestBuilder)
            and self._service_name == other._service_name
            and self._resource_name == other._resource_name
            and self._owner == other._owner
            and self._token == other._token
        )
