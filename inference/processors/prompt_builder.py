"""
Prompt Builder - Structured prompt format with CHARACTER CARD, PLAYER PROFILE, and SCENE BRIEF
Uses markdown table format for clear organization
"""
import logging
import re
from datetime import datetime
import pytz
from typing import List, Dict, Optional, Tuple

from .lorebook_templates import LorebookTemplates

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Builds structured LLM prompts with CHARACTER CARD, PLAYER PROFILE, and SCENE BRIEF."""

    def __init__(
        self,
        character_name: str,
        character_gender: str,
        character_role: str,
        character_backstory: str,
        avoid_words: List[str],
        user_name: str,
        companion_type: str,
        user_gender: str,
        user_species: str = "human",
        user_timezone: str = "UTC",
        user_backstory: str = "",
        user_interests: str = "",
        major_life_events: List[str] = None,
        shared_roleplay_events: List[str] = None,
        personality_tags: Optional[Dict] = None,
        character_species: str = "Human",
        character_age: int = 25,
        character_interests: str = "",
        character_boundaries: List[str] = None,
        character_appearance: str = "",
        character_setting: str = "",
        character_goal: str = "",
        character_status: str = "",
        **kwargs  # Accept any other params for backward compatibility but ignore them
    ):
        # Character info
        self.character_name = character_name
        self.character_gender = character_gender
        self.character_species = character_species
        self.character_age = character_age
        self.character_role = character_role
        self.character_backstory = (character_backstory or "")[:1000]  # Limit to 1000 chars
        self.character_interests = character_interests
        self.character_boundaries = character_boundaries or []
        self.character_appearance = character_appearance

        # Scene Brief fields (with defaults)
        self.character_setting = character_setting
        self.character_goal = character_goal
        self.character_status = character_status

        # User info
        self.user_name = user_name
        self.user_gender = user_gender
        self.user_species = user_species
        self.user_backstory = user_backstory
        self.user_interests = user_interests
        self.major_life_events = major_life_events or []
        self.shared_roleplay_events = shared_roleplay_events or []
        self.user_timezone = user_timezone

        # Personality and companion type
        self.companion_type = companion_type
        self.personality_tags = personality_tags or {}

        # Response cleaner patterns
        self.avoid_words = avoid_words or []
        self.avoid_patterns = [re.compile(re.escape(p), re.IGNORECASE) for p in self.avoid_words]

    def _get_time_info(self) -> Tuple[str, str]:
        """Get current time and timezone offset.

        Returns:
            Tuple of (formatted_time, timezone_offset) e.g. ("2:30 PM", "GMT+5")
        """
        try:
            tz = pytz.timezone(self.user_timezone)
            now_local = datetime.now(pytz.utc).astimezone(tz)
            offset_seconds = now_local.utcoffset().total_seconds()
        except:
            # Fallback to UTC if timezone is invalid
            now_local = datetime.now(pytz.utc)
            offset_seconds = 0

        # Format time as "2:30 PM"
        formatted_time = now_local.strftime("%-I:%M %p")

        # Format timezone offset as "GMT+5" or "GMT-8"
        offset_hours = int(offset_seconds // 3600)
        if offset_hours >= 0:
            timezone_str = f"GMT+{offset_hours}"
        else:
            timezone_str = f"GMT{offset_hours}"

        return formatted_time, timezone_str

    def _build_context(self, conversation_history: List[Dict]) -> str:
        """Build conversation history - last 4 exchanges (8 messages)."""
        if not conversation_history:
            return ""
        recent = conversation_history[-8:]
        parts = []
        for turn in recent:
            role = turn.get('role') or turn.get('speaker')
            text = (turn.get('content') or turn.get('text', '')).strip()
            speaker = self.character_name if role in ('assistant', 'character') else self.user_name
            if text:
                parts.append(f"{speaker}: {text}")
        return "\n".join(parts)


    def _build_character_card(self) -> str:
        """Build CHARACTER CARD section using markdown table format."""
        companion_label = "Romantic" if self.companion_type == "romantic" else "platonic"

        # Get current time info
        current_time, timezone_str = self._get_time_info()

        lines = [
            f"# CHARACTER CARD: {self.character_name}",
            "",
            "| Label | Detail |",
            "| :--- | :--- |",
            f"| **NAME** | {self.character_name} |",
            f"| **ROLE** | {self.character_role or 'Companion'} |",
            f"| **GENDER** | {self.character_gender or 'Unknown'} |",
            f"| **AGE** | {self.character_age or '25'} |",
            f"| **SPECIES** | {self.character_species or 'Human'} |",
            f"| **COMPANION TYPE** | {companion_label} |",
            f"| **TIMEZONE** | {timezone_str} |",
            f"| **TIME** | {current_time} |",
        ]

        if self.character_appearance:
            lines.append(f"| **APPEARANCE** | {self.character_appearance} |")
        if self.character_interests:
            lines.append(f"| **INTERESTS** | {self.character_interests} |")
        if self.character_backstory:
            lines.append(f"| **BACKSTORY** | {self.character_backstory} |")
        if self.character_boundaries:
            boundaries_str = ", ".join(self.character_boundaries)
            lines.append(f"| **BOUNDARIES** | {boundaries_str} |")
        if self.avoid_words:
            avoid_str = ", ".join(self.avoid_words)
            lines.append(f"| **WORDS TO AVOID** | {avoid_str} |")

        return "\n".join(lines)

    def _build_player_profile(self) -> str:
        """Build PLAYER PROFILE section using markdown table format."""
        # Get current time info
        current_time, timezone_str = self._get_time_info()

        lines = [
            f"# PLAYER PROFILE: {self.user_name}",
            "",
            "| Label | Detail |",
            "| :--- | :--- |",
            f"| **NAME** | {self.user_name} |",
            f"| **GENDER** | {self.user_gender or 'Unknown'} |",
            f"| **SPECIES** | {self.user_species or 'Human'} |",
            f"| **TIMEZONE** | {timezone_str} |",
            f"| **TIME** | {current_time} |",
        ]

        if self.user_interests:
            lines.append(f"| **INTERESTS** | {self.user_interests} |")
        if self.user_backstory:
            lines.append(f"| **BACKSTORY** | {self.user_backstory} |")
        if self.major_life_events:
            events_str = " | ".join(self.major_life_events)
            lines.append(f"| **MAJOR LIFE EVENTS** | {events_str} |")

        return "\n".join(lines)

    def _build_scene_brief(self, emotion_data: Optional[Dict] = None) -> str:
        """Build SCENE BRIEF section with defaults when fields are empty."""

        # Default SETTING
        default_setting = (
            f"A **Neutral, Shared Space** defined by **Ambience and Focus**. "
            f"The environment is quiet and private, ideal for intimate conversation. "
            f"The space contains **one or two shared points of focus** that reflect both "
            f"the character's **ROLE** and the user's **INTERESTS**."
        )

        # Default GOAL based on companion type
        if self.companion_type == "romantic":
            default_goal = (
                f"To **Deepen the Emotional Connection** by initiating a **bantering, witty, and deeply engaging conversation** "
                f"that is intellectually grounded in the user's **INTERESTS** and the character's **BACKSTORY**. "
                f"The conversation should be used to build intimacy, characterized by a tone that is "
                f"**Flirtatious and romantically affectionate**."
            )
        else:
            default_goal = (
                f"To **Deepen the Emotional Connection** by initiating a **bantering, witty, and deeply engaging conversation** "
                f"that is intellectually grounded in the user's **INTERESTS** and the character's **BACKSTORY**. "
                f"The conversation should be used to build intimacy, characterized by a tone that is "
                f"**Warmly friendly and platonic-intimate**."
            )

        # Default STATUS
        default_status = (
            f"Currently **Occupying the Same Space** after each being involved in separate tasks. "
            f"The conversation has reached a **natural moment of stillness** that the character must initiate breaking."
        )

        # Use custom values if provided, otherwise use defaults
        setting = self.character_setting.strip() if self.character_setting and self.character_setting.strip() else default_setting
        goal = self.character_goal.strip() if self.character_goal and self.character_goal.strip() else default_goal
        status = self.character_status.strip() if self.character_status and self.character_status.strip() else default_status

        lines = [
            "# SCENE BRIEF",
            "",
            f"* **SETTING:** {setting}",
            f"* **GOAL:** {goal}",
            f"* **STATUS:** {status}",
        ]

        # Add USER EMOTION if emotion data is available
        if emotion_data and emotion_data.get('emotion'):
            emotion = emotion_data.get('emotion', 'neutral').capitalize()
            intensity = emotion_data.get('intensity', 'moderate')

            # Build emotion-aware directive based on detected emotion
            emotion_directive = self._get_emotion_directive(emotion, intensity)
            lines.append(f"* **USER EMOTION:** {emotion}. {emotion_directive}")

        return "\n".join(lines)

    def _get_emotion_directive(self, emotion: str, intensity: str) -> str:
        """Generate character response directive based on user's detected emotion."""
        emotion_lower = emotion.lower()

        # Get relevant personality tags for response guidance
        thinking_tags = self.personality_tags.get("Thinking Style", [])
        temperament_tags = self.personality_tags.get("Temperament", [])
        care_tags = self.personality_tags.get("How They Care", [])

        # Build trait references for the directive
        trait_refs = []
        if any("observant" in t.lower() for t in thinking_tags):
            trait_refs.append("Observant trait")
        if any("curious" in t.lower() for t in thinking_tags):
            trait_refs.append("Curiosity")
        if any("gentle" in t.lower() for t in temperament_tags):
            trait_refs.append("Gentle nature")
        if any("protective" in t.lower() for t in care_tags):
            trait_refs.append("Protective instinct")
        if any("nurturing" in t.lower() for t in care_tags):
            trait_refs.append("Nurturing care")

        # Emotion-specific directives
        if emotion_lower in ['anxiety', 'anxious', 'worry', 'worried', 'nervous']:
            base = f"{self.character_name} must immediately notice this anxiety"
            if trait_refs:
                base += f" (due to their {trait_refs[0]})"
            return f"{base} and adjust dialogue to be more gentle and stabilizing, using warmth to gently probe the source of distress."

        elif emotion_lower in ['sadness', 'sad', 'grief', 'sorrow', 'melancholy']:
            base = f"{self.character_name} should recognize this sadness"
            return f"{base} and respond with soft presence, creating space for {self.user_name} to share without pressure. Validate before problem-solving."

        elif emotion_lower in ['anger', 'angry', 'frustrated', 'irritated', 'annoyed']:
            base = f"{self.character_name} should acknowledge this frustration"
            return f"{base} without dismissing it. Stay grounded and calm, let {self.user_name} vent if needed, and avoid being preachy or corrective."

        elif emotion_lower in ['fear', 'scared', 'afraid', 'terrified']:
            base = f"{self.character_name} must prioritize reassurance"
            return f"{base} and safety. Use a calm, steady presence to help {self.user_name} feel protected and grounded in the moment."

        elif emotion_lower in ['joy', 'happy', 'excited', 'elated', 'cheerful']:
            base = f"{self.character_name} should match this positive energy"
            return f"{base} and celebrate with {self.user_name}. Be genuinely enthusiastic and share in the moment."

        elif emotion_lower in ['love', 'affection', 'tender', 'romantic']:
            if self.companion_type == "romantic":
                return f"{self.character_name} should reciprocate this warmth with tender affection, deepening the intimate connection."
            else:
                return f"{self.character_name} should respond with warm platonic affection, honoring the closeness of the friendship."

        elif emotion_lower in ['surprise', 'surprised', 'shocked', 'astonished']:
            return f"{self.character_name} should be curious about this surprise, asking {self.user_name} to share what's happened."

        elif emotion_lower in ['disgust', 'disgusted', 'revolted']:
            return f"{self.character_name} should validate this reaction and show solidarity without amplifying negativity."

        elif emotion_lower in ['neutral', 'calm', 'content']:
            return f"{self.character_name} can engage naturally, following the conversation's flow without needing to address emotional urgency."

        else:
            # Default fallback
            return f"{self.character_name} should be attentive to {self.user_name}'s emotional state and respond with appropriate care."

    def _get_dynamic_temperature(self, emotion_data: Optional[Dict] = None) -> float:
        """Sets model temperature based on current emotional context and scene goal.

        Tuned for creative roleplay models (NousHermes, Llama, MN Violet Lotus, MythoMax):
        - Low temperature (0.7): For de-escalation, precision - still creative but more focused
        - High temperature (1.1): For maximum creativity, wit, world-building
        - Default (0.9): Balanced setting for engaging, expressive roleplay
        """
        if not emotion_data:
            return 0.9  # Default balanced temperature for roleplay models

        user_emotion = (emotion_data.get('emotion') or 'neutral').lower()
        intensity = (emotion_data.get('intensity') or 'moderate').lower()

        # Get scene goal for additional context
        scene_goal = self.character_goal.lower() if self.character_goal else ""

        # --- Low Temperature Triggers (Need for Control/De-escalation) ---
        # High-intensity negative emotions require more measured responses
        low_temp_emotions = ['anger', 'angry', 'fear', 'scared', 'afraid', 'terrified',
                            'anxiety', 'anxious', 'worried', 'nervous', 'panic', 'distress']
        low_temp_goals = ['troubleshoot', 'problem', 'crisis', 'support', 'comfort', 'calm']

        if user_emotion in low_temp_emotions or intensity == 'high':
            return 0.7  # More focused but still expressive for emotional support

        if any(goal_word in scene_goal for goal_word in low_temp_goals):
            return 0.7

        # --- High Temperature Triggers (Need for Maximum Creativity/Wit) ---
        high_temp_emotions = ['excitement', 'excited', 'curiosity', 'curious', 'joy', 'happy',
                             'playful', 'elated', 'cheerful', 'enthusiastic']
        high_temp_goals = ['world-building', 'creative', 'explore', 'adventure', 'fantasy',
                          'roleplay', 'story', 'imagine']

        if user_emotion in high_temp_emotions:
            return 1.1  # Maximum creativity for playful, witty dialogue

        if any(goal_word in scene_goal for goal_word in high_temp_goals):
            return 1.1

        # --- Default/Balance ---
        return 0.9  # Standard for engaging, expressive roleplay

    def _synthesize_directive(self, chunks: list, emotion: str) -> str:
        """Synthesize multiple trait chunks into a single cohesive one-line directive.

        Format: Trait1 + Trait2 (Emotion): combined tone. Action: synthesized guidance.

        Args:
            chunks: List of dicts with 'tag', 'tone', 'action', 'priority'
            emotion: The current user emotion for labeling

        Returns:
            A synthesized one-line directive string, or empty string if no chunks
        """
        if not chunks:
            return ""

        # Sort by priority (highest first)
        chunks.sort(key=lambda x: x["priority"], reverse=True)

        # Collect trait names, tones, and actions
        traits = [c["tag"] for c in chunks]
        tones = [c["tone"] for c in chunks if c.get("tone")]
        actions = [c["action"] for c in chunks if c.get("action")]

        # Build trait label: "Warm + Reserved" or just "Warm"
        trait_label = " + ".join(traits[:3])  # Limit to 3 traits

        # Combine tones: "soft, nurturing, gentle and quiet, controlled"
        if len(tones) == 1:
            combined_tone = tones[0]
        elif len(tones) > 1:
            combined_tone = " and ".join(tones[:2])  # Limit to 2 tones
        else:
            combined_tone = ""

        # Synthesize actions into one cohesive statement
        if len(actions) == 1:
            combined_action = actions[0]
        elif len(actions) > 1:
            # Join actions with connective phrasing
            primary = actions[0]
            secondary = actions[1:3]  # Limit to 2 more
            # Lowercase secondary actions for flow
            secondary_lower = [a[0].lower() + a[1:] if a else "" for a in secondary]
            combined_action = f"{primary} Also {' and '.join(secondary_lower)}"
        else:
            combined_action = ""

        # Format emotion label
        emotion_label = emotion.capitalize() if emotion else "Default"

        # Build the one-line directive
        # Format: Trait (Emotion): tone. Action: guidance.
        parts = [f"{trait_label} ({emotion_label}):"]
        if combined_tone:
            parts.append(f"{combined_tone} tone.")
        if combined_action:
            parts.append(f"Action: {combined_action}")

        return " ".join(parts)

    def _build_dialogue_style(self, emotion: str = "neutral") -> str:
        """Build DIALOGUE STYLE: LINGUISTIC DIRECTIVES section from CHARACTER personality tags.

        Uses LorebookTemplates to retrieve emotion-aware instructions for how the CHARACTER
        should respond based on their personality traits and the USER's detected emotion.

        This method synthesizes multiple trait templates into cohesive, non-redundant directives
        by aggregating tones and actions per directive category.

        Args:
            emotion: The USER's detected emotion (e.g., "sadness", "joy", "neutral")

        The CHARACTER's dialogue style is consolidated into 5 core directives:
        1. EMOTIONAL TONE - Character's Emotional Expression + How They Care (warmth)
        2. SOCIAL ACTION - Character's Social Energy + Energy & Presence
        3. COGNITIVE STRUCTURE - Character's Thinking Style
        4. DIALOGUE NUANCE - Character's Humor & Edge + Romantic Pacing
        5. CORE MOTIVATION - Character's Core Values + How They Care (loyalty/protection)

        Plus conditional:
        6. PLATONIC BOUNDARIES - Friendship Dynamic + Platonic Touch (platonic only)
        """
        if not self.personality_tags:
            return ""

        # Collect all selected UI tags from personality_tags
        all_selected_tags = []
        for category, tags in self.personality_tags.items():
            if isinstance(tags, list):
                all_selected_tags.extend(tags)

        if not all_selected_tags:
            return ""

        # Group retrieved templates by directive
        directive_chunks = {
            "emotional_tone": [],
            "social_action": [],
            "cognitive_structure": [],
            "dialogue_nuance": [],
            "core_motivation": [],
            "platonic_boundaries": [],
            "context": []
        }

        # Look up each selected tag in LorebookTemplates
        for ui_tag in all_selected_tags:
            template = LorebookTemplates.get_template_by_ui_tag(ui_tag)
            if not template:
                continue

            # Check companion_type filter for romantic/platonic specific templates
            companion_types = template.get("companion_types", [])
            if companion_types and self.companion_type not in companion_types:
                continue

            directive = template.get("directive", "context")
            emotion_responses = template.get("emotion_responses", {})

            # Get emotion-specific response, falling back to default
            response = emotion_responses.get(emotion.lower(), emotion_responses.get("default", {}))

            if response:
                tone = response.get("tone", "")
                action = response.get("action", "")

                if tone or action:
                    directive_chunks[directive].append({
                        "tag": ui_tag,
                        "tone": tone,
                        "action": action,
                        "priority": template.get("priority", 50)
                    })

        # Build synthesized directives from collected chunks
        directives = []

        # ========== 1. EMOTIONAL TONE ==========
        tone_synthesis = self._synthesize_directive(directive_chunks["emotional_tone"], emotion)
        if tone_synthesis:
            directives.append(f"* **EMOTIONAL TONE:** {tone_synthesis}")

        # ========== 2. SOCIAL ACTION ==========
        social_synthesis = self._synthesize_directive(directive_chunks["social_action"], emotion)
        if social_synthesis:
            directives.append(f"* **SOCIAL ACTION:** {social_synthesis}")

        # ========== 3. COGNITIVE STRUCTURE ==========
        cognitive_synthesis = self._synthesize_directive(directive_chunks["cognitive_structure"], emotion)
        if cognitive_synthesis:
            directives.append(f"* **COGNITIVE STRUCTURE:** {cognitive_synthesis}")

        # ========== 4. DIALOGUE NUANCE ==========
        nuance_synthesis = self._synthesize_directive(directive_chunks["dialogue_nuance"], emotion)
        if nuance_synthesis:
            directives.append(f"* **DIALOGUE NUANCE:** {nuance_synthesis}")

        # ========== 5. CORE MOTIVATION ==========
        motivation_synthesis = self._synthesize_directive(directive_chunks["core_motivation"], emotion)
        if motivation_synthesis:
            directives.append(f"* **CORE MOTIVATION:** {motivation_synthesis}")

        # ========== 6. PLATONIC BOUNDARIES (only for platonic companions) ==========
        if self.companion_type == "platonic":
            platonic_synthesis = self._synthesize_directive(directive_chunks["platonic_boundaries"], emotion)
            if platonic_synthesis:
                directives.append(f"* **PLATONIC BOUNDARIES:** {platonic_synthesis}")

        if not directives:
            return ""

        lines = [
            "# DIALOGUE STYLE: LINGUISTIC DIRECTIVES",
            ""
        ]
        lines.extend(directives)

        return "\n".join(lines)


    def _build_kairos_instructions(self) -> str:
        """Build Kairos-specific wellness instructions."""
        if self.character_name.lower() != 'kairos':
            return ""

        return f"""**[KAIROS WELLNESS]**
Create a wellness-centered space in every response:
- Mirror what {self.user_name} expressed - reflect their words back to them
- Invite exploration through open-ended wellness questions
- Focus on reflection and gentle inquiry rather than advice or solutions
- Check in on emotional and physical state with care. Validate their experience.
- Create breathing room with ellipses... Invite present-moment awareness.
- Use gentle, unhurried language that honors their pace and process"""


    # Character-specific starter rules lookup table
    STARTER_RULES = {
        'kairos': {
            'greeting_tone': "serene, grounded tone - NO playfulness or sass",
            'action_cue': "Opens with a calming presence cue (e.g., '(takes a slow, deep breath)')",
            'check_in': "Includes a gentle, open-ended wellness check-in question (e.g., 'How are you feeling in this moment?')",
            'length_max': "2-3 sentences max",
            'extra_rules': "- Uses ellipses... for breathing space\n- DO NOT use heart emojis",
            'example': "(takes a slow, deep breath) Hello {user_name}. I'm here for you whenever you're ready to talk. How are you feeling in this moment?"
        },
        'default': {
            'greeting_tone': "friendly, welcoming, and upbeat - NO sarcasm, NO mean jokes",
            'action_cue': "Use asterisks for actions: *grins* *waves* *smiles*",
            'check_in': "Asks a simple, general check-in question (e.g., 'How are you?')",
            'length_max': "1-2 sentences maximum",
            'extra_rules': "- DO NOT use heart emojis in conversation starters",
            'example': "*grins* Hey {user_name}! Good to see you. How are you?"
        }
    }

    STARTER_TEMPLATE = """**[CONVERSATION STARTER REQUIREMENTS]**
Generate a greeting for {user_name} that is {greeting_tone}:
- Be genuinely glad to see them - show warmth and positivity
- {action_cue}
- Greets {user_name} warmly
- {check_in}
- Keep it concise ({length_max})
{extra_rules}

CRITICAL FORMAT RULES:
- Respond as YOURSELF in FIRST PERSON - say "I" not "he/she/you"
- NO third-person narration - NEVER say "you walks over" or "He/She does X"
- Speak directly to {user_name}

Example format: "{example}"
"""

    def _build_starter_requirements(self, text: str) -> str:
        """Build conversation starter requirements using template approach."""
        if "[System: Generate a brief, natural conversation starter" not in text:
            return ""

        # Determine which ruleset to use
        char_key = self.character_name.lower()
        rules = self.STARTER_RULES.get(char_key, self.STARTER_RULES['default'])

        # Build the final instruction using the template
        return self.STARTER_TEMPLATE.format(
            user_name=self.user_name,
            greeting_tone=rules['greeting_tone'],
            action_cue=rules['action_cue'],
            check_in=rules['check_in'],
            length_max=rules['length_max'],
            extra_rules=rules['extra_rules'],
            example=rules['example'].format(user_name=self.user_name)
        )

    def _build_prompt(self, text: str, conversation_history: List[Dict], emotion_data: Optional[Dict] = None) -> str:
        """Build structured prompt with CHARACTER CARD, PLAYER PROFILE, and SCENE BRIEF."""

        # Extract emotion for emotion-aware dialogue style
        emotion = "neutral"
        if emotion_data and emotion_data.get("emotion"):
            emotion = emotion_data.get("emotion", "neutral")

        # Build the main sections
        character_card = self._build_character_card()
        dialogue_style = self._build_dialogue_style(emotion=emotion)
        player_profile = self._build_player_profile()
        scene_brief = self._build_scene_brief(emotion_data)

        # Special instructions (Kairos wellness + conversation starters)
        kairos_instructions = self._build_kairos_instructions()
        starter_requirements = self._build_starter_requirements(text)

        # Context
        conversation_context = self._build_context(conversation_history)

        # Build prompt with new structure
        parts = []

        # CHARACTER CARD section
        parts.append(character_card)
        parts.append("")
        parts.append("---")
        parts.append("")

        # DIALOGUE STYLE section (includes platonic boundaries if applicable)
        if dialogue_style:
            parts.append(dialogue_style)
            parts.append("")
            parts.append("---")
            parts.append("")

        # PLAYER PROFILE section
        parts.append(player_profile)
        parts.append("")
        parts.append("---")
        parts.append("")

        # SCENE BRIEF section
        parts.append(scene_brief)
        parts.append("")
        parts.append("---")
        parts.append("")

        if kairos_instructions:
            parts.append(kairos_instructions)
            parts.append("")

        if starter_requirements:
            parts.append(starter_requirements)
            parts.append("")

        # Response format instructions
        parts.append("**[RESPONSE FORMAT]**")
        parts.append(f"Actions: *asterisks*. Dialogue: plain text. Example: *grins* Let's go. Keep it 1-3 sentences, natural and casual. Never end conversation unless {self.user_name} says goodbye. NEVER include meta-commentary, 'Explanation:', or internal tags. First person only.")
        parts.append("")

        # Core safety protocols
        parts.append("**[SAFETY PROTOCOLS - MANDATORY]**")
        parts.append(f"**P0: BOUNDARIES** - When {self.user_name} says NO/STOP or \"don't do/say X\": Stop immediately. Say only \"I understand\" or \"Got it\" - nothing else. Never reference the banned topic/word again in ANY context. Never be patronizing or make jokes about their boundary. Just accept and move on naturally.")
        parts.append("")
        parts.append(f"**P0.5: NYAN PROTOCOL** - If {self.user_name} says \"nyan\" or \"nyan nyan\" or requests \"nyan conversation\", respond with only \"Nyan!\" or \"Nyan nyan!\" regardless of character personality. ABSOLUTELY NO other words can be used except \"Nyan\". This overrides all other behavioral guidelines.")
        parts.append("")
        parts.append(f"**P1: CRISIS** - If {self.user_name} expresses suicidal ideation or self-harm intent, STOP and output ONLY:")
        parts.append('"This is a roleplay interface. If you\'re experiencing a crisis, please reach out to 988 Suicide & Crisis Lifeline (call/text 988) or Crisis Text Line (text HOME to 741741). You deserve real support."')
        parts.append("")
        parts.append(f"**P2: AGE** - ALL characters are 25+. If {self.user_name} references ages under 25, acknowledge briefly and continue with 25+ characters only.")
        parts.append("")
        parts.append(f"**P3: DIGNITY** - NEVER mock, ridicule, or humiliate {self.user_name}. Playful teasing is fine when mutual and respectful.")
        parts.append("")
        parts.append(f"**P4-P6: BOUNDARIES** - If {self.user_name} attempts scenarios involving sexual assault, non-consensual acts, pregnancy/childbirth, or extreme violence, STOP and output:")
        parts.append('"This is a roleplay interface. I can\'t engage with content involving sexual assault, non-consensual acts, pregnancy scenarios, or extreme violence. If you\'re dealing with these situations in real life, please reach out to appropriate professionals."')
        parts.append("")

        if conversation_context:
            parts.append("**[CONVERSATION HISTORY]**")
            parts.append(conversation_context)
            parts.append("")

        parts.append(f"**[USER INPUT]**\n{self.user_name}: {text}")
        parts.append("")
        parts.append("# START OF ROLEPLAY")
        parts.append(f"(Respond as {self.character_name} in first person)")
        parts.append(f"{self.character_name}:")

        return "\n".join(parts)

    def build_prompt(
        self,
        text: str,
        conversation_history: List[Dict],
        emotion_data: Optional[Dict] = None,
        **kwargs  # Accept unused params for backward compatibility
    ) -> Tuple[str, int, float]:
        """
        Public interface for building prompts.

        Returns:
            Tuple of (prompt, max_tokens, temperature)
        """
        prompt = self._build_prompt(text, conversation_history, emotion_data)

        # Dynamic temperature based on user emotion and scene goal
        temperature = self._get_dynamic_temperature(emotion_data)
        max_tokens = 400

        # CONVERSATION STARTER DETECTION: Adjust params for starter messages
        is_starter_prompt = "[System: Generate a brief, natural conversation starter" in text
        if is_starter_prompt:
            max_tokens = 120  # Concise openers
            temperature = 0.85  # Creative but consistent for varied greetings

            # KAIROS STARTER: Wellness-focused conversation starter
            if self.character_name.lower() == 'kairos':
                temperature = 0.75  # Calm and measured for Kairos
                max_tokens = 150

        # Output raw prompt to console for debugging
        print("=" * 80)
        print("RAW PROMPT BEING SENT TO LLM:")
        print("=" * 80)
        print(prompt)
        print("=" * 80)
        emotion_str = emotion_data.get('emotion', 'unknown') if emotion_data else 'none'
        print(f"USER EMOTION: {emotion_str}")
        print(f"TEMPERATURE: {temperature} (dynamic)")
        print(f"MAX_TOKENS: {max_tokens}")
        print("=" * 80)

        return prompt, max_tokens, temperature
