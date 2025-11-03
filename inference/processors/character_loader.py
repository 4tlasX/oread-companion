"""Character profile loader for inference service"""
from pathlib import Path
import logging
import json
from typing import Tuple, List, Dict, Any, Optional
from .lorebook_generator import LorebookGenerator
from .age_detector import AgeDetector

logger = logging.getLogger(__name__)
lorebook_gen = LorebookGenerator()
age_detector = AgeDetector()

def load_user_settings() -> Dict[str, Any]:
    """
    Load user settings from data/profiles/user-profile.json or user-settings.txt (legacy)
    Supports both JSON (v2.0) and TXT (legacy) formats
    """
    defaults = {
        "userName": "User",
        "userGender": "non-binary",
        "userSpecies": "human",
        "timezone": "UTC",
        "userBackstory": "",
        "userPreferences": {
            "music": [],
            "books": [],
            "movies": [],
            "hobbies": [],
            "other": ""
        },
        "majorLifeEvents": [],
        "sharedRoleplayEvents": [],
        "communicationBoundaries": ""
    }

    try:
        # Profile path relative to project root
        project_root = Path(__file__).resolve().parent.parent.parent
        profiles_dir = project_root / "data" / "profiles"
        json_path = profiles_dir / "user-profile.json"
        txt_path = profiles_dir / "user-settings.txt"

        # Try JSON format first
        if json_path.exists():
            try:
                content = json_path.read_text(encoding='utf-8')
                data = json.loads(content)

                if data.get('version') == '2.0' and data.get('type') == 'user':
                    return {
                        "userName": data['user'].get('name', defaults['userName']),
                        "userGender": data['user'].get('gender', defaults['userGender']),
                        "userSpecies": data['user'].get('species', defaults['userSpecies']),
                        "timezone": data['user'].get('timezone', defaults['timezone']),
                        "userBackstory": data['user'].get('backstory', defaults['userBackstory']),
                        "userPreferences": data['user'].get('preferences', defaults['userPreferences']),
                        "majorLifeEvents": data['user'].get('majorLifeEvents', defaults['majorLifeEvents']),
                        "sharedRoleplayEvents": data.get('sharedMemory', {}).get('roleplayEvents', defaults['sharedRoleplayEvents']),
                        "communicationBoundaries": data['user'].get('communicationBoundaries', defaults['communicationBoundaries'])
                    }
            except (json.JSONDecodeError, KeyError) as e:
                # Expected: Profile files are encrypted, can only be read by Node.js
                logger.debug(f"Could not parse user profile JSON (likely encrypted): {e}")

        # Fallback to TXT format (legacy)
        if txt_path.exists():
            content = txt_path.read_text(encoding='utf-8')
            settings = defaults.copy()

            for line in content.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if key in settings:
                        settings[key] = value

            return settings

        # Expected: User profile is encrypted or not yet created
        logger.debug(f"No user settings file found, using defaults")
        return defaults

    except Exception as e:
        logger.error(f"Error loading user settings: {e}")
        return defaults


