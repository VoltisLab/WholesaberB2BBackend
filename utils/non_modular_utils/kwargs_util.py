from django.db import models


class KwargsUtil:
    @classmethod
    def cherry_pick(cls, kwargs: dict, items: list) -> list:
        return [kwargs.get(item, None) for item in items]

    @staticmethod
    def model_field(model_object: models.Model, model_field: str):
        if model_object is None:
            return None
        else:
            return model_object.__dict__.get(model_field)
