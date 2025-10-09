/**
 * Configuration helper for CodeChat frontend
 * 
 * This file provides an easy way to configure the API endpoint.
 * You can either:
 * 1. Modify the API_ENDPOINT value below
 * 2. Set window.CODECHAT_API_ENDPOINT before loading this script
 * 3. Set localStorage.setItem('chatApiEndpoint', 'your-endpoint')
 */

// Default API endpoint from Terraform deployment
const API_ENDPOINT = 'enter-API-gateway-endpoint-here';

// Set the global configuration if not already set
if (!window.CODECHAT_API_ENDPOINT) {
    window.CODECHAT_API_ENDPOINT = API_ENDPOINT;
}

// Helper function to update the API endpoint at runtime
window.setCodeChatApiEndpoint = function(endpoint) {
    if (!endpoint || typeof endpoint !== 'string') {
        console.error('Invalid API endpoint provided');
        return;
    }
    
    window.CODECHAT_API_ENDPOINT = endpoint;
    localStorage.setItem('chatApiEndpoint', endpoint);
    console.log('CodeChat API endpoint updated to:', endpoint);
    
    // If chat assistant is already loaded, trigger a repository reload
    if (window.chatAssistant && typeof window.chatAssistant.loadAvailableRepositories === 'function') {
        window.chatAssistant.apiEndpoint = endpoint;
        window.chatAssistant.loadAvailableRepositories();
    }
};

// Helper function to get current API endpoint
window.getCodeChatApiEndpoint = function() {
    return window.CODECHAT_API_ENDPOINT || localStorage.getItem('chatApiEndpoint') || '';
};

console.log('CodeChat API endpoint configured:', window.CODECHAT_API_ENDPOINT);