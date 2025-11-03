/**
 * Main Express server
 */
import express from 'express';
import session from 'express-session';
import https from 'https';
import fs from 'fs';
import cors from 'cors';
import helmet from 'helmet';
import path from 'path';
import crypto from 'crypto';
import { envConfig } from './core/env_config.js';
import { apiAuthMiddleware } from './middleware/apiAuth.js';
import { rateLimiterMiddleware } from './middleware/rateLimiter.js';
import { securityHeadersMiddleware, requestValidationMiddleware } from './middleware/security.js';
import { requireAuth, requireAuthPage } from './middleware/authMiddleware.js';
import chatRoutes from './routes/chat.js';
import analyzeRoutes from './routes/analyze.js';
import healthRoutes from './routes/health.js';
import profilesRoutes from './routes/profiles.js';
import authRoutes from './routes/auth.js';
import favoritesRoutes from './routes/favorites.js';
import { getChatbot } from './utils/dependencies.js';
const app = express();

// Generate secure session secret
const sessionSecret = crypto.randomBytes(32).toString('hex');

// SECURITY: Localhost-only access middleware
// This ensures the app can ONLY be accessed from the local machine
app.use((req, res, next) => {
    const remoteAddress = req.socket.remoteAddress;
    const isLocalhost =
        remoteAddress === '127.0.0.1' ||
        remoteAddress === '::1' ||
        remoteAddress === '::ffff:127.0.0.1' ||
        req.hostname === 'localhost';

    if (!isLocalhost) {
        console.warn(`⚠️  Blocked non-localhost access attempt from: ${remoteAddress}`);
        return res.status(403).json({
            error: 'Forbidden',
            message: 'This application only accepts connections from localhost'
        });
    }

    next();
});

// Middleware
app.use(helmet());
app.use(cors({
    origin: ['http://localhost:9000', 'http://127.0.0.1:9000'],
    credentials: true,
    methods: ['GET', 'POST', 'DELETE', 'OPTIONS'],
    maxAge: 600
}));
app.use(express.json());

// Session middleware - MUST come before routes
app.use(session({
    secret: sessionSecret,
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: false, // Set to true if using HTTPS
        httpOnly: true,
        maxAge: 24 * 60 * 60 * 1000, // 24 hours
        sameSite: 'lax'
    },
    name: 'connect.sid'
}));

app.use(securityHeadersMiddleware);
app.use(requestValidationMiddleware);
app.use(rateLimiterMiddleware);

// Health check (no auth required)
app.use(healthRoutes);

// Authentication routes (no auth required to access these)
app.use(authRoutes);

// API routes (with OLD API key authentication for backward compatibility)
// We'll update these to use session auth instead
app.use('/api', apiAuthMiddleware);
app.use('/api', chatRoutes);
app.use('/api', analyzeRoutes);
app.use('/api', profilesRoutes);
app.use('/api', favoritesRoutes);
// Serve static uploads directory (no auth required for serving images)
const uploadsPath = path.resolve(process.cwd(), '../data/uploads');
app.use('/uploads', express.static(uploadsPath));

// Serve data directory for Terms of Service and other public files
const dataPath = path.resolve(process.cwd(), '../data');
app.use('/data', express.static(dataPath));

// Serve static frontend files
const frontendPath = path.resolve(process.cwd(), '../frontend/src');
app.use('/assets', express.static(path.join(frontendPath, 'assets')));

// Login page (no auth required)
app.get('/login', (req, res) => {
    res.sendFile(path.join(frontendPath, 'login.html'));
});

// Protected routes - require authentication
app.get('/', requireAuthPage, (req, res) => {
    res.sendFile(path.join(frontendPath, 'index.html'));
});

app.get('/settings', requireAuthPage, (req, res) => {
    res.sendFile(path.join(frontendPath, 'settings.html'));
});

// Root API documentation
app.get('/api', (req, res) => {
    res.json({
        service: 'Echo Chatbot API',
        version: '1.0.0',
        endpoints: {
            'POST /api/chat': 'Send a chat message',
            'POST /api/analyze': 'Analyze emotion without response',
            'GET /api/profiles': 'List available profiles',
            'GET /api/profiles/active': 'Get active profile',
            'POST /api/profiles/active': 'Set active profile',
            'GET /health': 'Health check'
        }
    });
});

// Catch-all route for SPA - must be last
// This handles any routes that don't match the above (like /Liam, /Echo, etc.)
// and redirects them to the main app
app.get('*', requireAuthPage, (req, res) => {
    // Don't catch API routes, uploads, or data routes
    if (req.path.startsWith('/api') ||
        req.path.startsWith('/uploads') ||
        req.path.startsWith('/data') ||
        req.path.startsWith('/assets')) {
        return res.status(404).json({ error: 'Not Found' });
    }
    res.sendFile(path.join(frontendPath, 'index.html'));
});
// Error handler
app.use((err, req, res, next) => {
    console.error('Error:', err);
    res.status(err.status || 500).json({
        error: err.name || 'Internal Server Error',
        message: err.message || 'An unexpected error occurred'
    });
});
// Start server
async function startServer() {
    try {
        console.log('Initializing chatbot...');
        await getChatbot();
        const port = envConfig.server.port;
        const host = envConfig.server.host;
        // Check if SSL certificates are configured
        const sslCertPath = process.env.SSL_CERT_PATH;
        const sslKeyPath = process.env.SSL_KEY_PATH;
        if (sslCertPath && sslKeyPath) {
            try {
                const certPath = path.resolve(process.cwd(), sslCertPath);
                const keyPath = path.resolve(process.cwd(), sslKeyPath);
                // Check if certificate files exist
                if (fs.existsSync(certPath) && fs.existsSync(keyPath)) {
                    const httpsOptions = {
                        cert: fs.readFileSync(certPath),
                        key: fs.readFileSync(keyPath)
                    };
                    https.createServer(httpsOptions, app).listen(port, host, () => {
                        console.log(`
========================================
✅ Echo Chatbot Server Running (HTTPS)
========================================
Host: ${host}
Port: ${port}
URL: https://${host}:${port}

API Key: ${envConfig.api.key.substring(0, 8)}...
🔒 SSL/TLS Enabled
========================================
            `);
                    });
                    return;
                }
                else {
                    console.warn('⚠️  SSL certificate files not found, starting without SSL');
                }
            }
            catch (sslError) {
                console.warn('⚠️  Error loading SSL certificates, starting without SSL:', sslError);
            }
        }
        // Fall back to HTTP if SSL is not configured or failed
        app.listen(port, host, () => {
            console.log(`
========================================
✅ Echo Chatbot Server Running (HTTP)
========================================
Host: ${host}
Port: ${port}
URL: http://${host}:${port}

API Key: ${envConfig.api.key.substring(0, 8)}...
⚠️  SSL/TLS Disabled
========================================
      `);
        });
    }
    catch (error) {
        console.error('Failed to start server:', error);
        process.exit(1);
    }
}
startServer();
//# sourceMappingURL=server.js.map