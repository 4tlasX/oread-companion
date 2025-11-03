/**
 * In-memory rate limiter middleware
 */
import { envConfig } from '../core/env_config.js';
const rateLimitStore = new Map();
// Clean up old entries every 5 minutes
setInterval(() => {
    const now = Date.now();
    for (const [key, entry] of rateLimitStore.entries()) {
        if (entry.resetTime < now) {
            rateLimitStore.delete(key);
        }
    }
}, 5 * 60 * 1000);
export function rateLimiterMiddleware(req, res, next) {
    // Skip rate limiting for health checks and static assets
    if (req.path === '/health' || req.path.startsWith('/assets')) {
        return next();
    }
    const clientIp = req.ip || req.socket.remoteAddress || 'unknown';
    const now = Date.now();
    const minuteKey = `${clientIp}:minute`;
    const hourKey = `${clientIp}:hour`;
    // Check minute limit
    const minuteEntry = rateLimitStore.get(minuteKey);
    if (minuteEntry) {
        if (minuteEntry.resetTime > now) {
            if (minuteEntry.count >= envConfig.rateLimit.perMinute) {
                return res.status(429).json({
                    error: 'Too Many Requests',
                    message: 'Rate limit exceeded. Please try again later.'
                });
            }
            minuteEntry.count++;
        }
        else {
            rateLimitStore.set(minuteKey, { count: 1, resetTime: now + 60 * 1000 });
        }
    }
    else {
        rateLimitStore.set(minuteKey, { count: 1, resetTime: now + 60 * 1000 });
    }
    // Check hour limit
    const hourEntry = rateLimitStore.get(hourKey);
    if (hourEntry) {
        if (hourEntry.resetTime > now) {
            if (hourEntry.count >= envConfig.rateLimit.perHour) {
                return res.status(429).json({
                    error: 'Too Many Requests',
                    message: 'Hourly rate limit exceeded. Please try again later.'
                });
            }
            hourEntry.count++;
        }
        else {
            rateLimitStore.set(hourKey, { count: 1, resetTime: now + 60 * 60 * 1000 });
        }
    }
    else {
        rateLimitStore.set(hourKey, { count: 1, resetTime: now + 60 * 60 * 1000 });
    }
    next();
}
//# sourceMappingURL=rateLimiter.js.map