def load_default_character_profile() -> Tuple[str, str, List[str], str, str, str, str, str, Optional[Dict], Optional[Dict]]:
    """
    Load the default character profile (used when no specific character is requested).
    Supports both JSON (v2.0) and TXT (legacy) formats.

    Returns:
        Tuple of (character_profile_string, character_name, avoid_words_list, user_name, companion_type, character_gender, character_role, character_backstory, lorebook, personality_tags)
    """
    try:
        project_root = Path(__file__).resolve().parent.parent.parent
        profiles_dir = project_root / "data" / "profiles"

        # Load user settings
        user_settings = load_user_settings()
        user_name = user_settings.get("userName", "User")

        # Load default character name - try JSON first
        character_name = None
        user_profile_json = profiles_dir / "user-profile.json"

        # Try JSON format first
        if user_profile_json.exists():
            try:
                content = user_profile_json.read_text(encoding='utf-8')
                data = json.loads(content)

                if data.get('version') == '2.0' and data.get('settings', {}).get('defaultActiveCharacter'):
                    character_name = data['settings']['defaultActiveCharacter']
                    logger.info(f"Default character loaded from JSON")
            except (json.JSONDecodeError, KeyError) as e:
                # Expected: User settings are encrypted
                logger.debug(f"Could not read default character from JSON (likely encrypted): {e}")

        if not character_name:
            # Expected: User settings are encrypted - Node.js will pass character data via API
            logger.debug(f"No default character found in settings, using fallback")
            return load_default_character(user_name)

        # Try JSON format first, then TXT (legacy)
        json_path = profiles_dir / f"{character_name}.json"
        txt_path = profiles_dir / f"{character_name}.txt"

        profile = None
        is_json = False

        # Try JSON format
        if json_path.exists():
            try:
                content = json_path.read_text(encoding='utf-8')
                data = json.loads(content)

                if data.get('version') == '2.0' and data.get('type') == 'character':
                    profile = data['character']
                    is_json = True
                    logger.info("Loaded JSON profile")
            except (json.JSONDecodeError, KeyError) as e:
                # Expected: Character profiles are encrypted, can only be read by Node.js
                logger.debug(f"Could not parse character profile JSON (likely encrypted): {e}")

        # Fallback to TXT format
        if not profile and txt_path.exists():
            content = txt_path.read_text(encoding='utf-8')
            profile = parse_profile(content)
            logger.info("Loaded TXT profile")

        if not profile:
            # Expected: Profile files are encrypted - Node.js will pass character data via API
            logger.debug(f"Character profile not found on disk (likely encrypted), using default")
            return load_default_character(user_name)

        # Extract fields
        char_name = profile.get('name', character_name)
        char_gender = profile.get('gender', 'female')
        char_role = profile.get('role', '')
        char_backstory = profile.get('backstory', '')
        avoid_words_str = profile.get('avoidWords', '')
        avoid_words = [
            word.strip().lower()
            for word in avoid_words_str.split(',')
            if word.strip()
        ]
        companion_type = profile.get('companionType', 'friend').lower()

        # CRITICAL: Validate character age (MUST be 25+)
        char_age = profile.get('age', '')
        if char_age:
            is_valid, parsed_age = age_detector.validate_character_age(str(char_age))
            if not is_valid:
                logger.warning(f"⚠️  Character '{char_name}' age '{char_age}' is below minimum (25+)")
                logger.warning(f"   Enforcing minimum age: setting to 25")
                profile['age'] = 25
            elif parsed_age and parsed_age < 25:
                logger.warning(f"⚠️  Character '{char_name}' age {parsed_age} is below minimum (25+)")
                logger.warning(f"   Enforcing minimum age: setting to 25")
                profile['age'] = 25
            else:
                logger.info(f"✅ Character age validated: {char_age} (25+)")
        else:
            logger.warning(f"⚠️  Character '{char_name}' has no age specified")
            logger.warning(f"   Setting default age: 25")
            profile['age'] = 25

        # Extract or generate lorebook (only in JSON format)
        lorebook = None
        personality_tags = None
        if is_json:
            # Check if lorebook already exists
            if 'lorebook' in data:
                lorebook = data['lorebook']
                logger.info(f"   Found existing lorebook with {len(lorebook.get('chunks', []))} chunks")
            # Generate from tagSelections if available
            elif 'tagSelections' in profile and profile['tagSelections']:
                logger.info(f"   Generating lorebook from tagSelections...")
                lorebook = lorebook_gen.generate_lorebook_from_tags(
                    character_name=char_name,
                    companion_type=companion_type,
                    selected_tags=profile['tagSelections']
                )
                logger.info(f"   ✅ Generated lorebook: {lorebook['total_chunks']} chunks, ~{lorebook['total_tokens']} tokens")

            # Extract personality tags for character-emotion interactions
            if 'tagSelections' in profile:
                personality_tags = profile['tagSelections']
                logger.info(f"   Loaded personality tags: {len(personality_tags)} categories")

        # Format character profile string
        character_string = format_character_profile(profile)

        format_type = "JSON" if is_json else "TXT"
        logger.info(f"✅ Loaded character (avoid words: {len(avoid_words)}, format: {format_type})")

        return (character_string, char_name, avoid_words, user_name, companion_type, char_gender, char_role, char_backstory, lorebook, personality_tags)

    except Exception as e:
        logger.error(f"Error loading character profile: {e}", exc_info=True)
        return load_default_character("User")


