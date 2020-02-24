__all__ = [
    "ServiceNotFound",
    "ResourceNotFound",
    "RequestAlreadyBuilt",
    "RequestNotBuilt",
    "DiscoveryServicesError",
    "DiscoveryResourcesError",
    "UpdateTokenError",
    "ClientNotInitialized",
]


class ServiceNotFound(LookupError):
    """
    Exception class that represents a service that cannot be found.
    """

    pass


class ResourceNotFound(LookupError):
    """
    Exception class that represents a resource that cannot be found.
    """

    pass


class RequestAlreadyBuilt(Exception):
    """
    Exception class for notifying that the Request building is completed.
    """

    pass


class RequestNotBuilt(Exception):
    """
    Exception class for notifying that the Request building is not completed.
    """


class DiscoveryServicesError(Exception):
    """
    Exception class for errors occurred during services discovering process.
    """

    pass


class DiscoveryResourcesError(Exception):
    """
    Exception class for errors occurred during resources discovering process.
    """

    def __init__(self, service: str):
        self.service = service

    def __str__(self):
        return self.service  # pragma: no cover


class UpdateTokenError(Exception):
    """
    Exception class for errors occurred during authentication token update process.
    """

    pass


class ClientNotInitialized(Exception):
    """
    Exception class for representing a client that hasn't been initialized.
    """
