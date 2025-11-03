/**
 * Security middleware - headers and request validation
 */
const SUSPICIOUS_PATTERNS = [
    /<script[^>]*>.*?<\/script>/gi,
    /javascript:/gi,
    /on\w+\s*=/gi,
    /<iframe/gi
];
export function securityHeadersMiddleware(req, res, next) {
    // Security headers
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('X-XSS-Protection', '1; mode=block');
    res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
    res.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' blob: data: https:; connect-src 'self' https://localhost:9000 https://127.0.0.1:9000 wss://localhost:9000 wss://127.0.0.1:9000");
    next();
}
export function requestValidationMiddleware(req, res, next) {
    // Check request size (10MB default)
    const contentLength = parseInt(req.headers['content-length'] || '0');
    if (contentLength > 10 * 1024 * 1024) {
        return res.status(413).json({
            error: 'Payload Too Large',
            message: 'Request body exceeds maximum size'
        });
    }
    // Check for suspicious patterns in body (for POST requests)
    if (req.method === 'POST' && req.body) {
        const bodyStr = JSON.stringify(req.body);
        for (const pattern of SUSPICIOUS_PATTERNS) {
            if (pattern.test(bodyStr)) {
                console.warn(`Suspicious pattern detected in request from ${req.ip}`);
                return res.status(400).json({
                    error: 'Bad Request',
                    message: 'Invalid request content'
                });
            }
        }
    }
    next();
}
//# sourceMappingURL=security.js.map