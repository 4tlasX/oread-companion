/**
 * API Key authentication middleware
 * Accepts EITHER a valid API key OR a valid session
 */
import { envConfig } from '../core/env_config.js';
export function apiAuthMiddleware(req, res, next) {
    // Check if user has a valid session
    if (req.session && req.session.authenticated) {
        // Session is valid, allow access
        return next();
    }

    // No session, check for API key
    const apiKey = req.headers['x-api-key'];
    if (!apiKey || apiKey !== envConfig.api.key) {
        return res.status(401).json({
            error: 'Unauthorized',
            message: 'Invalid or missing API key or session'
        });
    }
    next();
}
//# sourceMappingURL=apiAuth.js.map