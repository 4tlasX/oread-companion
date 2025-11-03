# Frequently Asked Questions

Quick answers to common questions about Oread, AI basics, and getting the most out of your companion.

---

## Table of Contents

### Understanding AI Basics
- [How does AI actually work?](#how-does-ai-actually-work)
- [What's an LLM?](#whats-an-llm)
- [Can AI really understand me?](#can-ai-really-understand-me)
- [Why does AI make stuff up sometimes?](#why-does-ai-make-stuff-up-sometimes)

### Memory & Features
- [How does memory work?](#how-does-memory-work)
- [Should I turn memory on?](#should-i-turn-memory-on)
- [How do I clear or update memory?](#how-do-i-clear-or-update-memory)
- [What about web search?](#what-about-web-search)
- [What gets sent to Brave if I use search?](#what-gets-sent-to-brave-if-i-use-search)

### Getting Started
- [Where do I find AI models?](#where-do-i-find-ai-models)
- [What kind of model should I use?](#what-kind-of-model-should-i-use)
- [How do I create a character?](#how-do-i-create-a-character)
- [How do I backup my stuff?](#how-do-i-backup-my-stuff)

### When Things Go Wrong
- [Oread won't start](#oread-wont-start)
- [Everything is super slow](#everything-is-super-slow)
- [I got an encryption error](#i-got-an-encryption-error)
- [Web search doesn't work](#web-search-doesnt-work)

### Contributing
- [How can I help?](#how-can-i-help)
- [Where do I report bugs?](#where-do-i-report-bugs)

---

## Understanding AI Basics

### How does AI actually work?

Think of it like really advanced autocomplete.

Your phone suggests the next word when you're texting based on common patterns. AI does the same thing, but for entire conversations. It was trained on millions of text examples and learned patterns like:
- "Hello" often gets "how are you?"
- Sad messages use words like "sorry" and "unfortunately"
- Questions usually end with "?"

When you message your AI companion, it:
1. Reads your message
2. Finds similar patterns from its training
3. Predicts what words would fit
4. Strings them together into a response

**The important part:** There's no thinking happening. No understanding. No consciousness. It's pattern recognition and prediction—very sophisticated, but not sentient.

---

### What's an LLM?

**Large Language Model** - basically the AI brain that runs your companion.

"Large" means it has billions of parameters (mathematical values that encode all those text patterns). More parameters usually means better quality, but also slower and needs more RAM.

Common sizes:
- **7-8B** (7-8 billion parameters) - Fast, runs on most computers
- **12-13B** - Good balance of quality and speed
- **70B+** - Very sophisticated but needs powerful hardware

---

### Can AI really understand me?

No. And that's important to remember.

AI predicts likely responses based on patterns. When it seems to "get" you, that's because:
- You used common phrasing that matches its training
- The conversation history gave it context
- The character profile guided its responses

It's like a very sophisticated parrot—can repeat phrases that sound relevant, but has no idea what they mean.

**Why this matters:** Knowing AI lacks real understanding helps you maintain healthy boundaries. You're interacting with a text prediction algorithm, not a conscious being.

---

### Why does AI make stuff up sometimes?

AI "hallucinates" when it confidently states false information.

**Examples:**
- "The Eiffel Tower was built in 1987" (nope, 1889)
- "I remember when you told me about your pet dragon" (you didn't)
- "Studies show eating rocks improves memory" (please don't)

**Why it happens:** AI generates text by predicting likely next words. Sometimes "plausible-sounding lies" score higher than "accurate truths" in its pattern matching. It has no fact-checking mechanism—just pattern recall.

**How to minimize it:**
- Enable web search (AI can look up current info)
- Don't trust it for important facts
- Verify anything critical yourself

**Never rely on AI for medical, legal, financial, or other critical decisions.**

---

## Memory & Features

### How does memory work?

Oread has two types:

**Short-term (always on):**
- Last 20 messages in your current chat
- Stored in RAM, cleared when you refresh
- Gives the AI context for current conversation

**Long-term (optional - ChromaDB):**
- Searches through ALL your past conversations
- Finds relevant topics from weeks/months ago
- Stored on disk, persists between sessions

**Example:** You mention Paris in week 1. In week 4 you say "I'm planning a France trip." With memory enabled, the AI recalls "Oh, you visited Paris before!"

---

### Should I turn memory on?

**Turn it ON if:**
- You want conversations that build on previous chats
- You discuss ongoing projects or relationships
- You have 16GB+ RAM
- You don't mind a slight performance hit (~200-500ms per message)

**Keep it OFF if:**
- Your computer is slower
- You prefer each chat to feel fresh
- You want maximum speed
- Privacy is paramount (memory database stored on disk)

Try it both ways and see what you prefer. It's off by default.

---

### How do I clear or update memory?

Sometimes you need to clear memory, especially if:
- The AI is recalling outdated or incorrect information
- You want to start fresh without past context influencing responses
- You've made character changes and want them fully reflected
- The AI seems "stuck" on old conversation patterns

**To completely clear the memory database:**

1. **Stop all Oread services** (close the inference, backend, and frontend processes)

2. **Delete the ChromaDB folder:**
   ```bash
   rm -rf inference/chroma_db/
   ```
   This removes all stored long-term memories.

3. **Restart Oread**
   The memory database will automatically rebuild as you have new conversations.

**What gets cleared:**
- All past conversation memories
- Semantic search history
- Long-term context stored on disk

**What stays:**
- Short-term memory (last 20 messages) - this refreshes each session anyway
- Your character profiles
- Your settings and preferences
- Conversation history in browser (until you refresh)

**When to clear memory:**
- You notice the AI referencing outdated info consistently
- After making significant character personality changes
- The AI "remembers" something incorrectly and won't let it go
- You want a clean slate for privacy reasons

**Important:** Memory clears won't fix issues with the current conversation session. If you need to reset the current chat context, refresh your browser. Memory clearing only affects the long-term ChromaDB storage.

---

### What about web search?

When enabled, Oread can search the web to get current information.

**How it works:**
1. You ask something like "What's happening with AI lately?"
2. Oread extracts keywords: "AI news"
3. Searches Brave, gets top results
4. AI sees those results and can reference real info

**Good for:**
- Current events and news
- Fact-checking
- "What's the latest..." questions

**Keep it off for:**
- Pure roleplay/creative writing
- Maximum privacy (search queries go to Brave)
- Faster responses (search adds 1-2 seconds)

It's off by default. You need a Brave API key to enable it (free tier: 2000 searches/month).

---

### What gets sent to Brave if I use search?

**What Brave receives:**
- Keywords from your message ("protests last night" from "Did you hear about the protests last night?")
- Your API key
- Timestamp

**What Brave does NOT get:**
- Your character's name
- Full conversation history
- Your profile info
- Previous messages

If privacy is important, keep web search disabled. That's why it's off by default.

---

## Getting Started

### Where do I find AI models?

**Hugging Face** is your main source: https://huggingface.co/models?library=gguf

Search for "GGUF" format models. These are optimized to run on regular computers.

**Look for "quantized" versions:**
- Q4_K_M = good balance (smaller file, decent quality)
- Q5_K_M = better quality, larger file
- Q8_0 = near-original quality, much larger

**Download:** Click the GGUF file → Download → Save to your `models/` folder in Oread.

**Note:** Some models are several GB. Make sure you have space and a stable internet connection.

---

### What kind of model should I use?

**It depends on your computer and what you want.**

**For roleplay/creative companions:**
- Models trained for chat/instruct work well
- Look for "chat," "instruct," or names mentioning roleplay
- Examples: MN-Violet-Lotus-12B, Nous-Hermes, Mistral-Instruct

**For factual/assistant tasks:**
- Models trained for reasoning and accuracy
- Examples: Llama-3-Instruct, Gemma-2

**For lower-end computers (8-16GB RAM):**
- 7-8B models
- Q4_K_M quantization
- Examples: Mistral-7B, Phi-3-Mini

**For better quality (16GB+ RAM, ideally GPU):**
- 12-13B models
- Q4_K_M or Q5_K_M quantization

**The model you choose matters.** Different models have different personalities, capabilities, and "vibes." Experiment to find what you like. Some are more creative, some more factual, some friendlier, some more formal.

**Important:** Research any model before using it. Some are specifically trained to be uncensored (no content filters). That's your choice, but understand what you're downloading.

---

### How do I create a character?

1. **Go to Settings** (gear icon in chat)
2. **Click "➕ New"** to create a profile
3. **Fill in the character details:**

**Basic Information:**
- **Name** - What you'll call them
- **Species** - Human, fantasy, AI, whatever fits your story
- **Gender** - Their pronouns and identity
- **Age** - How old they are
- **Companion Type** - Friend, partner, mentor, etc.

**Important Note on User Profiles:**
For the best roleplay experience, fill out your user profile in Settings. The more details you provide about yourself, the more personalized and engaging your AI companion's responses will be. This helps the AI understand your context and tailor conversations to you specifically.

**Appearance & Presence:**
- **Appearance** - Physical description
- **Avatar** - Upload a picture (optional)

**Background & Context:**
- **Role/Career** - What they do, their profession
- **Personal Interests/Domains of Expertise** - What they know and care about
- **Backstory** - Their history and experiences

**Communication Preferences:**
- **Communication Boundaries** - Topics or approaches they avoid
- **Words/Phrases to Avoid** - Specific language they won't use

**Personality & Behavior:**
- **Personality Traits** - Select 3-7 traits across 8 categories:
  - Emotional Expression (Warm, Reserved, Passionate, Stoic, etc.)
  - Social Energy (Extroverted, Introverted, Supportive, etc.)
  - Thinking Style (Analytical, Creative, Philosophical, Practical, etc.)
  - Humor & Edge (Witty, Sarcastic, Playful, Brooding, etc.)
  - Core Values (Honest, Courageous, Justice-Oriented, Authentic, etc.)
  - How They Care (Kind, Empathetic, Protective, Nurturing, etc.)
  - Energy & Presence (Confident, Gentle, Intense, Easygoing, etc.)
  - Lifestyle & Interests (Outdoorsy, Intellectual, Contemplative, Social, etc.)
- **Additional Custom Traits** - Add anything not covered by the tags

**Relationship Dynamics:**
- **Romantic or Platonic** - Choose your relationship type
- **If Romantic:** Control physical intimacy level, pacing, scene detail, and who initiates
- **If Platonic:** Choose friendship style and physical comfort boundaries

4. **Save** and **Set Active**

**Design Philosophy:**

Oread's character system is built to be **inclusive and respectful** of all identities, orientations, and relationship types. Whether you want a platonic friend, a romantic partner, a mentor, or a creative collaborator—the system supports your vision without assumptions.

⚠️ **Note:** The personality trait system is still being tested and refined. Tags work, but their effectiveness varies depending on the model you're using. We're continuously improving how traits translate into consistent behavior.

**About Roleplay & Fictional References:**

When engaging in roleplay, your AI companion may reference or create fictional characters, scenarios, or worlds as part of the creative storytelling experience. This is expected behavior—roleplay is collaborative fiction-building. The AI might:
- Reference fictional characters from popular media
- Create entirely new fictional characters for your story
- Build imaginary scenarios and settings
- Take on different personas within the roleplay

This is all part of the creative experience and is completely normal. Remember: roleplay is fiction, and both you and the AI are co-creating an imaginary narrative together.

---

### How do I backup my stuff?

**Easy way:**
1. Settings → "Backup Data" section
2. Click "Download Backup"
3. Save the JSON file somewhere safe

**What's included:**
- All characters
- Your settings
- Profile info

**What's NOT included:**
- Conversation history (not saved by default)
- Memory database (separate folder)

**Do this regularly.** If something breaks, you'll be glad you did.

**Advanced:** You can also manually copy these folders:
- `data/profiles/` - Your characters
- `data/favorites/` - Favorite messages
- `inference/chroma_db/` - Memory database

---

## When Things Go Wrong

### Oread won't start

**Check the basics:**

1. **Are the services running?**
   ```bash
   # Should return something
   curl http://localhost:9000
   curl http://localhost:9001/health
   ```

2. **Port conflict?**
   ```bash
   # See what's using the ports
   lsof -i :9000
   lsof -i :9001
   ```
   If something else is there, either stop it or change Oread's ports in the `.env` files.

3. **Dependencies installed?**
   ```bash
   cd backend && npm install
   cd frontend && npm install
   cd inference && pip install -r requirements.txt
   ```

4. **Do you have a model?**
   ```bash
   ls models/
   # Should see your GGUF file
   ```

**Still stuck?** Check the terminal output for error messages. Those usually tell you what's wrong.

---

### Everything is super slow

**This is often normal.** AI inference is computationally expensive.

**What affects speed:**

1. **Model size** - Bigger = slower
   - 7B model: 10-30 words/second
   - 12B model: 5-15 words/second
   - 70B model: 1-3 words/second

2. **Your hardware:**
   - GPU: 10-20x faster than CPU
   - Apple Silicon (M1/M2/M3): Very fast with Metal
   - Older CPU: Much slower

3. **Features enabled:**
   - Memory adds ~200-500ms
   - Web search adds ~1-2 seconds
   - More conversation history = slower

**Speed it up:**
- Use a smaller model (7B instead of 12B)
- Turn off memory and web search
- Enable GPU in `inference/.env`: `LLM_N_GPU_LAYERS=-1`
- Use Q4_K_M instead of larger quantizations
- Use an SSD (not HDD) for faster model loading

---

### I got an encryption error

**"Failed to decrypt profile"**

This usually means wrong password or corrupted file.

**Try:**
1. Make sure you're using the right password
2. If you just changed passwords, there might have been a re-encryption issue
3. Restore from backup (Settings → Download Backup)
4. If no backup... the file might be unrecoverable

**Prevention:**
- Export backups regularly
- Use a strong, memorable password
- Don't force-quit during password changes

---

### Web search doesn't work

**Checklist:**

1. **Is it enabled?**
   - Settings → "Enable Web Search" ON
   - API key entered in "Web Search API Key"

2. **Is your query actually triggering search?**
   - Try: "What's the latest news about AI?"
   - Check inference logs for "Performing web search"
   - Not all messages trigger search—only relevant ones

3. **Valid API key?**
   - Log in to https://brave.com/search/api/
   - Check it's active
   - Verify you haven't hit quota (free = 2000/month)

**Still broken?** [Open an issue](https://github.com/sleddd/oread/issues) with your logs.

---

## Contributing

### How can I help?

Lots of ways!

**Report bugs:**
- Check if it's already reported: https://github.com/sleddd/oread/issues
- If not, open a new issue with details

**Suggest features:**
- Open a discussion or issue
- Explain what you want and why

**Submit code:**
- Fork the repo
- Make your changes
- Test thoroughly
- Open a pull request
- **Don't remove safety features** (license violation)

**Improve docs:**
- Fix typos
- Clarify confusing sections
- Add examples
- Documentation PRs are especially welcome!

**Share your experience:**
- Write about Oread
- Help others in discussions
- Make tutorials

---

### Where do I report bugs?

**GitHub Issues:** https://github.com/sleddd/oread/issues

**Before reporting:**
1. Search existing issues (might already exist)
2. Try to reproduce it consistently
3. Gather info:
   - OS and version
   - Hardware (CPU, RAM, GPU)
   - Model you're using
   - Steps to reproduce
   - Error messages

**Security vulnerabilities:** Don't open a public issue. Email the maintainer (see GitHub profile).

---

## Still Have Questions?

If you didn't find your answer:
1. Search GitHub Issues/Discussions
2. Open a new Discussion thread
3. Be specific about what you're trying to do

We'll keep updating this FAQ based on what people ask!