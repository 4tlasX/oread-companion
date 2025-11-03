"""
Dynamic Lorebook Generator V2
Generates character-specific lorebook chunks from UI tag selections
"""
from typing import Dict, List, Any, Optional
import logging
import json

from .lorebook_templates import LorebookTemplates

logger = logging.getLogger(__name__)


class LorebookGenerator:
    """
    Generate character-specific lorebooks from UI tag selections.
    Maps user-selected tags to template chunks.
    """

    def __init__(self):
        """Initialize generator with V2 template library"""
        self.templates = LorebookTemplates

    def generate_lorebook_from_tags(
        self,
        character_name: str,
        companion_type: str,
        selected_tags: Dict[str, List[str]],
        custom_chunks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete lorebook for a character from UI tag selections.

        Args:
            character_name: Name of the character
            companion_type: Type of companion ('romantic', 'friend', 'mentor', etc.)
            selected_tags: Dict of category → list of selected tags from new V3 system:
                {
                    "Emotional Expression": ["Warm", "Expressive"],
                    "Social Energy": ["Friendly", "Introverted"],
                    "Thinking Style": ["Curious", "Creative"],
                    "Humor & Edge": ["Witty", "Playful"],
                    "Core Values": ["Honest", "Loyal"],
                    "How They Care": ["Kind", "Empathetic"],
                    "Energy & Presence": ["Confident", "Easygoing"],
                    "Lifestyle & Interests": ["Intellectual", "Outdoorsy"],
                    "Intimacy Level": ["Sweet"],
                    "Romance Pacing": ["Natural"],
                    etc.
                }
            custom_chunks: Optional list of custom user-written chunks

        Returns:
            Complete lorebook dict ready to be stored in character profile
        """
        logger.info(f"Generating tag-based lorebook (V3 system)")

        # 1. Build chunk list from selected tags
        chunks = []
        tag_matched_count = 0

        # 2. For each category, get templates for selected tags
        for category, tags in selected_tags.items():
            for tag in tags:
                template = self.templates.get_template_by_ui_tag(tag, category)
                if template:
                    chunks.append({
                        "id": template["id"],
                        "category": template["category"],
                        "priority": template["priority"],
                        "tokens": template.get("tokens", 100),
                        "triggers": template.get("triggers", {}),
                        "content": template["content"],
                        "source": "tag_matched",
                        "ui_tag": template.get("ui_tag"),
                        "ui_category": category
                    })
                    tag_matched_count += 1
                else:
                    logger.warning(f"No template found for tag '{tag}' in category '{category}'")

        logger.debug(f"Matched {tag_matched_count} templates from {sum(len(tags) for tags in selected_tags.values())} tags")

        # 3. Add custom chunks (user-written)
        if custom_chunks:
            for custom_chunk in custom_chunks:
                chunks.append({
                    "id": custom_chunk.get("id", f"custom_{len(chunks)}"),
                    "category": custom_chunk.get("category", "custom"),
                    "priority": custom_chunk.get("priority", 50),
                    "tokens": custom_chunk.get("tokens", 100),
                    "triggers": custom_chunk.get("triggers", {}),
                    "content": custom_chunk["content"],
                    "source": "custom"
                })

        # 4. Calculate total tokens
        total_tokens = sum(chunk["tokens"] for chunk in chunks)

        # 5. Build complete lorebook
        lorebook = {
            "character_name": character_name,
            "companion_type": companion_type,
            "version": "3.0",  # V3 uses new personality tag system
            "generation_method": "tag_based_v3",
            "selected_tags": selected_tags,
            "total_chunks": len(chunks),
            "total_tokens": total_tokens,
            "chunks": chunks,
            "metadata": {
                "tag_matched_count": tag_matched_count,
                "custom_count": len(custom_chunks) if custom_chunks else 0,
                "total_tags_selected": sum(len(tags) for tags in selected_tags.values())
            }
        }

        logger.info(
            f"✅ Generated V3 lorebook: {len(chunks)} chunks, "
            f"~{total_tokens} tokens total ({lorebook['metadata']['total_tags_selected']} tags)"
        )

        return lorebook

    def regenerate_lorebook(
        self,
        existing_lorebook: Dict[str, Any],
        selected_tags: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Regenerate lorebook with updated tag selections.
        Preserves custom chunks from existing lorebook.

        Args:
            existing_lorebook: Current lorebook
            selected_tags: Updated tag selections

        Returns:
            New lorebook with updated chunks
        """
        # Extract custom chunks from existing lorebook
        custom_chunks = [
            chunk for chunk in existing_lorebook.get("chunks", [])
            if chunk.get("source") == "custom"
        ]

        # Regenerate with new tags
        return self.generate_lorebook_from_tags(
            character_name=existing_lorebook["character_name"],
            companion_type=existing_lorebook["companion_type"],
            selected_tags=selected_tags,
            custom_chunks=custom_chunks
        )

    def get_tag_preview(self, ui_tag: str, category: str = None) -> Optional[str]:
        """
        Get preview of a tag's associated template content.
        Useful for UI tooltip/preview.

        Args:
            ui_tag: UI tag name (e.g., "Warm", "Honest")
            category: Optional category for disambiguation

        Returns:
            First 150 chars of content, or None if not found
        """
        template = self.templates.get_template_by_ui_tag(ui_tag, category)
        if not template:
            return None

        content = template["content"]
        # Extract just the main instruction, skip the header
        lines = content.split('\n')
        main_content = '\n'.join(lines[2:]) if len(lines) > 2 else content

        if len(main_content) > 150:
            return main_content[:150] + "..."
        return main_content

    def get_available_tags(self) -> Dict[str, List[str]]:
        """
        Get all available UI tags organized by category.
        For frontend dropdown/multiselect population.

        Returns:
            Dict of category → list of tag names
        """
        # This would need to be built from the TAG_TO_TEMPLATE_ID mapping
        # For now, returning empty dict - frontend has tags hardcoded in HTML
        return {}

    def validate_tags(self, selected_tags: Dict[str, List[str]]) -> tuple[bool, List[str]]:
        """
        Validate that all selected tags exist in the template library.

        Args:
            selected_tags: Dict of category → list of tags

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        available_tags = self.templates.TAG_TO_TEMPLATE_ID.keys()

        for category, tags in selected_tags.items():
            for tag in tags:
                if tag not in available_tags and not self._check_contextual_tag(tag, category):
                    errors.append(f"Invalid tag '{tag}' in category '{category}'")

        return len(errors) == 0, errors

    def _check_contextual_tag(self, tag: str, category: str) -> bool:
        """Check if tag is valid in given context (handles ambiguous tags)"""
        if tag == "No Touch" and category == "Platonic Touch":
            return True
        if tag == "Reserved" and category == "Platonic Touch":
            return True
        if tag == "Friendly" and category == "Platonic Touch":
            return True
        if tag == "Affectionate" and category == "Platonic Touch":
            return True
        return False

    def export_lorebook_json(self, lorebook: Dict[str, Any]) -> str:
        """
        Export lorebook as formatted JSON string.

        Args:
            lorebook: Lorebook dict

        Returns:
            Formatted JSON string
        """
        return json.dumps(lorebook, indent=2)

    def import_lorebook_json(self, json_str: str) -> Dict[str, Any]:
        """
        Import lorebook from JSON string.

        Args:
            json_str: JSON string

        Returns:
            Lorebook dict
        """
        return json.loads(json_str)

    def estimate_retrieval_size(
        self,
        lorebook: Dict[str, Any],
        max_chunks: int = 7
    ) -> Dict[str, int]:
        """
        Estimate typical retrieval size.

        Args:
            lorebook: Lorebook to analyze
            max_chunks: Maximum chunks to retrieve per request

        Returns:
            Dict with estimates
        """
        chunks = lorebook.get("chunks", [])

        # Always-include chunks (universal)
        always_include = [
            c for c in chunks
            if c.get("triggers", {}).get("always_check") or c.get("source") == "universal"
        ]
        min_tokens = sum(c["tokens"] for c in always_include)

        # Sort by priority
        sorted_chunks = sorted(chunks, key=lambda x: x["priority"], reverse=True)

        # Typical: always_include + top 5 others
        typical_chunks = always_include.copy()
        others = [c for c in sorted_chunks if c not in always_include]
        typical_chunks.extend(others[:5])
        typical_tokens = sum(c["tokens"] for c in typical_chunks)

        # Max: always_include + top max_chunks others
        max_retrieval_chunks = always_include.copy()
        max_retrieval_chunks.extend(others[:max_chunks])
        max_tokens = sum(c["tokens"] for c in max_retrieval_chunks)

        return {
            "min_tokens": min_tokens,
            "typical_tokens": typical_tokens,
            "max_tokens": max_tokens,
            "always_include_count": len(always_include)
        }

    def get_lorebook_summary(self, lorebook: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get human-readable summary of lorebook for UI display.

        Args:
            lorebook: Lorebook dict

        Returns:
            Summary dict with readable stats
        """
        chunks = lorebook.get("chunks", [])

        # Category breakdown
        categories = {}
        for chunk in chunks:
            cat = chunk.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

        # Tag summary
        selected_tags = lorebook.get("selected_tags", {})
        total_tags = sum(len(tags) for tags in selected_tags.values())

        return {
            "character_name": lorebook.get("character_name"),
            "companion_type": lorebook.get("companion_type"),
            "total_chunks": len(chunks),
            "total_tokens": lorebook.get("total_tokens", 0),
            "total_tags_selected": total_tags,
            "categories": categories,
            "selected_tags": selected_tags,
            "version": lorebook.get("version", "unknown")
        }
