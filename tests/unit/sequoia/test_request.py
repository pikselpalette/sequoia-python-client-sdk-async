import datetime
from json import JSONDecodeError
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from sequoia.exceptions import RequestAlreadyBuilt, RequestNotBuilt, ResourceNotFound, ServiceNotFound
from sequoia.request import RequestBuilder
from sequoia.response import Response
from sequoia.types import Resource, ResourcesRegistry, Service, ServicesRegistry


@pytest.fixture(scope="module")
def resource():
    return Resource(name="bar", path="/bar")


@pytest.fixture(scope="module")
def resources_registry(resource):
    return ResourcesRegistry({"bar": resource})


@pytest.fixture(scope="module")
def service(resources_registry):
    s = Service(name="foo", url="https://foo")
    s._resources = resources_registry
    return s


@pytest.fixture(scope="module")
def services_registry(service):
    return ServicesRegistry({"foo": service})


class TestCaseBuiltDecorator:
    @pytest.fixture(scope="class")
    def request_builder(self, services_registry):
        return RequestBuilder(
            httpx_client=AsyncMock(spec=httpx.AsyncClient), available_services=services_registry, max_retries=1
        )

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    def test_request_no_service(self, request_builder):
        with pytest.raises(RequestNotBuilt):
            request_builder._service

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_request_no_resource(self, request_builder):
        with pytest.raises(RequestNotBuilt):
            await request_builder.foo._resource