def parse_profile(content: str) -> Dict[str, str]:
    """Parse profile content into dictionary"""
    profile = {}
    for line in content.split('\n'):
        if '=' in line:
            first_equals = line.index('=')
            key = line[:first_equals].strip()
            value = line[first_equals + 1:].replace('\\n', '\n')

            if key == 'notifications':
                profile[key] = value == 'true'
            else:
                profile[key] = value

    return profile


def format_character_profile(profile: Dict[str, str]) -> str:
    """Format profile dictionary into character string"""
    companion_type = 'Platonic' if profile.get('companionType') == 'friend' else 'Romantic'

    # Start building the profile
    profile_str = f"""Character Profile: {profile.get('name', 'Unknown')}

Gender: {profile.get('gender', 'Unknown')}
Species: {profile.get('species', 'human')}
Age: {profile.get('age', 'Unknown')}
Companion Type: {companion_type}
"""

    # Add personality kernel if present (high priority)
    personality_kernel = profile.get('personalityKernel', '').strip()
    if personality_kernel:
        profile_str += f"""
**CORE PERSONALITY (CRITICAL - OVERRIDE ALL DEFAULTS):**
{personality_kernel}
"""

    # Add the rest of the profile
    profile_str += f"""
Appearance:
{profile.get('appearance', '')}

Personal Interests/Domains of Expertise:
{profile.get('interests', '')}

Backstory:
{profile.get('backstory', '')}

Communication Style:
{profile.get('communicationStyle', '')}

Affection Style:
{profile.get('affectionStyle', '')}

Communication Boundaries:
{profile.get('boundaries', '')}

Words/Phrases to Avoid:
{profile.get('avoidWords', '')}
"""

    return profile_str


def load_default_character(user_name: str = "User") -> Tuple[str, str, List[str], str, str, str, str, str, Optional[Dict], Optional[Dict]]:
    """Load default character profile"""
    default_profile = """Character Profile: Default Character

This is a default character profile. Please select a character in the profile builder.
"""
    logger.info("Loading default character")
    return (default_profile, "Default Character", [], user_name, 'friend', 'female', '', '', None, None)


def load_consent() -> Optional[Dict[str, Any]]:
    """
    Load consent status from user-profile.json

    Returns:
        Dictionary with consent data or None if not found/error
    """
    try:
        project_root = Path(__file__).resolve().parent.parent.parent
        profiles_dir = project_root / "data" / "profiles"
        json_path = profiles_dir / "user-profile.json"

        if not json_path.exists():
            logger.warning("User profile not found - consent cannot be verified")
            return None

        content = json_path.read_text(encoding='utf-8')
        data = json.loads(content)

        if 'consent' in data:
            return data['consent']
        else:
            logger.warning("No consent data found in user profile")
            return None

    except Exception as e:
        logger.error(f"Error loading consent: {e}")
        return None


