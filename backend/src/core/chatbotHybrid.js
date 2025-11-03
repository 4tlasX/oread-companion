/**
 * Hybrid chatbot orchestrator
 * Uses Python inference service for model inference
 * Handles all other logic in Node.js
 */
import { getInferenceClient } from '../clients/inferenceClient.js';
import { ResponseBuilder } from '../processors/responseBuilder.js';
import { CharacterLoader, loadUserSettings } from './characterLoader.js';
import { MAX_HISTORY } from './config.js';
const logger = console;
export class HybridChatbot {
    responseBuilder;
    conversationHistory = [];
    initialized = false;
    characterLoader;
    cachedCharacter = null;  // Cache character profile to avoid repeated loads
    constructor() {
        this.responseBuilder = new ResponseBuilder();
        this.characterLoader = new CharacterLoader();
    }
    /**
     * Initialize chatbot and check inference service
     */
    async initialize() {
        if (this.initialized)
            return;
        logger.info('Initializing hybrid chatbot...');
        // Load character profile asynchronously (only if not already loaded)
        if (!this.characterLoader.getActiveCharacter()) {
            await this.characterLoader.loadCharacterAsync();
        } else {
            logger.info('Character already loaded, skipping character load');
        }
        // Check inference service health
        const inferenceClient = getInferenceClient();
        try {
            await inferenceClient.waitForReady(5, 2000);
            inferenceClient.startHealthChecks(30000); // Check every 30s
        }
        catch (error) {
            logger.error('Failed to connect to inference service:', error);
            throw new Error('Inference service is not available. Please start it with: cd inference-service && python main.py');
        }
        this.initialized = true;
        logger.info('✅ Hybrid chatbot initialized');
    }
    /**
     * Process a message and generate response
     * @param {boolean} skipHistory - If true, don't add this message to conversation history (for system prompts)
     */
    async processMessage(userMessage, sessionId = null, userId = 'default', skipHistory = false) {
        if (!this.initialized) {
            throw new Error('Chatbot not initialized');
        }

        // CRITICAL: Sanitize history before processing to remove any old system prompts
        // This cleans up any pollution from before the skipHistory fix
        this.sanitizeHistory();

        const inferenceClient = getInferenceClient();
        try {
            // Step 1: Detect emotion using Python service
            const emotionResult = await inferenceClient.detectEmotion({
                text: userMessage
            });
            // --- CRITICAL FIX: Robust validation against missing data ---
            if (!emotionResult || typeof emotionResult.confidence !== 'number') {
                logger.error('Inference service returned invalid emotion result structure (missing confidence).', emotionResult);
                throw new Error('Inference service failed to return valid emotion data. Check Python logs for model load errors.');
            }
            // -----------------------------------------------------------
            const emotionData = {
                emotion: emotionResult.emotion,
                confidence: emotionResult.confidence,
                scores: emotionResult.scores,
                intensity: emotionResult.intensity,
                category: emotionResult.category
            };
            logger.info(`Detected emotion: ${emotionData.emotion} (${emotionData.confidence})`);

            // Step 2: Use Python's context-aware generation (with all the romantic/formatting instructions)
            // OPTIMIZATION: Use cached character profile (only load once per session)
            if (!this.cachedCharacter) {
                this.cachedCharacter = this.characterLoader.getActiveCharacter();
            }
            const character = this.cachedCharacter;

            // Load user settings for memory/search preferences
            // Use the same encryption key that was set on the characterLoader
            const userSettings = await loadUserSettings(this.characterLoader.encryptionKey);

            // Merge user settings into character profile
            const enrichedCharacter = {
                ...character,
                // Add user settings so inference has access to them
                user_name: userSettings.userName,
                user_gender: userSettings.userGender,
                user_species: userSettings.userSpecies,
                user_timezone: userSettings.timezone,
                user_backstory: userSettings.userBackstory,
                user_preferences: userSettings.userPreferences,
                user_major_life_events: userSettings.majorLifeEvents,
                shared_roleplay_events: userSettings.sharedRoleplayEvents,
                user_communication_boundaries: userSettings.communicationBoundaries
            };

            // CRITICAL FIX: Pass actual conversation history to Python
            // This enables context-aware responses and prevents repetition
            const contextRequest = {
                text: userMessage,
                emotion_data: emotionData,
                conversation_history: this.conversationHistory,  // Use real history!
                // Send FULL character object WITH user settings so Python doesn't need to load from disk
                character_profile: enrichedCharacter || null,
                enable_memory: userSettings.enableMemory,  // User preference for memory retrieval
                enable_web_search: userSettings.enableWebSearch,  // User preference for web search
                web_search_api_key: userSettings.webSearchApiKey || null  // Brave Search API key
            };

            // Log minimal context (no sensitive data)
            logger.info(`Processing message - History: ${this.conversationHistory.length} messages, Memory: ${userSettings.enableMemory ? 'enabled' : 'disabled'}`);

            const llmResult = await inferenceClient.generateWithContext(contextRequest);
            const llmResponse = llmResult.text;
            // Step 4: Update conversation history (unless skipHistory is true for system prompts)
            if (!skipHistory) {
                this.conversationHistory.push({
                    role: 'user',
                    content: userMessage
                });
            }
            let finalResponse;
            if (llmResponse && llmResponse.trim().length > 0) {
                // OPTIMIZATION: Python already cleaned the response
                // No need to clean again (saves 3-5ms per message)
                if (!skipHistory) {
                    this.conversationHistory.push({
                        role: 'assistant',
                        content: llmResponse  // Already cleaned by Python
                    });
                }
                finalResponse = this.responseBuilder.buildLLMResponse(llmResponse, emotionData.emotion);
            }
            else {
                // Fallback to emotion-based response
                const emotionResponse = this.responseBuilder.buildEmotionResponse(emotionData.emotion);
                if (!skipHistory) {
                    this.conversationHistory.push({
                        role: 'assistant',
                        content: emotionResponse.response
                    });
                }
                finalResponse = emotionResponse;
            }
            // Step 5: Trim history
            if (this.conversationHistory.length > MAX_HISTORY) {
                this.conversationHistory = this.conversationHistory.slice(-MAX_HISTORY);
            }
            // --- FIX: Use nullish coalescing (??) for safe metadata assignment ---
            // This prevents errors if any field (like tokens_generated) is undefined
            finalResponse.metadata = {
                ...finalResponse.metadata,
                emotion_confidence: emotionData.confidence ?? 0,
                emotion_scores: emotionData.scores ?? {},
                tokens_generated: llmResult.tokens_generated ?? 0,
                character: this.characterLoader.getActiveCharacterName()
            };

            // Save conversation to memory if enabled (background, non-blocking)
            if (userSettings.enableMemory) {
                inferenceClient.saveConversation({
                    user_id: userId,
                    character_name: this.characterLoader.getActiveCharacterName(),
                    user_message: userMessage,
                    character_response: finalResponse.response,
                    emotion: emotionData.emotion,
                    session_id: sessionId
                }).then(() => {
                    logger.debug(`Conversation saved to persistent memory`);
                }).catch(error => {
                    logger.warn(`Failed to save conversation to memory: ${error.message}`);
                    // Don't fail the request if memory save fails
                });
            }

            // Return immediately without waiting for memory save
            return finalResponse;
        }
        catch (error) {
            logger.error(`Error processing message: ${error.message}`);
            // Check if it's an inference service error
            if (error.message?.includes('inference service')) {
                // Re-throw the specific error message to the caller
                //throw new Error('Inference service unavailable. Please ensure Python service is running.');
            }
            return this.responseBuilder.buildFallbackResponse();
        }
    }
    /**
     * Analyze emotion without generating response
     */
    async analyzeEmotion(text) {
        if (!this.initialized) {
            throw new Error('Chatbot not initialized');
        }
        const inferenceClient = getInferenceClient();
        const result = await inferenceClient.detectEmotion({ text });
        // Safety check for analysis endpoint
        if (!result || typeof result.confidence !== 'number') {
            logger.error('Inference service returned invalid emotion result structure for analysis.', result);
            throw new Error('Inference service failed to return valid emotion data for analysis.');
        }
        return {
            emotion: result.emotion,
            confidence: result.confidence,
            scores: result.scores,
            intensity: result.intensity,
            category: result.category
        };
    }
    // NOTE: cleanResponse() method removed - Python already handles all text cleaning
    // This saves 3-5ms per message and prevents formatting bugs
    /**
     * Reload character profile and clear cache
     */
    async reloadCharacter() {
        if (!this.initialized) {
            throw new Error('Chatbot not initialized');
        }
        await this.characterLoader.loadActiveCharacter();
        // Clear cached character to force reload on next message
        this.cachedCharacter = null;
        logger.info('✅ Character reloaded and cache cleared');
    }
    /**
     * Sanitize conversation history to remove system prompts
     * Filters out any messages containing system instructions like [System: or IMPORTANT INSTRUCTIONS
     */
    sanitizeHistory() {
        const originalLength = this.conversationHistory.length;

        this.conversationHistory = this.conversationHistory.filter(msg => {
            const content = msg.content || '';
            // Remove messages that contain system prompts
            const isSystemPrompt =
                content.includes('[System:') ||
                content.includes('IMPORTANT INSTRUCTIONS') ||
                content.includes('Generate a brief, natural conversation starter') ||
                content.includes('TIME-AWARE Examples') ||
                content.includes('REQUIREMENTS:') ||
                content.length > 2000; // Remove unusually long messages (likely system prompts)

            return !isSystemPrompt;
        });

        const removedCount = originalLength - this.conversationHistory.length;
        if (removedCount > 0) {
            logger.info(`🧹 Sanitized conversation history: removed ${removedCount} system prompts`);
        }
    }

    /**
     * Clear conversation history
     */
    clearHistory() {
        const historyLength = this.conversationHistory.length;
        this.conversationHistory = [];
        logger.info(`🧹 Conversation history cleared (removed ${historyLength} messages)`);
        // Character info logged at debug level
    }
    /**
     * Get conversation history
     */
    getHistory() {
        return [...this.conversationHistory];
    }
    /**
     * Get active character name (uses cache if available)
     */
    getActiveCharacterName() {
        return this.cachedCharacter?.characterName || this.characterLoader.getActiveCharacterName();
    }
}
//# sourceMappingURL=chatbotHybrid.js.map