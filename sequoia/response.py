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
        self.__dict__.update(response.__dict__.copy())

    def json(self, **kwargs: typing.Any) -> typing.Union[dict, list]:
        if not hasattr(self, "_json"):
            self._json = super().json(cls=JSONDecoder) if self.text != "" else self.text

        return self._json

    def __repr__(self) -> str:
        params = {
            "status_code": self.status_code,
            "reason": self.reason_phrase,
            "headers": dict(self.headers),
        }
        try:
            params["content"] = repr(self.content.decode("utf-8"))
        except httpx.exceptions.RequestNotRead:
            pass

        formatted_params = ", ".join([f"{k}={v}" for k, v in params.items()])
        return f"<{self.__class__.__name__}({formatted_params})>"
