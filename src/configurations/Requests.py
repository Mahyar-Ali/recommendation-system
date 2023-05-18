from typing import Dict, List, Optional

from pydantic import BaseModel, conint, constr, root_validator

from src.validators.extras_validator import validate_extra_fileds


class Recommendation_Product_Request(BaseModel):
    product_id: constr(min_length=3, strict=True)
    num_responses: Optional[conint(ge=1, strict=True)] = 3

    class Config:
        use_enum_values = True

    @root_validator(pre=True)
    def validate_extra(cls, values):
        return validate_extra_fileds(cls, values)


class Recommendation_User_Request(BaseModel):
    user_id: constr(min_length=3, strict=True)

    class Config:
        use_enum_values = True

    @root_validator(pre=True)
    def validate_extra(cls, values):
        return validate_extra_fileds(cls, values)


class Content_Moderation_Request(BaseModel):
    title: constr(min_length=3, strict=True)
    text: Optional[constr(min_length=3, strict=True)]

    class Config:
        use_enum_values = True

    @root_validator(pre=True)
    def validate_extra(cls, values):
        return validate_extra_fileds(cls, values)


class Review_Calculation_Request(BaseModel):
    review: constr(min_length=2, strict=True)
    ratings: conint(ge=0, le=5, strict=True)
    quantity: conint(ge=0, strict=True)

    class Config:
        use_enum_values = True

    @root_validator(pre=True, allow_reuse=True)
    def validate_extra(cls, values):
        return validate_extra_fileds(cls, values)


class Update_Product_Model_Request(BaseModel):
    pass


class Update_User_Model_Request(BaseModel):
    pass
