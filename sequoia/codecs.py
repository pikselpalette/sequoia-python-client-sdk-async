import datetime
import json
import typing

import isodate


class JSONEncoder(json.JSONEncoder):
    """
    Extended JSON encoder adapted to Sequoia API spec: http://docs.sequoia.piksel.com/concepts/api/types.html
    """

    deserialize_functions = {
        datetime.datetime: lambda x: x.replace(tzinfo=None).isoformat(timespec="milliseconds") + "Z",  # Force UTC time
        datetime.timedelta: isodate.duration_isoformat,
    }

    def default(self, o) -> typing.Dict[typing.Any, typing.Any]:
        """
        Deserialize Python native objects into JSON compatible types.

        :param o: Object to deserialize.
        :return: JSON compatible value.
        """
        for k, f in self.deserialize_functions.items():
            if isinstance(o, k):
                encode = f
                break
        else:
            encode = super().default

        return encode(o)


class JSONDecoder(json.JSONDecoder):
    """
    Extended JSON decoder adapted to Sequoia API spec: http://docs.sequoia.piksel.com/concepts/api/types.html
    """

    serialize_functions = (isodate.parse_datetime, isodate.parse_duration)

    def __init__(self, *, strict=True):
        super().__init__(object_hook=self.serialize, strict=strict)

    def serialize(self, o):
        """
        Serialize JSON objects into Python native types.

        :param o: JSON object.
        :return: Serialized object.
        """
        if isinstance(o, dict):
            return {k: self.serialize(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [self.serialize(i) for i in o]

        return self.parse(o)

    def parse(self, value) -> typing.Any:
        """
        Parse a value and serialize it into a Python native type.

        :param value: JSON value to be serialized.
        :return: Serialized value.
        """
        for f in self.serialize_functions:
            try:
                result = f(value)
                break
            except Exception:
                pass
        else:
            result = value

        return result
