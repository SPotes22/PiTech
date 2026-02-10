"""Database bootstrap helpers for the lightweight ORM."""

from .models import FormModel, UserModel


def initialize_models() -> tuple[FormModel, UserModel]:
    return FormModel(), UserModel()
