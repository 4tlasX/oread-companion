# Contributing to Oread

Thanks for your interest in making Oread better! We welcome contributions that align with our core values: privacy, safety, transparency, and user autonomy.

---

## Quick Start

**Want to help but not sure how?**

- 🐛 **Found a bug?** [Open an issue](https://github.com/sleddd/oread/issues)
- 💡 **Have an idea?** Start a [discussion](https://github.com/sleddd/oread/discussions)
- 📖 **Fix a typo?** PRs for docs are always welcome
- 🔧 **Want to code?** Check out [good first issues](https://github.com/sleddd/oread/labels/good%20first%20issue)

---

## How to Contribute

### Reporting Bugs

**Before submitting:**
- Check if someone already reported it
- Try to reproduce it with default settings
- Make sure you're on the latest version

**When reporting:**
```markdown
**What happened:**
Clear description of the bug

**How to reproduce:**
1. Go to...
2. Click on...
3. See error

**Expected behavior:**
What you thought would happen

**System info:**
- OS: macOS 13.2
- Node: v18.16.0
- Python: 3.11.2
- Model: MN-Violet-Lotus-12B Q4_K_M

**Logs/Screenshots:**
(if helpful)
```

**⚠️ Privacy:** Don't include personal data, API keys, or conversation content in bug reports.

---

### Suggesting Features

Got an idea? We'd love to hear it!

**Good feature requests include:**
1. **What** you want to add
2. **Why** it's useful
3. **How** it might work (optional)

**Things to consider:**
- Does it maintain privacy? (local-only data)
- Does it respect safety boundaries? (keeps ethical protections)
- Is it inclusive? (works for diverse users)

---

### Contributing Code

We accept PRs for:
- Bug fixes
- Performance improvements
- Documentation updates
- New features (discuss first!)

**The process:**

1. **Fork the repo** and create a branch
   ```bash
   git checkout -b fix-profile-loading
   ```

2. **Make your changes**
   - Follow the existing code style
   - Keep commits focused and atomic
   - Test thoroughly

3. **Update docs** if needed
   - README for user-facing changes
   - Code comments for complex logic

4. **Submit a PR**
   - Use the template (see below)
   - Be patient with review process
   - Respond to feedback

**PR Template:**
```markdown
## What This Does
Brief description of your changes

## Why
What problem does this solve?

## Testing
How did you test this?

## Checklist
- [ ] Code tested and working
- [ ] Docs updated (if needed)
- [ ] No safety features removed
- [ ] Follows code style
```

---

## Development Setup

### Prerequisites
- Node.js 18+
- Python 3.10+
- A GGUF model file

### Quick Setup

```bash
# 1. Fork and clone
git clone https://github.com/YOUR-USERNAME/oread.git
cd oread

# 2. Install dependencies
cd backend && npm install
cd ../frontend && npm install
cd ../inference && pip install -r requirements.txt --break-system-packages

# 3. Set up environment
cp backend/.env.example backend/.env
cp inference/.env.example inference/.env
# Edit with your settings

# 4. Run locally
./start-oread.sh
# Or start services manually in separate terminals
```

---

## Code Style

**We're not picky, but consistency helps.**

### JavaScript
- Use `const` and `let`, not `var`
- Async/await > callbacks
- Clear variable names
- Comment the "why," not the "what"

```javascript
// Good - explains intent
// Decrypt profile with user's password to verify authentication
const profile = await decryptProfile(name, password);

// Unnecessary - obvious from code
// Get the profile
const profile = getProfile(name);
```

### Python
- Follow PEP 8 (mostly)
- Type hints for public functions
- Docstrings for complex logic

```python
def build_prompt(character: dict, history: list[dict]) -> str:
    """Build LLM prompt from character profile and conversation history.
    
    Includes safety checks, emotion context, and memory retrieval.
    """
    # Implementation...
```

---

## Safety Requirements

**This is important. Please read carefully.**

### What You Can't Do

❌ **Remove safety features** - Age verification, consent checks, crisis detection  
❌ **Bypass protections** - No jailbreaking tools or prompt injection helpers  
❌ **Add telemetry** - No tracking, analytics, or phone-home features  
❌ **Compromise privacy** - Data stays local, no cloud uploads  

### Why This Matters

We built Oread with ethical guardrails because AI companions can affect people's wellbeing. Removing these protections violates the license and defeats the purpose of responsible development.

**If you disagree with a safety feature,** open an issue to discuss it. But don't remove it and submit a PR.

### Safety-Critical Files

Extra scrutiny for changes to:
- `inference/processors/safety/` - All safety checks
- `inference/processors/prompt_builder.py` - LLM prompting
- `backend/src/routes/profiles.js` - User data handling
- `frontend/src/settings.html` - Consent management

---

## Testing

### Run Tests

```bash
# Backend (if tests exist)
cd backend && npm test

# Inference (if tests exist)
cd inference && pytest
```

### Manual Testing

Before submitting, verify:
- [ ] Chat works with a test character
- [ ] Settings save correctly
- [ ] No console errors
- [ ] Safety checks still function
- [ ] Privacy maintained (no external calls unless opt-in)

---

## Documentation

**Update docs when you:**
- Add features users will see
- Change configuration options
- Modify setup process

**Key files:**
- `README.md` - Main user guide
- `INSTALLATION.md` - Setup instructions
- `FAQ.md` - Common questions
- `SECURITY_ETHICS_SAFETY.md` - Safety documentation

---

## Commit Messages

Keep them clear and descriptive:

```bash
# Good ✓
git commit -m "Fix profile encryption for non-ASCII characters"
git commit -m "Add timezone support to conversation context"

# Not helpful ✗
git commit -m "fix bug"
git commit -m "updates"
```

---

## Community Guidelines

### Be Cool
- Assume good intentions
- Give constructive feedback
- Respect different viewpoints
- Focus on ideas, not people

### Where to Engage
- **Issues** - Bugs and feature requests
- **Discussions** - Questions and ideas
- **PRs** - Code review

### Response Times
This is a small project. Be patient with reviews—we'll get to your contribution!

---

## License

By contributing, you agree:
- Your code will be licensed under AGPL-3.0
- You retain copyright but grant usage rights
- Your changes remain open source
- You accept the safety requirements

---

## Recognition

Contributors will be acknowledged in:
- Release notes
- Future CONTRIBUTORS.md file
- Project documentation

---

## Questions?

**Not sure if your idea fits?** Open an issue to discuss first. We're friendly!

**Found a security vulnerability?** Email the maintainer privately (see GitHub profile). Don't open a public issue.

---

**Remember:** Safety and privacy are non-negotiable. Everything else is open for discussion.

Thanks for helping make Oread better for everyone! 🎉