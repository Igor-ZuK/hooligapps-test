from typing import Any
from typing import Optional
from typing import Union

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from pydantic.error_wrappers import ErrorWrapper

from project.core.uc.base import BaseUCError


class PyBusinessErrorWrapper(RequestValidationError):
    def __init__(self, errors: list[Union[Exception, BaseUCError]], *args: Any, **kwargs: Any):
        """Wrapper for expected error in business logic, which imitates pydantic validation 422-error format.

        Will be rendered to standard pydantic validation error in fastapi exception handlers. To see details about
        rendering go to `pydantic.error_wrappers.flatten_errors`.

        .. code-block:: python
            :caption: Wrap UC errors to 422 for frontend

            # uc/errors.py
            from project.core.uc.base import BaseUCError
            from project.core.uc.errors import FieldRelatedError
            from project.core.uc.errors import CommonRelatedError

            class CampaignValidationError(FieldRelatedError, BaseUCError):
                ...

            class CampaignIsNotEditable(CommonRelatedError, BaseUCError):
                ...

            # uc/do_smth_with_campaign/do_smth_uc.py

            class DoSmthUC(UC):
                async def execute(...) -> DoSmthResponse:
                    response = DoSmthResponse()
                    if len(campaign.name) < 5:
                        response.add_error(
                            CampaignValidationError(
                                message=FieldTypeErrorCode.string_length_not_in_range,
                                field="name"
                            )
                        )
                    if not self._is_campaign_processable(campaign):
                        response.add_error(
                            CampaignIsNotEditable(message=CampaignTreeErrorCode.ad_cant_be_edited_in_moderation_status)
                        )
                    ...
                    return response

            # apps/campaign/api/v1/endpoints.py
            from project.apps.exceptions import PyBusinessErrorWrapper

            @route.post(...)
            async def do_smth_with_campaign(
                campaign: Campaign,
                do_smth_uc: DoSmthUC = Depends(get_do_smth_uc),
            ):
                request = DoSmthRequest(...)
                result = await do_smth_uc.execute(request)
                if result.errors:
                   raise PyBusinessErrorWrapper(errors=result.errors)
                ...
        """
        transformed_errors = self._transform_business_errors_to_pydantic(errors)
        super().__init__(errors=transformed_errors, *args, **kwargs)  # type: ignore

    def _transform_business_errors_to_pydantic(
        self,
        errors: list[Union[Exception, BaseUCError]],
    ) -> list[ErrorWrapper]:
        """Transforms business errors to pydantic-formatted errors, which will be rendered by fastapi to 422.

        .. code-block:: python
            :caption: Example of rendered by FastApi error.

            {
              "detail": [
                {
                  "loc": ["name"],
                  "msg": "FieldTypeErrorCode.string_length_not_in_range",
                  "type": "value_error.field_error",
                  "ctx": {
                    "message": "string_length_not_in_range",
                    "error_code": -1,
                    "field": "name"
                  }
                }
              ]
            }
        """
        transformed = []
        for err in errors:
            if loc := getattr(err, "field", ""):
                transformed_err = ErrorWrapper(exc=err, loc=loc)
            else:
                transformed_err = ErrorWrapper(exc=err, loc=tuple())
            transformed.append(transformed_err)
        return transformed


class ErrorParams(BaseModel):
    """Parameters which may be used in error texts."""

    object_id: Optional[str]
    min_length: Optional[float]
    max_length: Optional[float]
    forbidden_symbols: Optional[str]
    min_value: Optional[float]
    max_value: Optional[float]


class Error422ResponseDetail(BaseModel):
    """Class used to represent validation and business errors as typed 422-errors in openapi.json."""

    loc: list[str]
    msg: str
    type: str
    ctx: Optional[ErrorParams]


class Error422Response(BaseModel):
    detail: list[Error422ResponseDetail]
