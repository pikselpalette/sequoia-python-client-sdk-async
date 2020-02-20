from unittest.mock import Mock

import pytest

from sequoia.response import Response


@pytest.fixture
def response_registry_list_services():
    response_mock = Mock(spec=Response)
    response_mock.json.return_value = {
        "services": [
            {
                "owner": "root",
                "name": "identity",
                "location": "https://identity.sequoia.piksel.com",
                "title": "Identity Service",
            },
            {
                "owner": "root",
                "name": "registry",
                "location": "https://registry.sequoia.piksel.com",
                "title": "Registry Service",
            },
            {
                "owner": "root",
                "name": "metadata",
                "location": "https://metadata.sequoia.piksel.com",
                "title": "Metadata Service",
            },
        ]
    }

    return response_mock


@pytest.fixture
def response_identity_get_description():
    response_mock = Mock(spec=Response)
    response_mock.json.return_value = {
        "name": "identity",
        "urn": "urn:piksel:service:identity",
        "title": "Identity and Access Service",
        "description": "Responsible for identity and access management",
        "features": [],
        "resourcefuls": {
            "users": {
                "path": "/data",
                "serviceName": "identity",
                "description": "Represents a user",
                "singularName": "user",
                "pluralName": "users",
                "hyphenatedPluralName": "users",
            }
        },
        "routes": [],
    }

    return response_mock


@pytest.fixture
def response_registry_get_description():
    response_mock = Mock(spec=Response)
    response_mock.json.return_value = {
        "name": "registry",
        "urn": "urn:piksel:service:registry",
        "title": "Registry Service",
        "description": "Responsible for managing the service registry",
        "features": [],
        "resourcefuls": {
            "services": {
                "path": "/data",
                "serviceName": "registry",
                "description": "Represents a service available in the environment at the given location.",
                "singularName": "service",
                "pluralName": "services",
                "hyphenatedPluralName": "services",
            }
        },
        "routes": [
            {
                "name": "manage-services-list",
                "title": "List Services",
                "group": "manage-services",
                "path": "/services/{owner}/{service?}",
                "method": "GET",
                "description": "Lists out services for a given tenancy",
                "tags": ["auth", "api"],
                "stability": "stable",
                "inputs": {
                    "params": [
                        {
                            "type": "name",
                            "flags": {"presence": "required"},
                            "options": {"language": {"string": {}}},
                            "meta": [{"sequoiaType": "name"}],
                            "examples": [{"value": "piksel"}],
                            "invalids": [""],
                            "name": "owner",
                            "required": True,
                        },
                        {"type": "string", "invalids": [""], "name": "service", "required": False},
                    ]
                },
                "responses": [],
            }
        ],
    }

    return response_mock


@pytest.fixture
def response_metadata_get_description():
    response_mock = Mock(spec=Response)
    response_mock.json.return_value = {
        "name": "metadata",
        "urn": "urn:piksel:service:metadata",
        "title": "Metadata Service",
        "description": "Stores content metadata resources",
        "features": [{"name": "fieldLocking"}],
        "resourcefuls": {
            "tenancyConfigurations": {
                "path": "/data",
                "serviceName": "metadata",
                "description": "Represents the tenancy configuration for the service",
                "singularName": "tenancyConfiguration",
                "pluralName": "tenancyConfigurations",
                "hyphenatedPluralName": "tenancy-configurations",
            }
        },
        "routes": [
            {
                "name": "root",
                "title": "root",
                "actions": [],
                "path": "/",
                "method": "GET",
                "description": "Redirect '/' to '/docs'",
                "stability": "stable",
                "inputs": {},
                "responses": [],
            }
        ],
    }

    return response_mock


@pytest.fixture
def response_identity_get_oauth_token():
    response_mock = Mock(spec=Response)
    response_mock.json.return_value = {"access_token": "74b685d3ba5943662884cf786e4ca8d6ff71cc09"}

    return response_mock
