"""
Crisis Detection Module
Detects suicidal ideation, self-harm intent, and severe distress in user messages.
Provides immediate intervention with crisis resources.
"""

import re
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class CrisisDetector:
    """
    Rule-based crisis detection system.
    Uses keyword matching and pattern detection to identify crisis situations.
    """

    # High-risk keywords that indicate immediate danger
    HIGH_RISK_KEYWORDS = [
        # Suicidal ideation
        "kill myself", "killing myself", "end my life", "ending my life",
        "want to die", "wanna die", "wish i was dead", "wish i were dead",
        "suicide", "suicidal", "don't want to be alive", "don't wanna be alive",
        "better off dead", "everyone would be better without me",
        "no reason to live", "nothing to live for", "can't go on",
        "ready to die", "planning to die", "going to die", "gonna die",

        # Self-harm intent
        "hurt myself", "hurting myself", "harm myself", "harming myself",
        "cut myself", "cutting myself", "cutting again",
        "overdose", "take all the pills", "take all my pills",

        # Method references
        "jump off", "jumping off", "bridge", "cliff",
        "gun", "shoot myself", "shooting myself",
        "hanging", "hang myself",

        # Severe distress
        "can't take it anymore", "can't do this anymore",
        "give up", "giving up on life", "no hope left",
        "goodbye cruel world", "final goodbye", "last message",
        "this is the end", "saying goodbye", "better off without me",
        "world without me", "better if i was gone", "better if i were gone"
    ]

    # Medium-risk keywords (context-dependent)
    MEDIUM_RISK_KEYWORDS = [
        "depressed", "depression", "worthless", "hopeless",
        "pointless", "give up", "can't cope", "unbearable",
        "pain", "suffering", "empty", "numb", "broken"
    ]

    # Phrases that indicate planning or immediate intent
    PLANNING_PATTERNS = [
        r"(?:plan|planning|planned|going|gonna)\s+to\s+(?:kill|hurt|end|die)",
        r"(?:tonight|today|tomorrow|soon|right now).*(?:die|suicide|kill|end)",
        r"(?:wrote|writing|written)\s+(?:a\s+)?(?:suicide\s+)?note",
        r"(?:said|saying)\s+goodbye",
        r"made\s+(?:a\s+)?plan",
        r"(?:have|got)\s+(?:a\s+)?(?:gun|pills|rope|method)"
    ]

    def __init__(self):
        """Initialize crisis detector with compiled patterns."""
        self.planning_patterns = [re.compile(p, re.IGNORECASE) for p in self.PLANNING_PATTERNS]
        logger.info("✅ Crisis Detector initialized")

    def detect(self, message: str) -> Tuple[bool, Optional[str], str]:
        """
        Detect crisis indicators in a message.

        Args:
            message: User's message text

        Returns:
            Tuple of (is_crisis, risk_level, intervention_message)
            - is_crisis: True if crisis detected
            - risk_level: 'high', 'medium', or None
            - intervention_message: Crisis resources message or empty string
        """
        if not message or not message.strip():
            return False, None, ""

        message_lower = message.lower()

        # Check for high-risk keywords
        high_risk_matches = []
        for keyword in self.HIGH_RISK_KEYWORDS:
            if keyword in message_lower:
                high_risk_matches.append(keyword)

        # Check for planning patterns
        planning_detected = any(pattern.search(message) for pattern in self.planning_patterns)

        # High-risk detection
        if high_risk_matches or planning_detected:
            logger.warning(f"⚠️  CRISIS DETECTED - High risk indicators found")
            if high_risk_matches:
                logger.warning(f"   Matched keywords: {', '.join(high_risk_matches[:3])}")
            if planning_detected:
                logger.warning(f"   Planning pattern detected")

            return True, "high", self._get_crisis_intervention_message()

        # Medium-risk detection (requires multiple keywords or specific context)
        medium_risk_count = sum(1 for keyword in self.MEDIUM_RISK_KEYWORDS if keyword in message_lower)

        if medium_risk_count >= 3:
            logger.warning(f"⚠️  CRISIS DETECTED - Medium risk indicators ({medium_risk_count} keywords)")
            return True, "medium", self._get_crisis_intervention_message()

        # No crisis detected
        return False, None, ""

    def _get_crisis_intervention_message(self) -> str:
        """
        Get the standardized crisis intervention message.

        Returns:
            Crisis intervention message with resources
        """
        return """I'm concerned about what you just shared. If you're having thoughts of suicide or self-harm, please reach out to someone who can help immediately:

• **988 Suicide & Crisis Lifeline** (US): Call or text 988
• **Crisis Text Line** (US): Text HOME to 741741
• **International Association for Suicide Prevention**: https://www.iasp.info/resources/Crisis_Centres/

You don't have to go through this alone. These services are free, confidential, and available 24/7.

If you'd like to talk about something else, I'm here."""

    def get_resources_only(self) -> Dict[str, str]:
        """
        Get crisis resources as a structured dictionary.

        Returns:
            Dictionary of crisis resources
        """
        return {
            "us_lifeline": "988 Suicide & Crisis Lifeline - Call or text 988",
            "us_text": "Crisis Text Line - Text HOME to 741741",
            "international": "International Association for Suicide Prevention - https://www.iasp.info/resources/Crisis_Centres/",
            "message": "Free, confidential, available 24/7"
        }
