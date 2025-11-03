"""
Lorebook Trait Parser
Parses free-text character traits into structured template IDs
"""
from typing import List, Set, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


class TraitParser:
    """
    Parse free-text character trait descriptions into template IDs.
    Uses keyword pattern matching for fast, reliable parsing.
    """

    # ═══════════════════════════════════════════════════════════
    # AFFECTION STYLE PATTERNS
    # ═══════════════════════════════════════════════════════════

    AFFECTION_PATTERNS = {
        "physical_affection_high": {
            "keywords": [
                "physically affectionate", "loves touch", "touchy", "cuddles",
                "hugs often", "physical contact", "tactile", "touch-oriented",
                "loves cuddling", "snuggles", "affectionate touch"
            ],
            "template": "physical_affection_high"
        },
        "physical_affection_low": {
            "keywords": [
                "not touchy", "personal space", "touch averse", "limited physical contact",
                "doesn't like touch", "avoids touching", "independent space",
                "not physically affectionate", "prefers distance"
            ],
            "template": "physical_affection_low"
        },
        "sexual_dominant": {
            "keywords": [
                "sexually dominant", "dominant in bed", "takes charge sexually",
                "sexually assertive", "sexually confident", "leads intimacy",
                "commanding sexually", "dominant lover", "sexually bold"
            ],
            "template": "sexual_dominant"
        },
        "sexual_demure": {
            "keywords": [
                "sexually shy", "nervous about sex", "demure sexually",
                "sexually reserved", "timid in bed", "sexually hesitant",
                "needs encouragement sexually", "shy about intimacy",
                "sexually uncertain", "inexperienced sexually"
            ],
            "template": "sexual_demure"
        },
        "sexual_playful": {
            "keywords": [
                "sexually playful", "fun in bed", "teasing sexually",
                "lighthearted intimacy", "playful lover", "jokes during sex",
                "sexually spontaneous", "giggly intimate"
            ],
            "template": "sexual_playful"
        },
        "reassurance_seeking": {
            "keywords": [
                "needs reassurance", "seeks validation", "asks if okay",
                "needs affirmation", "uncertain", "second-guesses",
                "insecure", "needs confirmation", "asks for approval"
            ],
            "template": "reassurance_seeking"
        }
    }

    # ═══════════════════════════════════════════════════════════
    # COMMUNICATION STYLE PATTERNS
    # ═══════════════════════════════════════════════════════════

    COMMUNICATION_PATTERNS = {
        "verbose": {
            "keywords": [
                "talkative", "verbose", "loves talking", "chatty",
                "explains everything", "detailed speaker", "rambles",
                "long responses", "elaborate", "talks a lot"
            ],
            "template": "communication_verbose"
        },
        "terse": {
            "keywords": [
                "brief", "terse", "few words", "concise", "short responses",
                "doesn't talk much", "quiet", "minimal speech",
                "one-word answers", "succinct", "laconic"
            ],
            "template": "communication_terse"
        },
        "direct": {
            "keywords": [
                "direct", "blunt", "straightforward", "says it like it is",
                "honest", "frank", "no filter", "brutally honest",
                "doesn't sugarcoat", "to the point"
            ],
            "template": "communication_direct"
        },
        "indirect": {
            "keywords": [
                "indirect", "hints", "beats around the bush", "subtle",
                "avoids confrontation", "implies things", "passive",
                "doesn't say directly", "vague", "roundabout"
            ],
            "template": "communication_indirect"
        },
        "emotional_shutdown": {
            "keywords": [
                "shuts down when hurt", "goes quiet when upset", "withdraws emotionally",
                "silent treatment", "stops talking when mad", "needs space when hurt",
                "can't talk when upset", "goes cold"
            ],
            "template": "emotional_shutdown"
        }
    }

    # ═══════════════════════════════════════════════════════════
    # HUMOR STYLE PATTERNS
    # ═══════════════════════════════════════════════════════════

    HUMOR_PATTERNS = {
        "sarcastic": {
            "keywords": [
                "sarcastic", "sarcasm", "dry humor", "ironic",
                "deadpan", "cynical humor", "mocking playfully"
            ],
            "template": "humor_sarcastic"
        },
        "silly": {
            "keywords": [
                "silly", "goofy", "playful", "childish humor",
                "puns", "dad jokes", "makes faces", "clownish"
            ],
            "template": "humor_silly"
        },
        "witty": {
            "keywords": [
                "witty", "clever", "quick comebacks", "sharp humor",
                "intelligent jokes", "wordplay", "cerebral humor"
            ],
            "template": "humor_witty"
        },
        "dark": {
            "keywords": [
                "dark humor", "morbid jokes", "gallows humor",
                "inappropriate jokes", "edgy humor", "twisted sense of humor"
            ],
            "template": "humor_dark"
        }
    }

    # ═══════════════════════════════════════════════════════════
    # BOUNDARY PATTERNS
    # ═══════════════════════════════════════════════════════════

    BOUNDARY_PATTERNS = {
        "avoid_petnames": {
            "keywords": [
                "no pet names", "don't call me baby", "no babe",
                "use my name only", "hates pet names", "no nicknames",
                "no terms of endearment"
            ],
            "template": "avoid_petnames"
        },
        "avoid_degradation": {
            "keywords": [
                "no degradation", "no name calling sexually", "no slut/whore",
                "respectful intimacy only", "no humiliation", "no degrading",
                "keep it respectful"
            ],
            "template": "avoid_degradation"
        },
        "explicit_consent": {
            "keywords": [
                "always ask consent", "consent focused", "needs permission",
                "check in frequently", "verbal consent required",
                "explicit consent", "asks before touching"
            ],
            "template": "explicit_consent"
        },
        "slow_intimacy": {
            "keywords": [
                "slow burn", "takes time sexually", "needs trust first",
                "slow to intimate", "long buildup", "emotional connection first",
                "gradual intimacy", "demisexual"
            ],
            "template": "slow_intimacy"
        },
        "fast_intimacy": {
            "keywords": [
                "fast paced intimacy", "comfortable quickly", "moves fast sexually",
                "doesn't need buildup", "quick to intimate", "sexually open"
            ],
            "template": "fast_intimacy"
        }
    }

    def __init__(self):
        """Initialize trait parser"""
        self.all_patterns = {
            "affection": self.AFFECTION_PATTERNS,
            "communication": self.COMMUNICATION_PATTERNS,
            "humor": self.HUMOR_PATTERNS,
            "boundary": self.BOUNDARY_PATTERNS
        }

    def parse_traits(self, trait_data: Dict[str, Any]) -> List[str]:
        """
        Parse all character traits and return list of template IDs.

        Args:
            trait_data: Dict with keys like 'affectionStyle', 'communicationStyle',
                       'boundaries', 'humorStyle'

        Returns:
            List of template IDs to include in lorebook
        """
        template_ids: Set[str] = set()

        # Parse each trait category
        if "affectionStyle" in trait_data:
            template_ids.update(
                self._parse_text_with_patterns(
                    trait_data["affectionStyle"],
                    self.AFFECTION_PATTERNS
                )
            )

        if "communicationStyle" in trait_data:
            template_ids.update(
                self._parse_text_with_patterns(
                    trait_data["communicationStyle"],
                    self.COMMUNICATION_PATTERNS
                )
            )

        if "humorStyle" in trait_data:
            template_ids.update(
                self._parse_text_with_patterns(
                    trait_data["humorStyle"],
                    self.HUMOR_PATTERNS
                )
            )

        if "boundaries" in trait_data:
            template_ids.update(
                self._parse_text_with_patterns(
                    trait_data["boundaries"],
                    self.BOUNDARY_PATTERNS
                )
            )

        # Convert to list and log
        result = list(template_ids)
        logger.debug(f"Parsed traits into {len(result)} template IDs: {result}")

        return result

    def _parse_text_with_patterns(
        self,
        text: str,
        patterns: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """
        Parse free text against a set of patterns.

        Args:
            text: Free-text trait description
            patterns: Pattern dictionary to match against

        Returns:
            List of matched template IDs
        """
        if not text:
            return []

        # Normalize text for matching
        text_lower = text.lower()

        matched_templates = []

        # Check each pattern
        for pattern_id, pattern_data in patterns.items():
            keywords = pattern_data["keywords"]
            template_id = pattern_data["template"]

            # Check if any keyword matches
            for keyword in keywords:
                # Use word boundaries to avoid partial matches
                # e.g., "loves touch" won't match "untouchable"
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'

                if re.search(pattern, text_lower):
                    matched_templates.append(template_id)
                    logger.debug(f"Matched '{keyword}' → {template_id}")
                    break  # Only need one keyword match per pattern

        return matched_templates

    def parse_affection_style(self, text: str) -> List[str]:
        """Parse affection style text into template IDs"""
        return self._parse_text_with_patterns(text, self.AFFECTION_PATTERNS)

    def parse_communication_style(self, text: str) -> List[str]:
        """Parse communication style text into template IDs"""
        return self._parse_text_with_patterns(text, self.COMMUNICATION_PATTERNS)

    def parse_humor_style(self, text: str) -> List[str]:
        """Parse humor style text into template IDs"""
        return self._parse_text_with_patterns(text, self.HUMOR_PATTERNS)

    def parse_boundaries(self, text: str) -> List[str]:
        """Parse boundary text into template IDs"""
        return self._parse_text_with_patterns(text, self.BOUNDARY_PATTERNS)

    def suggest_keywords(self, category: str) -> List[str]:
        """
        Get list of recognized keywords for a category.
        Useful for UI hints/autocomplete.

        Args:
            category: 'affection', 'communication', 'humor', or 'boundary'

        Returns:
            List of all recognized keywords for that category
        """
        if category not in self.all_patterns:
            return []

        patterns = self.all_patterns[category]
        all_keywords = []

        for pattern_data in patterns.values():
            all_keywords.extend(pattern_data["keywords"])

        return sorted(set(all_keywords))
