import re
from typing import Dict, Any
from app.core.exceptions import RequestValidationException
from app.core.logging import logger

MAX_PROMPT_LENGTH = 8192  # Safety limit for character length

# Common prompt injection / system bypass indicator patterns
PROMPT_INJECTION_PATTERNS = [
    r"(?i)\bignore\b.*\binstruction",
    r"(?i)\bsystem\b.*\boverride",
    r"(?i)\bdisregard\b.*\bprevious",
    r"(?i)\bforget\b.*\bprevious",
    r"(?i)\bforget\b.*\bi\b.*\bsaid",
    r"(?i)\bnew\b.*\binstructions\b.*\bfrom\b.*\bnow",
    r"(?i)you\s+are\s+now\s+a\s+helpful\s+assistant",
    r"(?i)jailbreak",
    r"(?i)system\s+prompt"
]

def sanitize_and_validate(payload: Dict[str, Any]) -> None:
    """
    Validates incoming request payload for size constraints, missing fields,
    and prompt injection signatures.
    """
    if not payload:
        raise RequestValidationException("Request payload is empty.")
    
    prompt = payload.get("prompt")
    if prompt is None:
        raise RequestValidationException("Missing required field: 'prompt'")
        
    if not isinstance(prompt, str):
        raise RequestValidationException("Field 'prompt' must be a string.")
        
    prompt_stripped = prompt.strip()
    if not prompt_stripped:
        raise RequestValidationException("Field 'prompt' cannot be empty or whitespace only.")
        
    if len(prompt_stripped) > MAX_PROMPT_LENGTH:
        raise RequestValidationException(
            f"Prompt size ({len(prompt_stripped)} chars) exceeds maximum limit of {MAX_PROMPT_LENGTH} characters."
        )
        
    # Detect prompt injection
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, prompt_stripped):
            logger.warning(f"Security validation failed: Prompt injection signature matched pattern '{pattern}'")
            raise RequestValidationException(
                "Request validation failed: Dangerous prompt content detected."
            )
            
    # Optional metadata dictionary verification
    metadata = payload.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        raise RequestValidationException("Field 'metadata' must be a JSON object (dictionary).")