class TestCaseRequestBuilder:
    @pytest.fixture()
    async def httpx_client(self):
        response_mock = httpx.Response(request=Mock(), status_code=200, content=b'{"bar": [{"id": 1}]}')
        client = AsyncMock(spec=httpx.AsyncClient)
        client.send = AsyncMock(return_value=response_mock)
        return client

    @pytest.fixture()
    def request_builder(self, httpx_client, services_registry):
        return RequestBuilder(httpx_client=httpx_client, available_services=services_registry, max_retries=1)

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_build_request(self, request_builder):
        # Build request
        builder = request_builder.foo.bar

        # Asserts
        assert builder._owner is None
        assert builder._token is None
        assert builder._service == Service(name="foo", url="https://foo")
        assert await builder._resource == Resource(name="bar", path="/bar")
        assert builder._max_retries == 1

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    def test_build_request_error_already_built(self, request_builder):
        # Build request
        with pytest.raises(RequestAlreadyBuilt):
            request_builder.foo.bar.foo()

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_error_service_not_found(self, request_builder):
        with pytest.raises(ServiceNotFound):
            await request_builder.wrong.bar.retrieve(pk="1")

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_error_resource_not_found(self, request_builder):
        with pytest.raises(ResourceNotFound):
            await request_builder.foo.wrong.retrieve(pk="1")

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_build_request_custom(self, request_builder):
        # Build request
        await request_builder.foo.custom(
            "/foobar", method="POST", json={"foo": datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)}
        )

        # Asserts
        assert request_builder._httpx_client.send.call_count == 1
        request = request_builder._httpx_client.send.call_args_list[0][1]["request"]
        await request.aread()
        assert request.method == "POST"
        assert request.url == "https://foo/foobar"
        assert request.content == b'{"foo": "2000-01-01T00:00:00.000Z"}'

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_error_custom_no_service(self, request_builder):
        # Build request
        with pytest.raises(RequestNotBuilt):
            await request_builder.custom("/foobar")

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_create(self, request_builder):
        # Run
        response = await request_builder.foo.bar.create(
            json={"foo": datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)}
        )

        # Asserts
        assert request_builder._httpx_client.send.call_count == 1
        request = request_builder._httpx_client.send.call_args_list[0][1]["request"]
        await request.aread()
        assert request.method == "POST"
        assert request.url == "https://foo/bar"
        assert request.content == b'{"bar": [{"foo": "2000-01-01T00:00:00.000Z"}]}'
        assert response == {"id": 1}

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_retrieve(self, request_builder):
        # Run
        response = await request_builder.foo.bar.retrieve(pk="1")

        # Asserts
        assert request_builder._httpx_client.send.call_count == 1
        request = request_builder._httpx_client.send.call_args_list[0][1]["request"]
        await request.aread()
        assert request.method == "GET"
        assert request.url == "https://foo/bar/1"
        assert response == {"id": 1}

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_update(self, request_builder):
        # Run
        response = await request_builder.foo.bar.update(
            pk="1", json={"foo": datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)}
        )

        # Asserts
        assert request_builder._httpx_client.send.call_count == 1
        request = request_builder._httpx_client.send.call_args_list[0][1]["request"]
        await request.aread()
        assert request.method == "PUT"
        assert request.url == "https://foo/bar/1"
        assert request.content == b'{"bar": [{"foo": "2000-01-01T00:00:00.000Z"}]}'
        assert response == {"id": 1}

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_delete(self, request_builder):
        # Run
        response = await request_builder.foo.bar.delete(pk="1")

        # Asserts
        assert request_builder._httpx_client.send.call_count == 1
        request = request_builder._httpx_client.send.call_args_list[0][1]["request"]
        await request.aread()
        assert request.method == "DELETE"
        assert request.url == "https://foo/bar/1"
        assert response is None

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_list(self, request_builder):
        # Prepare
        responses = [
            httpx.Response(
                request=Mock(), status_code=200, content=b'{"meta": {"continue": "/bar?page=2"}, "bar": [{"id": 1}]}'
            ),
            httpx.Response(request=Mock(), status_code=200, content=b'{"meta": {}, "bar": [{"id": 2}]}'),
        ]
        request_builder._httpx_client.send = AsyncMock(side_effect=responses)

        # Run
        items = [i async for i in request_builder.foo.bar.list()]

        # Asserts
        assert request_builder._httpx_client.send.call_count == 2
        first_request = request_builder._httpx_client.send.call_args_list[0][1]["request"]
        await first_request.aread()
        assert first_request.method == "GET"
        assert first_request.url == "https://foo/bar?continue=true"
        second_request = request_builder._httpx_client.send.call_args_list[1][1]["request"]
        await second_request.aread()
        assert second_request.method == "GET"
        assert second_request.url == "https://foo/bar?continue=true&page=2"
        assert items == [{"id": 1}, {"id": 2}]

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_request(self, request_builder):
        # Prepare
        request_mock = AsyncMock(
            return_value=httpx.Response(request=Mock(), status_code=200, content=b'{"foo": "2000-01-01T00:00:00.000Z"}')
        )
        request_builder._httpx_client.send = request_mock

        # Run
        response = await request_builder._request(method="GET", url="https://foo/bar", params={"foo": "bar"})

        # Asserts
        assert request_builder._httpx_client.send.call_count == 1
        request = request_builder._httpx_client.send.call_args_list[0][1]["request"]
        await request.aread()
        assert request.method == "GET"
        assert request.url == "https://foo/bar?foo=bar"
        assert response.json() == {"foo": datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)}

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_request_inject_owner(self, request_builder):
        # Prepare
        request_mock = AsyncMock(
            return_value=httpx.Response(request=Mock(), status_code=200, content=b'{"foo": "2000-01-01T00:00:00.000Z"}')
        )
        request_builder._httpx_client.send = request_mock
        request_builder._owner = "root"

        # Run
        response = await request_builder._request(method="GET", url="https://foo/bar", params={"foo": "bar"})

        # Asserts
        assert request_builder._httpx_client.send.call_count == 1
        request = request_builder._httpx_client.send.call_args_list[0][1]["request"]
        await request.aread()
        assert request.method == "GET"
        assert request.url == "https://foo/bar?owner=root&foo=bar"
        assert response.json() == {"foo": datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)}

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_request_exclude_owner(self, request_builder):
        # Prepare
        request_mock = AsyncMock(
            return_value=httpx.Response(request=Mock(), status_code=200, content=b'{"foo": "2000-01-01T00:00:00.000Z"}')
        )
        request_builder._httpx_client.send = request_mock
        request_builder._owner = "root"

        # Run
        response = await request_builder._request(
            method="GET", url="https://foo/bar", params={"foo": "bar"}, owner=False
        )

        # Asserts
        assert request_builder._httpx_client.send.call_count == 1
        request = request_builder._httpx_client.send.call_args_list[0][1]["request"]
        await request.aread()
        assert request.method == "GET"
        assert request.url == "https://foo/bar?foo=bar"
        assert response.json() == {"foo": datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)}

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_request_inject_token(self, request_builder):
        # Prepare
        request_mock = AsyncMock(
            return_value=httpx.Response(request=Mock(), status_code=200, content=b'{"foo": "2000-01-01T00:00:00.000Z"}')
        )
        request_builder._httpx_client.send = request_mock
        request_builder._token = "token"

        # Run
        response = await request_builder._request(method="GET", url="https://foo/bar", params={"foo": "bar"})

        # Asserts
        assert request_builder._httpx_client.send.call_count == 1
        request = request_builder._httpx_client.send.call_args_list[0][1]["request"]
        await request.aread()
        assert request.method == "GET"
        assert request.url == "https://foo/bar?foo=bar"
        assert "Authorization" in request.headers and request.headers["Authorization"] == "Bearer token"
        assert response.json() == {"foo": datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)}

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_request_exclude_token(self, request_builder):
        # Prepare
        request_mock = AsyncMock(
            return_value=httpx.Response(request=Mock(), status_code=200, content=b'{"foo": "2000-01-01T00:00:00.000Z"}')
        )
        request_builder._httpx_client.send = request_mock
        request_builder._token = "token"

        # Run
        response = await request_builder._request(
            method="GET", url="https://foo/bar", params={"foo": "bar"}, token=False
        )

        # Asserts
        assert request_builder._httpx_client.send.call_count == 1
        request = request_builder._httpx_client.send.call_args_list[0][1]["request"]
        await request.aread()
        assert request.method == "GET"
        assert request.url == "https://foo/bar?foo=bar"
        assert "Authorization" not in request.headers
        assert response.json() == {"foo": datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)}

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_request_http_error(self, request_builder):
        # Set up mocks
        request_mock = Mock(spec=httpx.Request)
        response_mock = Mock(spec=httpx.Response)
        response_mock.status_code = 400
        response_mock.content = b""
        request_builder._httpx_client.send = AsyncMock(
            side_effect=httpx.exceptions.HTTPError(request=request_mock, response=response_mock)
        )

        # Run
        with pytest.raises(httpx.exceptions.HTTPError):
            await request_builder.foo.bar.retrieve(pk=1)

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_request_json_decode_error(self, request_builder):
        # Set up mocks
        request_mock = AsyncMock(return_value=httpx.Response(request=Mock(), status_code=200, content=b"{}"))
        request_builder._httpx_client.send = request_mock

        # Run
        with patch.object(Response, "json", side_effect=JSONDecodeError("", "", 0)), pytest.raises(JSONDecodeError):
            await request_builder.foo.bar.retrieve(pk=1)

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_request_with_retry(self, httpx_client, services_registry):
        # Prepare
        request_builder = RequestBuilder(httpx_client=httpx_client, available_services=services_registry, max_retries=2)
        request_builder._httpx_client.send = AsyncMock(
            side_effect=[
                httpx.exceptions.TimeoutException(),
                httpx.Response(request=Mock(), status_code=200, content=b'{"foo": "2000-01-01T00:00:00.000Z"}'),
            ]
        )

        # Run
        response = await request_builder._request(method="GET", url="https://foo/bar", params={"foo": "bar"})

        # Asserts
        expected_method = "GET"
        expected_url = "https://foo/bar?foo=bar"
        assert request_builder._httpx_client.send.call_count == 2
        request1 = request_builder._httpx_client.send.call_args_list[0][1]["request"]
        await request1.aread()
        assert request1.method == expected_method
        assert request1.url == expected_url
        request2 = request_builder._httpx_client.send.call_args_list[1][1]["request"]
        await request2.aread()
        assert request2.method == expected_method
        assert request2.url == expected_url
        assert response.json() == {"foo": datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)}

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_request_http_error_with_retry(self, request_builder):
        # Set up mocks
        request_mock = Mock(spec=httpx.Request)
        response_mock = Mock(spec=httpx.Response)
        response_mock.status_code = 400
        response_mock.content = b""
        request_builder._httpx_client.send = AsyncMock(
            side_effect=httpx.exceptions.HTTPError(request=request_mock, response=response_mock)
        )

        # Run
        with pytest.raises(httpx.exceptions.HTTPError):
            await request_builder.foo.bar.retrieve(pk=1)
