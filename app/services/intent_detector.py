import re
from typing import Dict, Any, Tuple
from app.core.llm import llm_client
from app.core.logging import logger

INTENT_MAP = {
    "Proposal": [r"\bproposal\b", r"\bpitch\b", r"\bbid\b", r"\brfp\b", r"\btender\b"],
    "Technical Design": [r"\btechnical\s+design\b", r"\bsystem\s+design\b", r"\bdesign\s+document\b", r"\bdesign\s+doc\b"],
    "PRD": [r"\bprd\b", r"\bproduct\s+requirement\b", r"\brequirements\s+document\b"],
    "Meeting Minutes": [r"\bminutes\b", r"\bmeeting\s+notes\b", r"\bmeeting\s+summary\b", r"\baction\s+items\b"],
    "Architecture": [r"\barchitecture\b", r"\bhld\b", r"\bhigh\s+level\s+design\b"],
    "SOP": [r"\bsop\b", r"\bstandard\s+operating\b", r"\boperating\s+procedure\b"],
    "Migration Guide": [r"\bmigration\s+guide\b", r"\bmigration\s+plan\b", r"\bmigrate\b", r"\bmigration\b"],
    "Business Report": [r"\bbusiness\s+report\b", r"\bmarket\s+analysis\b", r"\bfinancial\s+report\b", r"\bquarterly\s+report\b"],
    "API Documentation": [r"\bapi\s+doc\b", r"\bapi\s+documentation\b", r"\bendpoints\b", r"\bswagger\b", r"\bopenapi\b"]
}

class IntentDetector:
    """Classifies user requests into enterprise document types."""
    
    def detect_intent(self, prompt: str) -> str:
        """
        Detects document intent. First uses fast deterministic keyword regex rules.
        If no matches, returns 'Unknown' so the planner can make reasonable assumptions.
        """
        logger.info("IntentDetector: Analyzing request intent.")
        prompt_lower = prompt.lower()
        
        # Rule-based classification
        matched_intents = []
        for intent, patterns in INTENT_MAP.items():
            for pattern in patterns:
                if re.search(pattern, prompt_lower):
                    matched_intents.append(intent)
                    break # Match found for this intent
                    
        if len(matched_intents) == 1:
            logger.info(f"IntentDetector: Classified intent as '{matched_intents[0]}' via rules.")
            return matched_intents[0]
        elif len(matched_intents) > 1:
            # If multiple trigger, return the first matching one
            logger.info(f"IntentDetector: Multiple intents matched: {matched_intents}. Selecting first: '{matched_intents[0]}'")
            return matched_intents[0]
            
        logger.info("IntentDetector: No rules matched. Classifying as 'Unknown' to let Planner reason.")
        return "Unknown"

# Global service instance
intent_detector = IntentDetector()
