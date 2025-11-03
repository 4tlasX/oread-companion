import dotenv from 'dotenv';
import { z } from 'zod';
import { resolve } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
// Load environment variables
dotenv.config();
// Environment variable schema
const envSchema = z.object({
    // Server
    HOST: z.string().default('127.0.0.1'),
    PORT: z.string().transform(Number).default('9000'),
    // SSL/TLS
    SSL_CERT_PATH: z.string().optional(),
    SSL_KEY_PATH: z.string().optional(),
    // API Auth
    API_KEY: z.string().default('dev-key-change-in-production'),
    // Rate Limiting
    RATE_LIMIT_PER_MINUTE: z.string().transform(Number).default('60'),
    RATE_LIMIT_PER_HOUR: z.string().transform(Number).default('1000'),
    // Logging
    LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
    // Model Paths (for reference only - inference service handles all model loading)
    EMOTION_MODEL_PATH: z.string().default('../models/roberta_emotions_onnx'),
    LLM_MODEL_PATH: z.string().default('../models/MN-Violet-Lotus-12B-Q4_K_M.gguf'),
    // Features
    ENABLE_WEB_SEARCH: z.string().transform(val => val === 'true').default('false'),
    ENABLE_MEMORY: z.string().transform(val => val === 'true').default('false'),
    // File Paths
    PROFILES_DIR: z.string().default('../frontend/profiles'),
    // Inference Service
    INFERENCE_SERVICE_URL: z.string().default('http://localhost:9001'),
});
// Parse and validate environment variables
const parsedEnv = envSchema.parse(process.env);
// Export configuration object
export const envConfig = {
    server: {
        host: parsedEnv.HOST,
        port: parsedEnv.PORT,
        ssl: {
            certPath: parsedEnv.SSL_CERT_PATH,
            keyPath: parsedEnv.SSL_KEY_PATH,
        },
    },
    api: {
        key: parsedEnv.API_KEY,
    },
    rateLimit: {
        perMinute: parsedEnv.RATE_LIMIT_PER_MINUTE,
        perHour: parsedEnv.RATE_LIMIT_PER_HOUR,
    },
    logging: {
        level: parsedEnv.LOG_LEVEL,
    },
    models: {
        // Model paths kept for reference only - inference service handles all model operations
        emotionModelPath: resolve(__dirname, '../../', parsedEnv.EMOTION_MODEL_PATH),
        llmModelPath: resolve(__dirname, '../../', parsedEnv.LLM_MODEL_PATH),
    },
    features: {
        enableWebSearch: parsedEnv.ENABLE_WEB_SEARCH,
        enableMemory: parsedEnv.ENABLE_MEMORY,
    },
    paths: {
        profilesDir: resolve(__dirname, '../../', parsedEnv.PROFILES_DIR),
    },
    inference: {
        baseUrl: parsedEnv.INFERENCE_SERVICE_URL,
    },
};
//# sourceMappingURL=env_config.js.map