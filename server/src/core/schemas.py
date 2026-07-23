from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class APIBaseModel(BaseModel):
    """The base model for all API input and output.

    It handles the conversion between camelCase (JSON) and snake_case (Python).
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
