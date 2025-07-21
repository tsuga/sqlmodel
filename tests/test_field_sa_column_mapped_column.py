from typing import Optional

import pytest
from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column
from sqlmodel import Field, ForeignKey, SQLModel


def test_sa_column_takes_precedence(clear_sqlmodel) -> None:
    class Item(SQLModel, table=True):
        id: Optional[int] = Field(
            default=None,
            sa_column=mapped_column(String, primary_key=True, nullable=False),
        )

    # It would have been nullable with no sa_column
    assert Item.id.nullable is False  # type: ignore
    assert isinstance(Item.id.type, String)  # type: ignore


def test_sa_column_no_sa_args() -> None:
    with pytest.raises(RuntimeError):

        class Item(SQLModel, table=True):
            id: Optional[int] = Field(
                default=None,
                sa_column_args=[Integer],
                sa_column=mapped_column(Integer, primary_key=True),
            )


def test_sa_column_no_sa_kargs() -> None:
    with pytest.raises(RuntimeError):

        class Item(SQLModel, table=True):
            id: Optional[int] = Field(
                default=None,
                sa_column_kwargs={"primary_key": True},
                sa_column=mapped_column(Integer, primary_key=True),
            )


def test_sa_column_no_type() -> None:
    with pytest.raises(RuntimeError):

        class Item(SQLModel, table=True):
            id: Optional[int] = Field(
                default=None,
                sa_type=Integer,
                sa_column=mapped_column(Integer, primary_key=True),
            )


def test_sa_column_no_primary_key() -> None:
    with pytest.raises(RuntimeError):

        class Item(SQLModel, table=True):
            id: Optional[int] = Field(
                default=None,
                primary_key=True,
                sa_column=mapped_column(Integer, primary_key=True),
            )


def test_sa_column_no_nullable() -> None:
    with pytest.raises(RuntimeError):

        class Item(SQLModel, table=True):
            id: Optional[int] = Field(
                default=None,
                nullable=True,
                sa_column=mapped_column(Integer, primary_key=True),
            )


def test_sa_column_no_foreign_key() -> None:
    with pytest.raises(RuntimeError):

        class Team(SQLModel, table=True):
            id: Optional[int] = Field(default=None, primary_key=True)
            name: str

        class Hero(SQLModel, table=True):
            id: Optional[int] = Field(default=None, primary_key=True)
            team_id: Optional[int] = Field(
                default=None,
                foreign_key="team.id",
                sa_column=mapped_column(Integer, primary_key=True),
            )


def test_sa_column_foreign_key_in_mapped_column_int() -> None:
    class Team(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        name: str

    class Hero(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        team_id: Optional[int] = Field(
            default=None,
            sa_column=mapped_column(Integer, ForeignKey("team.id")),
        )


def test_sa_column_foreign_key_in_mapped_column_custom_type() -> None:
    from sqlmodel import String, TypeDecorator

    class CustomType:
        def __init__(self, value: str):
            self.value = value

        @classmethod
        def from_str(cls, value: str) -> "CustomType":
            return cls(value)

        def __str__(self) -> str:
            return self.value

    class CustomTypeDecorator(TypeDecorator):
        impl = String()  # CustomType
        cache_ok = True

        def process_bind_param(self, value: CustomType, dialect):
            if value is not None:
                return str(value)
            return None

        def process_result_value(self, value, dialect):
            if value is not None:
                return CustomType.from_str(value)
            return None

        @property
        def python_type(self):
            return CustomType

    class Team(SQLModel, table=True):
        id: Optional[CustomType] = Field(
            sa_type=CustomTypeDecorator, default=None, primary_key=True
        )
        name: str

    class Hero(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        team_id: Optional[CustomType] = Field(
            default=None,
            sa_column=mapped_column(CustomTypeDecorator, ForeignKey("team.id")),
        )


def test_sa_column_no_unique() -> None:
    with pytest.raises(RuntimeError):

        class Item(SQLModel, table=True):
            id: Optional[int] = Field(
                default=None,
                unique=True,
                sa_column=mapped_column(Integer, primary_key=True),
            )


def test_sa_column_no_index() -> None:
    with pytest.raises(RuntimeError):

        class Item(SQLModel, table=True):
            id: Optional[int] = Field(
                default=None,
                index=True,
                sa_column=mapped_column(Integer, primary_key=True),
            )


def test_sa_column_no_ondelete() -> None:
    with pytest.raises(RuntimeError):

        class Item(SQLModel, table=True):
            id: Optional[int] = Field(
                default=None,
                sa_column=mapped_column(Integer, primary_key=True),
                ondelete="CASCADE",
            )
