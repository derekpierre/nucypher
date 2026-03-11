from typing import Any, List, Optional, Tuple

from marshmallow import ValidationError, fields, post_load, validate, validates

from nucypher.policy.conditions.base import Condition, _Serializable
from nucypher.policy.conditions.context import (
    is_context_variable,
    resolve_any_context_variables,
)
from nucypher.policy.conditions.lingo import (
    ConditionField,
    ConditionType,
    ReturnValueTest,
)
from nucypher.policy.conditions.utils import CamelCaseSchema, ConditionProviderManager


class SelectCase(_Serializable):
    class Schema(CamelCaseSchema):
        test = fields.Nested(ReturnValueTest.Schema(), required=True)
        condition = ConditionField(required=True)

        @post_load
        def make(self, data, **kwargs):
            return SelectCase(**data)

    def __init__(
        self,
        test: ReturnValueTest,
        condition: Condition,
    ):
        self.test = test
        self.condition = condition

        self._validate()


class SelectCondition(Condition):
    CONDITION_TYPE = ConditionType.SELECT.value
    MAX_NESTED_SELECT_CONDITIONS = 3

    @classmethod
    def _validate_select_condition_nesting(
        cls,
        conditions: List[Condition],
        field_name: str,
        current_level: int = 1,
    ):
        for condition in conditions:
            if not isinstance(condition, SelectCondition):
                continue

            level = current_level + 1
            if level > cls.MAX_NESTED_SELECT_CONDITIONS:
                raise ValidationError(
                    field=field_name,
                    message=f"Too many nested select conditions; only {cls.MAX_NESTED_SELECT_CONDITIONS} allowed",
                )

            # check cases
            sub_conditions = [case.condition for case in condition.cases]
            condition._validate_select_condition_nesting(
                conditions=sub_conditions,
                field_name="cases",
                current_level=level,
            )

            # check default condition
            if condition.default_condition is not None:
                condition._validate_select_condition_nesting(
                    conditions=[condition.default_condition],
                    field_name="default_condition",
                    current_level=level,
                )

    class Schema(Condition.Schema):
        condition_type = fields.Str(
            validate=validate.Equal(ConditionType.SELECT.value), required=True
        )
        value = fields.Str(required=True)
        cases = fields.List(
            fields.Nested(SelectCase.Schema()),
            required=True,
            validate=[validate.Length(min=2, error="At least 2 cases are required")],
        )
        default_condition = ConditionField(required=False)

        @post_load
        def make(self, data, **kwargs):
            return SelectCondition(**data)

        @validates("value")
        def validate_value(self, value):
            if not is_context_variable(value):
                raise ValidationError(
                    f"Invalid value; expected a context variable, but got '{value}'"
                )

        @validates("cases")
        def validate_case_conditions(self, value):
            conditions = [case.condition for case in value]
            SelectCondition._validate_select_condition_nesting(
                conditions=conditions, field_name="cases"
            )

        @validates("default_condition")
        def validate_default_condition(self, value):
            if value is not None:
                SelectCondition._validate_select_condition_nesting(
                    conditions=[value], field_name="default_condition"
                )

    def __init__(
        self,
        value: str,
        cases: List[SelectCase],
        condition_type: str = ConditionType.SELECT.value,
        default_condition: Optional[Condition] = None,
        name: Optional[str] = None,
    ):
        self.value = value
        self.cases = cases
        self.default_condition = default_condition
        super().__init__(condition_type=condition_type, name=name)

    def __repr__(self):
        r = f"{self.__class__.__name__}(value={self.value}, num_cases={len(self.cases)}, default_condition={self.default_condition})"
        return r

    def verify(
        self, providers: ConditionProviderManager, **context
    ) -> Tuple[bool, Any]:
        resolved_value = resolve_any_context_variables(
            self.value, providers=providers, **context
        )
        for case in self.cases:
            resolved_return_value_test = case.test.with_resolved_context(
                providers=providers, **context
            )
            if resolved_return_value_test.eval(resolved_value):
                return case.condition.verify(providers=providers, **context)

        if self.default_condition is not None:
            return self.default_condition.verify(providers=providers, **context)

        # TODO should the value returned be None? Does that affect lynx debugging output?
        return False, None
