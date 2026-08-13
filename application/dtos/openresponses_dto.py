from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field


class OpenResponsesRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    model: Optional[str] = None
    input: Union[str, list] = Field(..., description="User input message")
    previous_response_id: Optional[str] = None
    instructions: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_output_tokens: Optional[int] = None
    stream: Optional[bool] = None


class OutputTextAnnotation(BaseModel):
    pass


class OutputTextContent(BaseModel):
    type: str = "output_text"
    text: str
    annotations: List[Any] = Field(default_factory=list)


class Message(BaseModel):
    type: str = "message"
    id: str
    status: str = "completed"
    role: str = "assistant"
    content: List[OutputTextContent]


class UsageDetails(BaseModel):
    cached_tokens: int = 0


class OutputUsageDetails(BaseModel):
    reasoning_tokens: int = 0


class Usage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    input_tokens_details: UsageDetails = Field(default_factory=UsageDetails)
    output_tokens_details: OutputUsageDetails = Field(default_factory=OutputUsageDetails)


class TextFormat(BaseModel):
    type: str = "text"


class Reasoning(BaseModel):
    effort: Optional[str] = None
    summary: Optional[str] = None


class OpenResponsesResponse(BaseModel):
    id: str
    object: str = "response"
    created_at: int
    completed_at: int
    status: str = "completed"
    model: str
    previous_response_id: Optional[str]
    instructions: str
    output: List[Message]
    error: Optional[Any] = None
    tools: List[Any] = Field(default_factory=list)
    tool_choice: str = "auto"
    truncation: str = "auto"
    parallel_tool_calls: bool = False
    text: TextFormat = Field(default_factory=TextFormat)
    top_p: float = 1.0
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    top_logprobs: int = 0
    temperature: float = 1.0
    reasoning: Reasoning = Field(default_factory=Reasoning)
    usage: Usage = Field(default_factory=Usage)
    max_output_tokens: Optional[int] = None
    max_tool_calls: Optional[int] = None
    store: bool = False
    background: bool = False
    service_tier: str = "default"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    safety_identifier: Optional[str] = None
    prompt_cache_key: Optional[str] = None
