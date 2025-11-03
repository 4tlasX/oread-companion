#!/usr/bin/env python3
"""
Helper script to generate tag-based lorebooks for character profiles.

Usage:
    python inference/processors/generate_lorebook.py <character_name>

Example:
    python inference/processors/generate_lorebook.py echo
"""

import sys
import json
from pathlib import Path

# Get project root (two levels up from this file)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from inference.processors.lorebook_generator import LorebookGenerator


def interactive_tag_selection():
    """
    Interactive CLI for tag selection.
    Returns dict of category → selected tags.
    """
    generator = LorebookGenerator()
    available_tags = generator.get_available_tags()

    selected_tags = {}

    print("\n" + "="*70)
    print("TAG-BASED LOREBOOK GENERATION")
    print("="*70)
    print("\nSelect tags for each category. You can select multiple tags per category.")
    print("Leave blank to skip a category.\n")

    for category, tags in available_tags.items():
        print(f"\n📋 {category}")
        print("-" * 70)

        # Show available tags with numbers
        for i, tag in enumerate(tags, 1):
            print(f"  {i}. {tag}")

        # Get user selection
        while True:
            selection = input(f"\nSelect tags (e.g., '1,3,5' or 'all' or press Enter to skip): ").strip()

            if not selection:
                # Skip this category
                break

            if selection.lower() == 'all':
                selected_tags[category] = tags
                print(f"✓ Selected all tags: {', '.join(tags)}")
                break

            try:
                # Parse comma-separated numbers
                indices = [int(x.strip()) for x in selection.split(',')]
                selected = [tags[i-1] for i in indices if 1 <= i <= len(tags)]

                if selected:
                    selected_tags[category] = selected
                    print(f"✓ Selected: {', '.join(selected)}")
                    break
                else:
                    print("❌ Invalid selection. Try again.")
            except (ValueError, IndexError):
                print("❌ Invalid input. Please use numbers separated by commas (e.g., '1,3,5').")

    return selected_tags


def generate_lorebook_for_character(character_name: str, interactive: bool = True):
    """
    Generate and save tag-based lorebook for a character.

    Args:
        character_name: Name of the character (e.g., 'echo', 'Liam')
        interactive: If True, prompt user for tag selections
    """
    profiles_dir = project_root / "data" / "profiles"
    profile_path = profiles_dir / f"{character_name}.json"

    # Check if profile exists
    if not profile_path.exists():
        print(f"❌ Error: Character profile not found: {profile_path}")
        print(f"   Available profiles:")
        for json_file in profiles_dir.glob("*.json"):
            if json_file.stem != "user-profile":
                print(f"   - {json_file.stem}")
        return False

    # Load profile
    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading profile: {e}")
        return False

    # Validate profile structure
    if profile_data.get('type') != 'character':
        print(f"❌ Error: Invalid profile type (expected 'character', got '{profile_data.get('type')}')")
        return False

    character = profile_data.get('character', {})
    char_name = character.get('name', character_name)
    companion_type = character.get('companionType', 'friend')

    # Check if lorebook already exists
    if 'lorebook' in profile_data:
        print(f"\n⚠️  Warning: Lorebook already exists for '{char_name}'")
        existing_version = profile_data['lorebook'].get('version', 'unknown')
        print(f"   Existing version: {existing_version}")

        if existing_version == "2.0":
            print(f"   Existing tags:")
            for cat, tags in profile_data['lorebook'].get('selected_tags', {}).items():
                print(f"     • {cat}: {', '.join(tags)}")

        response = input("\n   Regenerate? (y/n): ").lower()
        if response != 'y':
            print("   Cancelled.")
            return False

    print(f"\n🚀 Generating lorebook for '{char_name}'")
    print(f"   Companion type: {companion_type}")

    # Get tag selections
    if interactive:
        selected_tags = interactive_tag_selection()

        if not selected_tags:
            print("\n❌ No tags selected. Cancelled.")
            return False

        # Save tag selections to character profile for future reference
        if 'tagSelections' not in character:
            character['tagSelections'] = {}
        character['tagSelections'] = selected_tags
        profile_data['character'] = character

    else:
        # Try to load from existing profile
        selected_tags = character.get('tagSelections', {})
        if not selected_tags:
            print(f"❌ No tag selections found in profile. Run in interactive mode.")
            return False

    # Generate lorebook
    try:
        generator = LorebookGenerator()

        # Validate tags first
        is_valid, errors = generator.validate_tags(selected_tags)
        if not is_valid:
            print(f"\n❌ Invalid tags detected:")
            for error in errors:
                print(f"   - {error}")
            return False

        lorebook = generator.generate_lorebook_from_tags(
            character_name=char_name,
            companion_type=companion_type,
            selected_tags=selected_tags
        )
    except Exception as e:
        print(f"❌ Error generating lorebook: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Add lorebook to profile
    profile_data['lorebook'] = lorebook

    # Save updated profile
    try:
        # Create backup
        backup_path = profile_path.with_suffix('.json.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2)

        # Save updated profile
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2)

        # Get summary
        summary = generator.get_lorebook_summary(lorebook)

        print(f"\n" + "="*70)
        print("✅ LOREBOOK GENERATED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📊 Summary:")
        print(f"   Character: {summary['character_name']}")
        print(f"   Companion Type: {summary['companion_type']}")
        print(f"   Total Chunks: {summary['total_chunks']}")
        print(f"   Estimated Tokens: ~{summary['total_tokens']}")
        print(f"   Tags Selected: {summary['total_tags_selected']}")
        print(f"\n📚 Category Breakdown:")

        for cat, count in sorted(summary['categories'].items()):
            print(f"     • {cat}: {count} chunks")

        print(f"\n🏷️  Selected Tags by Category:")
        for cat, tags in summary['selected_tags'].items():
            print(f"     • {cat}: {', '.join(tags)}")

        # Show retrieval estimates
        estimates = generator.estimate_retrieval_size(lorebook)
        print(f"\n⚡ Retrieval Estimates:")
        print(f"     • Minimum (always-include): ~{estimates['min_tokens']} tokens")
        print(f"     • Typical (5-7 chunks): ~{estimates['typical_tokens']} tokens")
        print(f"     • Maximum (all relevant): ~{estimates['max_tokens']} tokens")

        print(f"\n💾 Files:")
        print(f"     • Profile: {profile_path}")
        print(f"     • Backup: {backup_path}")

        print(f"\n🎉 Done! Restart the inference service to use the new lorebook.")

        return True

    except Exception as e:
        print(f"❌ Error saving profile: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python inference/processors/generate_lorebook.py <character_name> [--auto]")
        print("\nOptions:")
        print("  --auto    Use existing tag selections from profile (non-interactive)")
        print("\nExample:")
        print("  python inference/processors/generate_lorebook.py echo")
        print("  python inference/processors/generate_lorebook.py echo --auto")
        sys.exit(1)

    character_name = sys.argv[1]
    interactive = "--auto" not in sys.argv

    print(f"🚀 Tag-Based Lorebook Generator V2")
    print(f"   Character: {character_name}")
    print(f"   Mode: {'Interactive' if interactive else 'Auto (using saved tags)'}")
    print()

    success = generate_lorebook_for_character(character_name, interactive=interactive)

    if success:
        sys.exit(0)
    else:
        print("\n❌ Failed to generate lorebook.")
        sys.exit(1)


if __name__ == "__main__":
    main()
