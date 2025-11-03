/**
 * Request/response schemas using Zod
 */
import { z } from 'zod';
// Chat request schema
export const chatRequestSchema = z.object({
    message: z.string().min(1).max(5000),
    conversationId: z.string().optional(),
});
// Chat response schema
export const chatResponseSchema = z.object({
    response: z.string(),
    emotion: z.string(),
    sentiment: z.string(),
    metadata: z.object({
        strategy: z.string(),
        sentiment: z.string(),
        emotion: z.string(),
    }),
});
// Analyze request schema
export const analyzeRequestSchema = z.object({
    text: z.string().min(1).max(5000),
});
// Profile name schema
export const profileNameSchema = z.object({
    name: z.string().min(1).max(50),
});
//# sourceMappingURL=chatSchemas.js.map