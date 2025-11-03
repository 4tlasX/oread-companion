/**
 * Health check endpoint
 */
import { Router } from 'express';
const router = Router();
router.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        service: 'echo-chatbot',
        version: '1.0.0'
    });
});
export default router;
//# sourceMappingURL=health.js.map