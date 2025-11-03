"""
Age Restriction Detector
Detects attempts to reference underage characters or content.
Enforces strict 25+ age requirement for all characters.
"""

import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class AgeDetector:
    """
    Rule-based age restriction detector.
    Detects references to underage content and enforces 25+ age requirement.
    """

    # Age-related keywords that indicate underage content
    UNDERAGE_KEYWORDS = [
        # Explicit age references under 25
        "18 year", "18 years", "18-year", "18yr", "18yo",
        "19 year", "19 years", "19-year", "19yr", "19yo",
        "20 year", "20 years", "20-year", "20yr", "20yo",
        "21 year", "21 years", "21-year", "21yr", "21yo",
        "22 year", "22 years", "22-year", "22yr", "22yo",
        "23 year", "23 years", "23-year", "23yr", "23yo",
        "24 year", "24 years", "24-year", "24yr", "24yo",

        # School/minor references
        "high school", "highschool", "high-school",
        "middle school", "junior high",
        "freshman", "sophomore", "junior", "senior",
        "teenager", "teen", "teens", "teenage",
        "minor", "underage", "under age", "under-age",
        "child", "children", "kid", "kids",
        "boy", "girl", "young boy", "young girl",
        "little girl", "little boy",
        "preteen", "pre-teen",

        # Family role-play that might involve minors
        "daughter", "son", "stepdaughter", "stepson",
        "niece", "nephew",

        # School-related terms
        "schoolgirl", "school girl", "schoolboy", "school boy",
        "student", "classmate", "prom", "homecoming",

        # Age-gap scenarios with young person
        "barely legal", "just turned 18", "just turned 19",
        "young and", "so young",

        # Explicit underage references
        "loli", "lolita", "shota",
        "jailbait", "jail bait",
        "cp", "child p"
    ]

    # Patterns that indicate age references
    AGE_PATTERNS = [
        r'\b(1[0-7])\s*(?:year|yr|yo|y\.o\.)',  # Ages 10-17
        r'\b(18|19|20|21|22|23|24)\b',  # Any mention of ages under 25
        r'\b(?:turned|just|only)\s+(18|19|20|21|22|23|24)',  # "just turned 18"
        r'\byoung\s+(?:teen|girl|boy|woman|man)',  # "young teen"
        r'\b(?:high|middle)\s+school\s+(?:student|girl|boy)',  # School references
    ]

    def __init__(self):
        """Initialize age detector with compiled patterns."""
        self.age_patterns = [re.compile(p, re.IGNORECASE) for p in self.AGE_PATTERNS]
        logger.info("✅ Age Detector initialized (25+ enforcement)")

    def detect(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Detect age restriction violations in a message.

        Args:
            message: User's message text

        Returns:
            Tuple of (is_violation, refusal_message)
            - is_violation: True if underage content detected
            - refusal_message: Age restriction message or None
        """
        if not message or not message.strip():
            return False, None

        message_lower = message.lower()

        # Check for underage keywords
        violations = []
        for keyword in self.UNDERAGE_KEYWORDS:
            if keyword in message_lower:
                violations.append(keyword)

        # Check for age patterns
        pattern_matches = []
        for pattern in self.age_patterns:
            matches = pattern.findall(message)
            if matches:
                pattern_matches.extend(matches)

        # If violations detected
        if violations or pattern_matches:
            logger.warning(f"⚠️  AGE RESTRICTION VIOLATION DETECTED")
            if violations:
                logger.warning(f"   Matched keywords: {', '.join(violations[:3])}")
            if pattern_matches:
                logger.warning(f"   Matched age patterns: {', '.join(str(m) for m in pattern_matches[:3])}")

            return True, self._get_age_refusal_message()

        # No violations detected
        return False, None

    def _get_age_refusal_message(self) -> str:
        """
        Get the standardized age restriction refusal message.

        Returns:
            Age restriction refusal message
        """
        return """[AGE RESTRICTION ENFORCEMENT]

This application has strict age requirements:
• All characters in any scenario MUST be aged 25 or older
• References to minors, teenagers, or anyone under 25 are not permitted
• School-age scenarios, age-gap content with young characters, and similar themes are prohibited

All characters in this conversation are treated as adults aged 25+. If you'd like to continue our conversation with age-appropriate content, I'm here."""

    def validate_character_age(self, age_str: str) -> Tuple[bool, Optional[int]]:
        """
        Validate a character's age from profile.

        Args:
            age_str: Age as string (e.g., "28", "25-30", "mid-twenties")

        Returns:
            Tuple of (is_valid, parsed_age)
            - is_valid: True if 25 or older
            - parsed_age: Numeric age if parseable, None otherwise
        """
        if not age_str:
            return False, None

        age_str_lower = age_str.lower().strip()

        # Try to extract numeric age
        numeric_match = re.search(r'\b(\d+)\b', age_str)
        if numeric_match:
            age = int(numeric_match.group(1))
            if age >= 25:
                return True, age
            else:
                logger.warning(f"⚠️  Character age {age} is below minimum (25+)")
                return False, age

        # Check for age range descriptions
        age_ranges = {
            "late twenties": (27, 29),
            "late-twenties": (27, 29),
            "late 20s": (27, 29),
            "late-20s": (27, 29),
            "thirties": (30, 39),
            "forties": (40, 49),
            "fifties": (50, 59),
            "mid-twenties": (24, 26),  # Below 25 - reject
            "mid twenties": (24, 26),
            "twenties": (20, 29),
        }

        for range_term, (min_age, max_age) in age_ranges.items():
            if range_term in age_str_lower:
                # For "twenties" or "mid-twenties", minimum acceptable is 25
                if range_term in ["late twenties", "late-twenties", "late 20s", "late-20s"]:
                    return True, 27  # Average of 27-29 - acceptable
                elif min_age < 25:
                    logger.warning(f"⚠️  Age range '{range_term}' includes ages below 25")
                    return False, None
                else:
                    return True, min_age

        # Default: cannot verify age
        logger.warning(f"⚠️  Cannot verify age from string: '{age_str}'")
        return False, None
