class AgentException(Exception):
    """Base exception for all agent-related errors."""
    def __init__(self, message: str, details: str = None):
        super().__init__(message)
        self.message = message
        self.details = details or ""

class RequestValidationException(AgentException):
    """Raised when the incoming user request fails validation checks."""
    pass

class IntentDetectionException(AgentException):
    """Raised when intent detection fails critically."""
    pass

class PlannerException(AgentException):
    """Raised when planner is unable to construct a valid plan."""
    pass

class ToolExecutionException(AgentException):
    """Raised when a specific tool fails during execution."""
    def __init__(self, tool_name: str, message: str, details: str = None):
        super().__init__(f"Tool '{tool_name}' failed: {message}", details)
        self.tool_name = tool_name

class LLMException(AgentException):
    """Raised when external LLM calls fail, timeout, or hit rate limits."""
    pass

class DocxGenerationException(AgentException):
    """Raised when the DOCX generation/formatting fails."""
    pass

class ReflectionException(AgentException):
    """Raised when reflection fails critically."""
    pass
