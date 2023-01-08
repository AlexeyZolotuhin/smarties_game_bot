from dataclasses import field
from typing import ClassVar, Type, List, Optional

from marshmallow_dataclass import dataclass
from marshmallow import Schema, EXCLUDE


@dataclass
class MessageFrom:
    id: int
    first_name: str

    class Meta:
        unknown = EXCLUDE


@dataclass
class Chat:
    id: int
    type: str
    title: Optional[str] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class Message:
    message_id: int
    from_: Optional[MessageFrom] = field(metadata={"data_key": "from"})
    chat: Chat
    text: Optional[str] = None
    reply_to_message: Optional["Message"] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class User:
    id: int
    first_name: str

    class Meta:
        unknown = EXCLUDE


@dataclass
class NewChatMember:
    user: User
    status: Optional[str] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class MyChatMember:
    chat: Chat
    from_: MessageFrom = field(metadata={"data_key": "from"})
    new_chat_member: NewChatMember

    class Meta:
        unknown = EXCLUDE


@dataclass
class CallbackQuery:
    id: int
    from_: MessageFrom = field(metadata={"data_key": "from"})
    message: Message
    data: str

    class Meta:
        unknown = EXCLUDE


@dataclass
class UpdateObj:
    update_id: int
    message: Optional[Message] = None
    my_chat_member: Optional[MyChatMember] = None
    callback_query: Optional[CallbackQuery] = None

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


@dataclass
class GetUpdatesResponse:
    ok: bool
    result: List[UpdateObj]

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


@dataclass
class SendMessageResponse:
    ok: bool
    result: Message

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE
