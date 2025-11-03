/**
 * Emotion analysis endpoint
 */
import { Router } from 'express';
import { analyzeRequestSchema } from '../schemas/chatSchemas.js';
import { getChatbot } from '../utils/dependencies.js';
import { InputSanitizer } from '../utils/sanitizer.js';
const router = Router();
router.post('/analyze', async (req, res) => {
    try {
        // Validate request
        const parseResult = analyzeRequestSchema.safeParse(req.body);
        if (!parseResult.success) {
            return res.status(400).json({
                error: 'Validation Error',
                details: parseResult.error.errors
            });
        }
        const { text } = parseResult.data;
        // Sanitize input
        const sanitizedText = InputSanitizer.sanitizeChatMessage(text);
        // Get chatbot instance
        const chatbot = await getChatbot();
        // Analyze emotion
        const emotionData = await chatbot.analyzeEmotion(sanitizedText);
        // Return analysis
        res.json({
            emotion: emotionData.emotion,
            confidence: emotionData.confidence,
            scores: emotionData.scores,
            intensity: emotionData.intensity,
            category: emotionData.category
        });
    }
    catch (error) {
        console.error('Analysis error:', error);
        res.status(500).json({
            error: 'Internal Server Error',
            message: error.message || 'An error occurred analyzing the text'
        });
    }
});
export default router;
//# sourceMappingURL=analyze.js.map