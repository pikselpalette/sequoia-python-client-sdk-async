import datetime
import json

import pytest
from sequoia.codecs import JSONDecoder, JSONEncoder


class TestCaseJSONEncoder:
    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    def test_encode_datetime(self):
        # Prepare
        expected_result = '{"foo": "2000-01-01T00:00:00.000Z"}'

        # Run
        encoded_json = json.dumps({"foo": datetime.datetime(2000, 1, 1, 0, 0, 0)}, cls=JSONEncoder)

        # Asserts
        assert encoded_json == expected_result

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    def test_encode_duration(self):
        # Prepare
        expected_result = '{"foo": "P1DT1H"}'

        # Run
        encoded_json = json.dumps({"foo": datetime.timedelta(days=1, hours=1)}, cls=JSONEncoder)

        # Asserts
        assert encoded_json == expected_result

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    def test_encode_default(self):
        # Prepare
        class Foo:
            pass

        # Run
        with pytest.raises(TypeError):
            json.dumps({"foo": Foo()}, cls=JSONEncoder)


class TestCaseJSONDecoder:
    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    def test_decode_datetime(self):
        # Prepare
        expected_result = {"foo": datetime.datetime(2000, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)}

        # Run
        decoded_json = json.loads('{"foo": "2000-01-01T00:00:00.000Z"}', cls=JSONDecoder)

        # Asserts
        assert decoded_json == expected_result

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    def test_decode_duration(self):
        # Prepare
        expected_result = {"foo": datetime.timedelta(days=1, hours=1)}

        # Run
        decoded_json = json.loads('{"foo": "P1DT1H"}', cls=JSONDecoder)

        # Asserts
        assert decoded_json == expected_result

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    def test_decode_default(self):
        # Prepare
        expected_result = {"foo": False}

        # Run
        decoded_json = json.loads('{"foo": false}', cls=JSONDecoder)

        # Asserts
        assert decoded_json == expected_result

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    def test_decode_nested_json(self):
        # Prepare
        expected_result = {"foo": {"bar": False}}

        # Run
        decoded_json = json.loads('{"foo": {"bar": false}}', cls=JSONDecoder)

        # Asserts
        assert decoded_json == expected_result

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    def test_decode_list(self):
        # Prepare
        expected_result = {"foo": ["bar", False]}

        # Run
        decoded_json = json.loads('{"foo": ["bar", false]}', cls=JSONDecoder)

        # Asserts
        assert decoded_json == expected_result

    @pytest.mark.type_unit
    @pytest.mark.execution_fast
    @pytest.mark.priority_high
    def test_decode_single_value(self):
        # Prepare
        expected_result = {"foo": False}

        # Run
        decoded_json = json.loads('{"foo": false}', cls=JSONDecoder)

        # Asserts
        assert decoded_json == expected_result
