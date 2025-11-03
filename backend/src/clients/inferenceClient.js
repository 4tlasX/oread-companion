/**
 * Client for communicating with Python Inference Service
 * Supports both HTTP and gRPC (HTTP for simplicity initially)
 */
import axios from 'axios';
import { envConfig } from '../core/env_config.js';
const logger = console;
// ===== Inference Client Class =====
export class InferenceClient {
    client;
    baseUrl;
    healthCheckInterval;
    isHealthy = false;
    constructor(baseUrl) {
        this.baseUrl = baseUrl || envConfig.inference.baseUrl || 'http://localhost:9001';
        this.client = axios.create({
            baseURL: this.baseUrl,
            timeout: 180000, // 180 seconds (3 minutes) for complex LLM inference with context
            headers: {
                'Content-Type': 'application/json'
            }
        });
        // Add response interceptor for better error handling
        this.client.interceptors.response.use((response) => response, (error) => {
            if (error.response) {
                logger.error(`Inference service error: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
            }
            else if (error.request) {
                logger.error('Inference service unreachable:', error.message);
            }
            else {
                logger.error('Inference client error:', error.message);
            }
            throw error;
        });
        logger.info(`InferenceClient initialized: ${this.baseUrl}`);
    }
    /**
     * Start periodic health checks
     */
    startHealthChecks(intervalMs = 30000) {
        this.healthCheckInterval = setInterval(async () => {
            try {
                await this.checkHealth();
                this.isHealthy = true;
            }
            catch (error) {
                this.isHealthy = false;
                logger.warn('Inference service health check failed');
            }
        }, intervalMs);
    }
    /**
     * Stop periodic health checks
     */
    stopHealthChecks() {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
            this.healthCheckInterval = undefined;
        }
    }
    /**
     * Check if inference service is healthy
     */
    async checkHealth() {
        try {
            const response = await this.client.get('/health');
            return response.data;
        }
        catch (error) {
            throw new Error('Inference service health check failed');
        }
    }
    /**
     * Perform LLM text generation
     */
    async generateText(request) {
        try {
            logger.info(`Requesting LLM inference (${request.prompt.length} chars)`);
            const response = await this.client.post('/infer/llm', request);
            logger.info(`LLM inference completed: ${response.data.tokens_generated} tokens`);
            return response.data;
        }
        catch (error) {
            if (error.response?.status === 500) {
                throw new Error(`LLM inference failed: ${error.response.data?.detail || 'Unknown error'}`);
            }
            throw new Error(`Failed to communicate with inference service: ${error.message}`);
        }
    }
    /**
     * Generate text with full context (uses Python's sophisticated prompt building)
     */
    async generateWithContext(request) {
        try {
            logger.info(`Requesting context-aware LLM inference (${request.text.length} chars)`);
            const response = await this.client.post('/infer/llm/context', request);
            logger.info(`LLM inference completed: ${response.data.tokens_generated} tokens`);
            return response.data;
        }
        catch (error) {
            if (error.response?.status === 500) {
                throw new Error(`LLM context inference failed: ${error.response.data?.detail || 'Unknown error'}`);
            }
            throw new Error(`Failed to communicate with inference service: ${error.message}`);
        }
    }
    /**
     * Perform emotion detection
     */
    async detectEmotion(request) {
        try {
            logger.info(`Requesting emotion inference (${request.text.length} chars)`);
            // Python service returns: {label, score, top_emotions, intensity, category}
            const response = await this.client.post('/infer/emotion', request);
            // Map Python response to our interface
            const mapped = {
                emotion: response.data.label,
                confidence: response.data.score,
                scores: response.data.top_emotions?.reduce((acc, item) => {
                    acc[item.label] = item.score;
                    return acc;
                }, {}) || {},
                intensity: response.data.intensity,
                category: response.data.category
            };
            logger.info(`Emotion detected: ${mapped.emotion} (${mapped.confidence.toFixed(2)})`);
            return mapped;
        }
        catch (error) {
            if (error.response?.status === 500) {
                throw new Error(`Emotion inference failed: ${error.response.data?.detail || 'Unknown error'}`);
            }
            throw new Error(`Failed to communicate with inference service: ${error.message}`);
        }
    }
    /**
     * Save conversation to persistent memory via MCP
     */
    async saveConversation(request) {
        try {
            const response = await this.client.post('/mcp/save_conversation', request);
            return response.data;
        }
        catch (error) {
            logger.error(`Failed to save conversation: ${error.message}`);
            throw error;
        }
    }

    /**
     * Cancel an in-flight inference request
     */
    async cancelRequest(sessionId, requestId) {
        try {
            logger.info(`Sending cancellation signal`);
            const response = await this.client.post('/cancel', {
                session_id: sessionId,
                request_id: requestId
            });
            return response.data;
        }
        catch (error) {
            logger.warn(`Failed to cancel request ${requestId}: ${error.message}`);
            throw error;
        }
    }

    /**
     * Get health status
     */
    getHealthStatus() {
        return this.isHealthy;
    }
    /**
     * Wait for inference service to become ready
     */
    async waitForReady(maxRetries = 10, retryDelayMs = 2000) {
        for (let i = 0; i < maxRetries; i++) {
            try {
                await this.checkHealth();
                logger.info('✅ Inference service is ready');
                this.isHealthy = true;
                return;
            }
            catch (error) {
                logger.warn(`Waiting for inference service... (${i + 1}/${maxRetries})`);
                await new Promise(resolve => setTimeout(resolve, retryDelayMs));
            }
        }
        throw new Error('Inference service failed to become ready');
    }
}
// ===== Singleton Instance =====
let inferenceClientInstance = null;
export function getInferenceClient() {
    if (!inferenceClientInstance) {
        inferenceClientInstance = new InferenceClient();
    }
    return inferenceClientInstance;
}
export function resetInferenceClient() {
    if (inferenceClientInstance) {
        inferenceClientInstance.stopHealthChecks();
        inferenceClientInstance = null;
    }
}
//# sourceMappingURL=inferenceClient.js.map