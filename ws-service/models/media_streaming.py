from typing import Annotated, Any, Dict, Literal, Union

from pydantic import BaseModel, Field, field_validator

class MediaFormat(BaseModel):
    encoding: str
    sampleRate: int
    channels: int

class StartDetails(BaseModel):
    accountSid: str
    streamSid: str
    callSid: str
    tracks: list[str]
    mediaFormat: MediaFormat
    customParameters: Dict[str, Any]  # Flexible dict for custom params

class MediaDetails(BaseModel):
    track: Literal["inbound", "outbound"]
    chunk: int
    timestamp: int
    payload: str
    
    @field_validator('chunk', 'timestamp', mode='before')
    @classmethod
    def convert_str_to_int(cls, v):
        if isinstance(v, str):
            return int(v)
        return v

class StopDetails(BaseModel):
    accountSid: str
    callSid: str

# Messages from Twilio Media Streams
class BaseMessage(BaseModel):
    event: str

class ConnectedMessage(BaseMessage):
    event: Literal["connected"]
    protocol: str
    version: str

class StartMessage(BaseMessage):
    event: Literal["start"]
    start: StartDetails
    streamSid: str

class MediaMessage(BaseMessage):
    event: Literal["media"]
    media: MediaDetails
    streamSid: str

class StopMessage(BaseMessage):
    event: Literal["stop"]
    stop: StopDetails
    streamSid: str


Message = Union[ConnectedMessage, StartMessage, MediaMessage, StopMessage]

StreamMessage = Annotated[
    Union[StartMessage, MediaMessage, StopMessage],
    Field(discriminator='event')
]
