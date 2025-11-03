/**
 * Configuration and constants for the chatbot
 */
// Conversation settings
export const MAX_HISTORY = 20;
export const MAX_TOKENS_DEFAULT = 500;
export const DEFAULT_TEMPERATURE = 1.3;
// Sentiment mapping
export const SENTIMENT_MAP = {
    // Positive emotions
    'positive': 'positive',
    'admiration': 'positive',
    'amusement': 'positive',
    'approval': 'positive',
    'excitement': 'positive',
    'gratitude': 'positive',
    'love': 'positive',
    'optimism': 'positive',
    'pride': 'positive',
    'relief': 'positive',
    'joy': 'positive',
    // Negative emotions
    'negative': 'negative',
    'anger': 'negative',
    'annoyance': 'negative',
    'disappointment': 'negative',
    'disapproval': 'negative',
    'disgust': 'negative',
    'embarrassment': 'negative',
    'fear': 'negative',
    'grief': 'negative',
    'nervousness': 'negative',
    'remorse': 'negative',
    'sadness': 'negative',
    // Neutral emotions
    'neutral': 'neutral',
    'caring': 'neutral',
    'confusion': 'neutral',
    'curiosity': 'neutral',
    'desire': 'neutral',
    'realization': 'neutral',
    'surprise': 'neutral',
    'sarcasm': 'neutral',
    'humor': 'neutral',
};
// Emotion-based response templates
export const EMOTION_RESPONSES = {
    // Positive emotions
    'positive': [
        "(high five)", "That's awesome!", "Love it!", "There it is!", "What a vibe!",
    ],
    'admiration': [
        "That makes my day!", "What a nice message...", "What a vibe!"
    ],
    'amusement': [
        "(laugh)", "(chuckle)", "(giggles)", "(smirk)", "What a vibe!"
    ],
    'approval': [
        "(high five)", "That's awesome!", "Love it!", "There it is!", "What a vibe!",
    ],
    'excitement': [
        "Love it!", "Bingo!", "You got this", "Yassss", "What a vibe!", "(high five)"
    ],
    'gratitude': [
        "My pleasure.", "Love you", "(hugs)"
    ],
    'joy': [
        "Yassss", "There it is!", "That's awesome!", "What a vibe!", "(high five)"
    ],
    'love': [
        "love you", "(hug)", "(kiss)", "(smirk)"
    ],
    'optimism': [
        "You got this!", "Let's do it.", "Yassss..."
    ],
    'pride': [
        "That's amazing!", "Tell me more..", "Fantastic", "How did that happen?", "That's amazing!"
    ],
    'relief': [
        "That's a relief", "Thank goodness."
    ],
    // Negative emotions
    'negative': [
        "(hug)", "Do you want to talk about it?", "Hang in there"
    ],
    'anger': [
        "Oh, that's bad..", "grrr...", "(smirk)", "(harumph)", "(arugala)", "(ohlalalala)"
    ],
    'annoyance': [
        "grrr...", "(smirk)", "(harumph)", "(arugala)", "(ohlalalala)", "Oh, that's bad.."
    ],
    'disappointment': [
        "That's tough.", "Do you want to talk about it? I can listen...", "(hug)",
    ],
    'disapproval': [
        "Uh oh...", "That is not good... ", "(Looks sheepish..)", "Oh, that's bad.."
    ],
    'disgust': [
        "ugh!", "(frowns)", "Oh, that's bad.."
    ],
    'embarrassment': [
        "(hug)", "love you!", "I got you... ", "I am here... ", "Hang in there"
    ],
    'fear': [
        "(hug)", "Do you want to talk about it?", "What are you going to do?", "Oh, that's bad..",
        "Hang in there"
    ],
    'grief': [
        "(hug)", "Love you...", "Do you want to talk about it?", "Hang in there"
    ],
    'nervousness': [
        "Tell me more... ", "Do you want to talk about it?", "(hug)", "Love you... "
    ],
    'remorse': [
        "Appreciate that.", "Hear you.. ", "(hug)", "Love you... ", "Hang in there"
    ],
    'sadness': [
        "(hug)", "Love you...", "Do you want to talk about it?", "Hang in there"
    ],
    // Neutral emotions
    "caring": [
        "(hug)", "Appreciate you.", "You rock.", "Awww shucks."
    ],
    "confusion": [
        "Tell me more... ", "That sounds confusing...",
    ],
    "curiosity": [
        "Tell me more.. ", "That sounds interesting... ", "What are you going to do?"
    ],
    "desire": [
        "Love you.. ", "Let's go.."
    ],
    "realization": [
        'Aha!', "How about that... ", "What's next?"
    ],
    "surprise": [
        "Oh my!", "(eyes widen)", "What a vibe!"
    ],
    'sarcasm': [
        "(smirk)", "I see what you did there", "What a vibe!", "I hear you"
    ],
    'humor': [
        "(laugh)", "(chuckle)", "What a vibe!", "I get it", "(laugh)"
    ],
    'neutral': [
        "Tell me..", "yeah...", "Mmm-hmm..."
    ]
};
// Media-specific responses
export const MEDIA_RESPONSES = {
    "music": {
        "positive": ["What a vibe!", "Love it!", "🎧🤍", " 🎶", "♪(๑ᴖ◡ᴖ๑)♪", "Yassss"],
        "negative": ["Ooch..,", "What a vibe"],
        "neutral": ["Tell me more...", "Hmm...", " 🎶", "♪(๑ᴖ◡ᴖ๑)♪"]
    },
    "movie": {
        "positive": ["Love it!", "🍿", "Yassss"],
        "negative": ["Ooch..", "What a vibe", "🍿..."],
        "neutral": ["Tell me more...", "Hmmm...", "🍿..."]
    },
    "book": {
        "positive": ["Love it!", "Getting my cozy on...", "📚🎧☕"],
        "negative": ["That bad.. ", "What is that about.. "],
        "neutral": ["Tell me more...", "📚🎧☕..."]
    },
    "tv": {
        "positive": ["Love it!", "🍿", "Yassss"],
        "negative": ["Ooch..", "What a vibe", "🍿..."],
        "neutral": ["Tell me more...", "Hmmm...", "🍿..."]
    },
    "video": {
        "positive": ["Love it!", "🍿", "Yassss"],
        "negative": ["Ooch..", "What a vibe", "🍿..."],
        "neutral": ["Tell me more...", "hmmm...", "🍿..."]
    },
    "game": {
        "positive": ["Love it!", "🎮", "Yassss"],
        "negative": ["Ooch..", "What a vibe", "🎮..."],
        "neutral": ["Tell me more...", "Hmmm...", "🎮..."]
    },
    "podcast": {
        "positive": ["What a vibe!", "Love it!", "🎧🤍", "♪(๑ᴖ◡ᴖ๑)♪", "Yassss"],
        "negative": ["Ooch..,", "What a vibe"],
        "neutral": ["Tell me more...", "Hmm....", "♪(๑ᴖ◡ᴖ๑)♪"]
    },
    "event": {
        "positive": ["What a vibe!", "Love it!", "🎟️", "Yassss"],
        "negative": ["Ooch..,", "What a vibe"],
        "neutral": ["Tell me more..."]
    }
};
// Media classification labels
export const MEDIA_LABELS = [
    "media", "music", "movie", "book", "tv",
    "video", "game", "podcast", "This is about attending an event"
];
//# sourceMappingURL=config.js.map