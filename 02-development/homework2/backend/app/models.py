from datetime import date, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


ColumnName = Literal["To Do", "In Progress", "Done"]
ActivityType = Literal[
    "created",
    "moved",
    "edited",
    "assigned",
    "commented",
    "due_date_changed",
    "label_changed",
]


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}"


class User(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str = Field(min_length=1)
    color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")


class Label(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str = Field(min_length=1)
    color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")


class Column(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: ColumnName
    order: Literal[0, 1, 2]
    cardOrder: list[str] = Field(default_factory=list)


class Comment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    author: User
    text: str = Field(min_length=1)
    createdAt: datetime


class ActivityEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    type: ActivityType
    detail: str
    actor: User
    timestamp: datetime


class Card(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str = Field(min_length=1)
    description: str
    columnId: str
    dueDate: date | None
    labels: list[Label]
    assignee: User | None
    createdAt: datetime
    updatedAt: datetime
    comments: list[Comment]
    activityLog: list[ActivityEntry]


class Board(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str = Field(min_length=1)
    createdAt: datetime
    updatedAt: datetime
    columns: list[Column]
    cards: list[Card]


class BoardSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str = Field(min_length=1)
    createdAt: datetime
    updatedAt: datetime
    columns: list[Column]
    cardCount: int = Field(ge=0)


def non_blank(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("must not be blank")
    return value


class CreateBoardRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)

    _name_is_not_blank = field_validator("name")(non_blank)


class UpdateBoardRequest(CreateBoardRequest):
    pass


class CreateCardRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    columnId: str = Field(min_length=1)
    title: str = Field(min_length=1)

    _title_is_not_blank = field_validator("title")(non_blank)


class UpdateCardRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1)
    description: str | None = None
    dueDate: date | None = None
    labels: list[Label] | None = None
    assignee: User | None = None
    columnId: str | None = None
    position: int | None = Field(default=None, ge=0)
    actor: User | None = None

    @field_validator("title")
    @classmethod
    def title_is_not_blank(cls, value: str | None) -> str | None:
        return non_blank(value) if value is not None else value

    @model_validator(mode="after")
    def has_at_least_one_change(self):
        if not self.model_fields_set:
            raise ValueError("at least one card field is required")
        return self


class CreateCommentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    author: User

    _text_is_not_blank = field_validator("text")(non_blank)
