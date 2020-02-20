import copy
import logging
import typing

import httpx
from sequoia.codecs import JSONDecoder

logger = logging.getLogger(__name__)

__all__ = ["Response"]


class Response(httpx.Response):
    """
    Low level response interface for interact with Sequoia services.
    """

    def __init__(self, response: httpx.Response):
        self.__dict__.update(copy.deepcopy(response.__dict__))
        print(self.__dict__)
        # content = getattr(response, "_content", None)
        # stream = response.stream if not content else None
        # super().__init__(
        #     status_code=response.status_code,
        #     request=response.request,
        #     http_version=response.http_version,
        #     headers=response.headers,
        #     stream=stream,
        #     history=response.history,
        #     content=content,
        # )

    def json(self, **kwargs: typing.Any) -> typing.Union[dict, list]:
        if not hasattr(self, "_json"):
            self._json = super().json(cls=JSONDecoder)

        return self._json

    def __repr__(self) -> str:
        params = {
            "status_code": self.status_code,
            "reason": self.reason_phrase,
            "headers": dict(self.headers),
            "content": repr(self.content.decode("utf-8")),
        }
        formatted_params = ", ".join([f"{k}={v}" for k, v in params.items()])
        return f"<{self.__class__.__name__}({formatted_params})>"
