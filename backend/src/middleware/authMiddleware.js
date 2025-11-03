/**
 * Authentication Middleware
 * Protects routes by requiring valid session authentication
 */

/**
 * Require authentication middleware
 * Checks if user has a valid session
 */
export function requireAuth(req, res, next) {
    // Check if session exists and is authenticated
    if (req.session && req.session.authenticated) {
        // Session is valid, proceed to next middleware
        return next();
    }

    // No valid session - return unauthorized
    return res.status(401).json({
        error: 'Unauthorized',
        message: 'Please log in to access this resource',
        authenticated: false
    });
}

/**
 * Optional auth middleware
 * Attaches user info if authenticated, but doesn't block unauthenticated requests
 */
export function optionalAuth(req, res, next) {
    if (req.session && req.session.authenticated) {
        req.user = {
            username: req.session.username,
            platform: req.session.platform
        };
    }
    next();
}

/**
 * Redirect to login if not authenticated (for HTML pages)
 */
export function requireAuthPage(req, res, next) {
    if (req.session && req.session.authenticated) {
        return next();
    }

    // Redirect to login page
    return res.redirect('/login');
}