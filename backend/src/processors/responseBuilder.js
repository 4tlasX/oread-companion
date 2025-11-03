/**
 * Response builder - strategy selection for chatbot responses
 */
import { EMOTION_RESPONSES, SENTIMENT_MAP } from '../core/config.js';
export class ResponseBuilder {
    /**
     * Build LLM-generated response with metadata
     */
    buildLLMResponse(response, emotion) {
        const sentiment = SENTIMENT_MAP[emotion] || 'neutral';
        return {
            response,
            metadata: {
                strategy: 'llm',
                sentiment,
                emotion
            }
        };
    }
    /**
     * Build fallback emotion-based response
     */
    buildEmotionResponse(emotion) {
        const sentiment = SENTIMENT_MAP[emotion] || 'neutral';
        const responses = EMOTION_RESPONSES[emotion] || EMOTION_RESPONSES['neutral'];
        const response = responses[Math.floor(Math.random() * responses.length)];
        return {
            response,
            metadata: {
                strategy: 'emotion_fallback',
                sentiment,
                emotion
            }
        };
    }
    /**
     * Build default fallback response
     */
    buildFallbackResponse() {
        return {
            response: "I'm here.",
            metadata: {
                strategy: 'fallback',
                sentiment: 'neutral',
                emotion: 'neutral'
            }
        };
    }
}
//# sourceMappingURL=responseBuilder.js.map