def load_character_by_name(character_name: str) -> Tuple[str, str, List[str], str, str, str, str, str, Optional[Dict], Optional[Dict]]:
    """
    Load a specific character profile by name.

    Args:
        character_name: Name of the character to load

    Returns:
        Tuple of (character_profile_string, character_name, avoid_words_list, user_name, companion_type, character_gender, character_role, character_backstory, lorebook, personality_tags)
    """
    try:
        project_root = Path(__file__).resolve().parent.parent.parent
        profiles_dir = project_root / "data" / "profiles"

        # Load user settings
        user_settings = load_user_settings()
        user_name = user_settings.get("userName", "User")

        # Try JSON format first, then TXT (legacy)
        json_path = profiles_dir / f"{character_name}.json"
        txt_path = profiles_dir / f"{character_name}.txt"

        profile = None
        is_json = False

        # Try JSON format
        if json_path.exists():
            try:
                content = json_path.read_text(encoding='utf-8')
                data = json.loads(content)

                if data.get('version') == '2.0' and data.get('type') == 'character':
                    profile = data['character']
                    is_json = True
                    logger.debug(f"Loaded JSON profile")
            except (json.JSONDecodeError, KeyError) as e:
                # Expected: Character profiles are encrypted
                logger.debug(f"Could not parse character JSON (likely encrypted): {e}")

        # Fallback to TXT format
        if not profile and txt_path.exists():
            content = txt_path.read_text(encoding='utf-8')
            profile = parse_profile(content)
            logger.debug(f"Loaded TXT profile")

        if not profile:
            # Expected: Profile files are encrypted - Node.js will pass character data via API
            logger.debug(f"Character profile not found on disk, using default")
            return load_default_character_profile()

        # Extract fields
        char_name = profile.get('name', character_name)
        char_gender = profile.get('gender', 'female')
        char_role = profile.get('role', '')
        char_backstory = profile.get('backstory', '')
        avoid_words_str = profile.get('avoidWords', '')
        avoid_words = [
            word.strip().lower()
            for word in avoid_words_str.split(',')
            if word.strip()
        ]
        companion_type = profile.get('companionType', 'friend').lower()

        # CRITICAL: Validate character age (MUST be 25+)
        char_age = profile.get('age', '')
        if char_age:
            is_valid, parsed_age = age_detector.validate_character_age(str(char_age))
            if not is_valid:
                logger.warning(f"⚠️  Character '{char_name}' age '{char_age}' is below minimum (25+)")
                logger.warning(f"   Enforcing minimum age: setting to 25")
                profile['age'] = 25
            elif parsed_age and parsed_age < 25:
                logger.warning(f"⚠️  Character '{char_name}' age {parsed_age} is below minimum (25+)")
                logger.warning(f"   Enforcing minimum age: setting to 25")
                profile['age'] = 25
            else:
                logger.debug(f"✅ Character age validated: {char_age} (25+)")
        else:
            logger.warning(f"⚠️  Character '{char_name}' has no age specified")
            logger.warning(f"   Setting default age: 25")
            profile['age'] = 25

        # Extract or generate lorebook (only in JSON format)
        lorebook = None
        personality_tags = None
        if is_json:
            # Check if lorebook already exists
            if 'lorebook' in data:
                lorebook = data['lorebook']
                logger.debug(f"   Found existing lorebook with {len(lorebook.get('chunks', []))} chunks")
            # Generate from tagSelections if available
            elif 'tagSelections' in profile and profile['tagSelections']:
                logger.debug(f"   Generating lorebook from tagSelections...")
                lorebook = lorebook_gen.generate_lorebook_from_tags(
                    character_name=char_name,
                    companion_type=companion_type,
                    selected_tags=profile['tagSelections']
                )
                logger.debug(f"   ✅ Generated lorebook: {lorebook['total_chunks']} chunks, ~{lorebook['total_tokens']} tokens")

            # Extract personality tags for character-emotion interactions
            if 'tagSelections' in profile:
                personality_tags = profile['tagSelections']
                logger.debug(f"   Loaded personality tags: {len(personality_tags)} categories")

        # Format character profile string
        character_string = format_character_profile(profile)

        logger.debug(f"✅ Loaded character")

        return (character_string, char_name, avoid_words, user_name, companion_type, char_gender, char_role, char_backstory, lorebook, personality_tags)

    except Exception as e:
        logger.error(f"Error loading character {character_name}: {e}", exc_info=True)
        # Fallback to default
        return load_default_character_profile()


# Backward compatibility alias
load_active_character = load_default_character_profile


def check_consent() -> bool:
    """
    Check if user has accepted Terms of Service

    Returns:
        True if consent accepted, False otherwise
    """
    consent_data = load_consent()

    if not consent_data:
        return False

    return consent_data.get('accepted', False)