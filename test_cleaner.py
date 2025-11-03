#!/usr/bin/env python3
"""
Test script for response cleaner with the problematic example
"""
import re
import sys
sys.path.insert(0, '/Users/claudetteraynor/PycharmProjects/oread/inference/processors')

from response_cleaner import ResponseCleaner

# Create a test cleaner
cleaner = ResponseCleaner(
    character_name="Leo",
    user_name="Atlas",
    avoid_patterns=[]
)

# Test with your exact example
test_input = """(chuckles softly, gently tucking a stray lock of hair behind your ear) I doubt that's possible. You're too brilliant for that. *(EXPLAINATION: )* • Use first person to refer to yourself - "I", never third-person like "Leo" • Show confidence in Atlas's intelligence and abilities with the word choice ("brilliant") • Add a small, intimate action (tucking hair) to show physical affection naturally following enthusiasm • Maintain upbeat energy matching their positive mood"""

print("Input:")
print(test_input)
print("\n" + "="*80 + "\n")

cleaned = cleaner.clean(test_input)

print("Output:")
print(cleaned)
print("\n" + "="*80 + "\n")

# Expected output
expected = "I doubt that's possible. You're too brilliant for that."
print(f"Expected: {expected}")
print(f"Match: {cleaned == expected}")
