from pydantic import BaseModel


class GetUserInput(BaseModel):
    number_of_previous_conversations: int


class TextPhoneNumber(BaseModel):
    message: str


class SubagentTaskInput(BaseModel):
    task: str
