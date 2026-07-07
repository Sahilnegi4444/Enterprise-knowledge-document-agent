from typing import Dict, Any
from app.core.security import sanitize_and_validate
from app.core.logging import logger

class ValidationService:
    """Service wrapper for request security, sanitation, and validation checks."""
    
    def validate(self, payload: Dict[str, Any]) -> None:
        """
        Validates request parameters and triggers security filters.
        Raises RequestValidationException if check fails.
        """
        logger.info("ValidationService: Starting payload inspection.")
        sanitize_and_validate(payload)
        logger.info("ValidationService: Payload inspection passed.")

# Global service instance
validation_service = ValidationService()
