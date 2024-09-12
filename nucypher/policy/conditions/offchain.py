from typing import Any, Optional, Tuple

import requests
from jsonpath_ng.exceptions import JsonPathLexerError, JsonPathParserError
from jsonpath_ng.ext import parse
from marshmallow import fields, post_load, validate
from marshmallow.fields import Field, Url

from nucypher.policy.conditions.base import AccessControlCondition, ExecutionCall
from nucypher.policy.conditions.exceptions import (
    ConditionEvaluationFailed,
    InvalidCondition,
)
from nucypher.policy.conditions.lingo import ConditionType, ReturnValueTest
from nucypher.utilities.logging import Logger


class JSONPathField(Field):
    default_error_messages = {
        "invalidType": "Expression of type {value} is not valid for JSONPath",
        "invalid": "'{value}' is not a valid JSONPath expression",
    }

    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, str):
            raise self.make_error("invalidType", value=type(value))
        try:
            parse(value)
        except (JsonPathLexerError, JsonPathParserError):
            raise self.make_error("invalid", value=value)
        return value


class JsonApiCall(ExecutionCall):
    CALL_TYPE = "json-api"

    TIMEOUT = 5  # seconds

    class Schema(ExecutionCall.Schema):
        SKIP_VALUES = (None,)
        call_type = fields.Str(validate=validate.Equal("json-api"), required=True)
        endpoint = Url(required=True, relative=False, schemes=["https"])
        parameters = fields.Dict(required=False, allow_none=True)
        query = JSONPathField(required=False, allow_none=True)

        @post_load
        def make(self, data, **kwargs):
            return JsonApiCall(**data)

    def __init__(
        self,
        endpoint: str,
        call_type: str = CALL_TYPE,
        parameters: Optional[dict] = None,
        query: Optional[str] = None,
    ):
        self.call_type = call_type

        self.endpoint = endpoint
        self.parameters = parameters or {}
        self.query = query

        self.timeout = self.TIMEOUT
        self.logger = Logger(__name__)

    def execute(self, *args, **kwargs) -> Any:
        response = self._fetch()
        data = self._deserialize_response(response)
        result = self._query_response(data)
        return result

    def _fetch(self) -> requests.Response:
        """Fetches data from the endpoint."""
        try:
            response = requests.get(
                self.endpoint, params=self.parameters, timeout=self.timeout
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            self.logger.error(f"HTTP error occurred: {http_error}")
            raise ConditionEvaluationFailed(
                f"Failed to fetch endpoint {self.endpoint}: {http_error}"
            )
        except requests.exceptions.RequestException as request_error:
            self.logger.error(f"Request exception occurred: {request_error}")
            raise InvalidCondition(
                f"Failed to fetch endpoint {self.endpoint}: {request_error}"
            )

        if response.status_code != 200:
            self.logger.error(
                f"Failed to fetch endpoint {self.endpoint}: {response.status_code}"
            )
            raise ConditionEvaluationFailed(
                f"Failed to fetch endpoint {self.endpoint}: {response.status_code}"
            )

        return response

    def _deserialize_response(self, response: requests.Response) -> Any:
        """Deserializes the JSON response from the endpoint."""
        try:
            data = response.json()
        except (requests.exceptions.RequestException, ValueError) as json_error:
            self.logger.error(f"JSON parsing error occurred: {json_error}")
            raise ConditionEvaluationFailed(
                f"Failed to parse JSON response: {json_error}"
            )
        return data

    def _query_response(self, data: Any) -> Any:

        if not self.query:
            return data  # primitive value

        try:
            expression = parse(self.query)
            matches = expression.find(data)
            if not matches:
                message = f"No matches found for the JSONPath query: {self.query}"
                self.logger.info(message)
                raise ConditionEvaluationFailed(message)
        except (JsonPathLexerError, JsonPathParserError) as jsonpath_err:
            self.logger.error(f"JSONPath error occurred: {jsonpath_err}")
            raise ConditionEvaluationFailed(f"JSONPath error: {jsonpath_err}")

        if len(matches) > 1:
            message = (
                f"Ambiguous JSONPath query - Multiple matches found for: {self.query}"
            )
            self.logger.info(message)
            raise ConditionEvaluationFailed(message)
        result = matches[0].value

        return result


class JsonApiCondition(AccessControlCondition):
    """
    A JSON API condition is a condition that can be evaluated by reading from a JSON
    HTTPS endpoint. The response must return an HTTP 200 with valid JSON in the response body.
    The response will be deserialized as JSON and parsed using jsonpath.
    """

    CONDITION_TYPE = ConditionType.JSONAPI.value

    class Schema(JsonApiCall.Schema):
        name = fields.Str(required=False)
        condition_type = fields.Str(
            validate=validate.Equal(ConditionType.JSONAPI.value), required=True
        )
        return_value_test = fields.Nested(
            ReturnValueTest.ReturnValueTestSchema(), required=True
        )

        class Meta:
            exclude = ("call_type",)  # don't serialize call_type

        @post_load
        def make(self, data, **kwargs):
            return JsonApiCondition(**data)

    def __init__(
        self,
        return_value_test: ReturnValueTest,
        condition_type: str = ConditionType.JSONAPI.value,
        name: Optional[str] = None,
        *args,
        **kwargs,
    ):
        if condition_type != self.CONDITION_TYPE:
            raise InvalidCondition(
                f"{self.__class__.__name__} must be instantiated with the {self.CONDITION_TYPE} type."
            )

        try:
            self.json_api_call = self._create_json_api_call(*args, **kwargs)
        except ValueError as e:
            raise InvalidCondition(str(e))

        self.name = name
        self.condition_type = condition_type

        self.return_value_test = return_value_test

        super().__init__()

    def _create_json_api_call(self, *args, **kwargs):
        return JsonApiCall(*args, **kwargs)

    @property
    def endpoint(self):
        return self.json_api_call.endpoint

    @property
    def query(self):
        return self.json_api_call.query

    @property
    def parameters(self):
        return self.json_api_call.parameters

    @property
    def timeout(self):
        return self.json_api_call.timeout

    def verify(self, **context) -> Tuple[bool, Any]:
        """
        Verifies the offchain condition is met by performing a read operation on the endpoint
        and evaluating the return value test with the result. Parses the endpoint's JSON response using
        JSONPath.
        """
        result = self.json_api_call.execute(**context)
        eval_result = self.return_value_test.eval(result)  # test
        return eval_result, result
