from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from sequoia.client import Client
from sequoia.exceptions import (
    ClientNotInitialized,
    DiscoveryResourcesError,
    DiscoveryServicesError,
    UpdateTokenError,
)
from sequoia.request import RequestBuilder
from sequoia.response import Response
from sequoia.types import Resource, Service, ServicesRegistry


class TestCaseSequoiaClient:
    @pytest.fixture
    def sequoia_client(self):
        return Client(registry_url="", client_id="", client_secret="")

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    def test_init(self):
        client = Client(registry_url="https://registry.sequoia.piksel.com", client_id="foo", client_secret="bar")
        assert client._client_id == "foo"
        assert client._client_secret == "bar"
        assert client._token is None
        assert client._owner is None
        assert len(client._services) == 0

    @pytest.mark.asyncio
    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    async def test_aenter(self, sequoia_client, response_registry_list_services, response_identity_get_oauth_token):
        responses = [
            # Services discovery
            response_registry_list_services,
            # Auth token
            response_identity_get_oauth_token,
        ]
        with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock, side_effect=responses):
            async with sequoia_client as client:
                assert client._token == "74b685d3ba5943662884cf786e4ca8d6ff71cc09"
                assert client._owner is None
                assert client._services == ServicesRegistry(
                    {
                        "identity": Service(
                            name="identity",
                            url="https://identity.sequoia.piksel.com",
                            title="Identity and Access Service",
                            description="Responsible for identity and access management",
                        ),
                        "metadata": Service(
                            name="metadata",
                            url="https://metadata.sequoia.piksel.com",
                            title="Metadata Service",
                            description="Stores content metadata resources",
                        ),
                        "registry": Service(
                            name="registry",
                            url="https://registry.sequoia.piksel.com",
                            title="Registry Service",
                            description="Responsible for managing the service registry",
                        ),
                    }
                )

    @pytest.mark.asyncio
    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    async def test_aexit(self, sequoia_client, response_registry_list_services, response_identity_get_oauth_token):
        responses = [
            # Services discovery
            response_registry_list_services,
            # Auth token
            response_identity_get_oauth_token,
        ]
        with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock, side_effect=responses):
            async with sequoia_client as client:
                pass

            assert client._token is None
            assert client._owner is None
            assert client._services == ServicesRegistry()

    @pytest.mark.asyncio
    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    async def test_services(self, sequoia_client, response_registry_list_services, response_identity_get_oauth_token):
        responses = [
            # Services discovery
            response_registry_list_services,
            # Auth token
            response_identity_get_oauth_token,
        ]
        with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock, side_effect=responses):
            async with sequoia_client as client:
                assert client.services() == {
                    "identity": Service(
                        name="identity",
                        url="https://identity.sequoia.piksel.com",
                        title="Identity and Access Service",
                        description="Responsible for identity and access management",
                    ),
                    "metadata": Service(
                        name="metadata",
                        url="https://metadata.sequoia.piksel.com",
                        title="Metadata Service",
                        description="Stores content metadata resources",
                    ),
                    "registry": Service(
                        name="registry",
                        url="https://registry.sequoia.piksel.com",
                        title="Registry Service",
                        description="Responsible for managing the service registry",
                    ),
                }

    @pytest.mark.asyncio
    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    async def test_resources(
        self,
        sequoia_client,
        response_registry_list_services,
        response_identity_get_oauth_token,
        response_registry_get_description,
        response_identity_get_description,
        response_metadata_get_description,
    ):
        responses = [
            # Services discovery
            response_registry_list_services,
            # Auth token
            response_identity_get_oauth_token,
            # Resources discovery
            response_identity_get_description,
            response_metadata_get_description,
            response_registry_get_description,
        ]
        with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock, side_effect=responses):
            async with sequoia_client as client:
                assert await client.resources() == {
                    "identity": {"users": Resource(name="users", path="/data/users")},
                    "metadata": {
                        "tenancy_configurations": Resource(
                            name="tenancyConfigurations", path="/data/tenancy-configurations"
                        )
                    },
                    "registry": {"services": Resource(name="services", path="/data/services")},
                }

    @pytest.mark.asyncio
    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    async def test_resources_specific(
        self,
        sequoia_client,
        response_registry_list_services,
        response_identity_get_oauth_token,
        response_registry_get_description,
        response_identity_get_description,
        response_metadata_get_description,
    ):
        responses = [
            # Services discovery
            response_registry_list_services,
            # Auth token
            response_identity_get_oauth_token,
            # Resources discovery
            response_identity_get_description,
        ]
        with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock, side_effect=responses):
            async with sequoia_client as client:
                assert await client.resources("identity") == {"users": Resource(name="users", path="/data/users")}

    @pytest.mark.asyncio
    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    async def test_set_owner(
        self,
        sequoia_client,
        response_registry_list_services,
        response_registry_get_description,
        response_identity_get_description,
        response_metadata_get_description,
    ):
        responses = [
            # Get services and description of them after setting owner
            response_registry_list_services,
            response_identity_get_description,
            response_metadata_get_description,
            response_registry_get_description,
        ]
        with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock, side_effect=responses):
            assert sequoia_client._token is None
            assert sequoia_client._owner is None
            assert sequoia_client._services == ServicesRegistry()

            await sequoia_client.set_owner("root")

            assert sequoia_client._token is None
            assert sequoia_client._owner == "root"
            assert sequoia_client._services == ServicesRegistry(
                {
                    "identity": Service(
                        name="identity",
                        url="https://identity.sequoia.piksel.com",
                        title="Identity and Access Service",
                        description="Responsible for identity and access management",
                    ),
                    "metadata": Service(
                        name="metadata",
                        url="https://metadata.sequoia.piksel.com",
                        title="Metadata Service",
                        description="Stores content metadata resources",
                    ),
                    "registry": Service(
                        name="registry",
                        url="https://registry.sequoia.piksel.com",
                        title="Registry Service",
                        description="Responsible for managing the service registry",
                    ),
                }
            )

    @pytest.mark.asyncio
    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    async def test_update_services_wrong_response_getting_registry_list(self):
        wrong_response = Mock(spec=Response)
        wrong_response.json.return_value = {"foo": "bar"}
        responses = [
            # Wrong response from registry
            wrong_response
        ]
        with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock, side_effect=responses), pytest.raises(
            DiscoveryServicesError
        ):
            sequoia_client = Client(registry_url="", client_id="", client_secret="")
            await sequoia_client.update_services()

    @pytest.mark.asyncio
    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    async def test_update_services_error_getting_registry_list(self):
        wrong_response = Mock(spec=Response)
        wrong_response.json.return_value = {"foo": "bar"}
        responses = [
            # Error raised establishing connection with registry
            OSError()
        ]
        with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock, side_effect=responses), pytest.raises(
            DiscoveryServicesError
        ):
            sequoia_client = Client(registry_url="", client_id="", client_secret="")
            await sequoia_client.update_services()

    @pytest.mark.asyncio
    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    async def test_update_services_wrong_response_getting_service_description(self, response_registry_list_services):
        wrong_response = Mock(spec=Response)
        wrong_response.json.return_value = {"foo": "bar"}
        responses = [
            # Registry's list of services
            response_registry_list_services,
            # Wrong response from service description
            wrong_response,
        ]
        with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock, side_effect=responses), pytest.raises(
            DiscoveryResourcesError
        ):
            sequoia_client = Client(registry_url="", client_id="", client_secret="")
            await sequoia_client.update_services()
            await sequoia_client.resources("metadata")

    @pytest.mark.asyncio
    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    async def test_update_services_error_getting_service_description(self, response_registry_list_services):
        wrong_response = Mock(spec=Response)
        wrong_response.json.return_value = {"foo": "bar"}
        responses = [
            # Registry's list of services
            response_registry_list_services,
            # Error raised establishing connection with service
            OSError(),
        ]
        with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock, side_effect=responses), pytest.raises(
            DiscoveryResourcesError
        ):
            sequoia_client = Client(registry_url="", client_id="", client_secret="")
            await sequoia_client.update_services()
            await sequoia_client.resources("metadata")

    @pytest.mark.asyncio
    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    async def test_update_token_wrong_response(
        self, sequoia_client, response_registry_list_services, response_identity_get_oauth_token
    ):
        wrong_response = Mock(spec=Response)
        wrong_response.json.return_value = {"foo": "bar"}
        responses = [
            # Services discovery
            response_registry_list_services,
            # Right response from identity (for initializing)
            response_identity_get_oauth_token,
            # Wrong response from identity
            wrong_response,
        ]
        with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock, side_effect=responses), pytest.raises(
            UpdateTokenError
        ):
            async with sequoia_client as client:
                await client.update_token()

    @pytest.mark.asyncio
    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    async def test_update_token_error(
        self, sequoia_client, response_registry_list_services, response_identity_get_oauth_token
    ):
        responses = [
            # Services discovery
            response_registry_list_services,
            # Right response from identity (for initializing)
            response_identity_get_oauth_token,
            # Wrong response from identity
            OSError(),
        ]
        with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock, side_effect=responses), pytest.raises(
            UpdateTokenError
        ):
            async with sequoia_client as client:
                await client.update_token()

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    @pytest.mark.asyncio
    async def test_get_request_builder(
        self, sequoia_client, response_registry_list_services, response_identity_get_oauth_token
    ):
        responses = [
            # Services discovery
            response_registry_list_services,
            # Right response from identity (for initializing)
            response_identity_get_oauth_token,
        ]
        with patch.object(httpx.AsyncClient, "request", new_callable=AsyncMock, side_effect=responses):
            async with sequoia_client as client:
                assert client._builder == RequestBuilder(
                    httpx_client=client._httpx_client,
                    owner=client._owner,
                    token=client._token,
                    available_services=client._services,
                )

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    def test_get_request_builder_client_uninitialized(self, sequoia_client):
        with pytest.raises(ClientNotInitialized):
            sequoia_client.registry
