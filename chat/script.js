class ChatAssistant {
    constructor() {
        this.apiEndpoint = window.CODECHAT_API_ENDPOINT || localStorage.getItem('chatApiEndpoint') || '';
        this.conversations = JSON.parse(localStorage.getItem('chatConversations') || '[]');
        this.currentConversationId = null;
        this.availableRepositories = [];
        this.typingIndicatorId = null;

        this.chatContainer = document.getElementById('chatContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.repoSelect = document.getElementById('repoSelect');
        this.llmSelect = document.getElementById('llmSelect');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.clearHistoryBtn = document.getElementById('clearHistoryBtn');
        this.chatHistory = document.getElementById('chatHistory');
        this.sidebar = document.getElementById('sidebar');
        this.menuToggle = document.getElementById('menuToggle');
        this.attachBtn = document.getElementById('attachBtn');
        this.charCount = document.getElementById('charCount');
        this.welcomeScreen = document.getElementById('welcomeScreen');

        this.createErrorBanner();
        this.initializeWelcomeScreen();

        this.bindEvents();
        this.loadConversations();
        this.loadAvailableRepositories();
    }

    initializeWelcomeScreen() {
        // Bind example prompt buttons
        const examplePrompts = document.querySelectorAll('.example-prompt');
        examplePrompts.forEach(prompt => {
            prompt.addEventListener('click', () => {
                const promptText = prompt.getAttribute('data-prompt');
                if (promptText && this.messageInput) {
                    this.messageInput.value = promptText;
                    this.handleInputChange();
                    this.messageInput.focus();
                }
            });
        });
    }

    bindEvents() {
        if (this.sendBtn) {
            this.sendBtn.addEventListener('click', () => this.sendMessage());
        }

        if (this.messageInput) {
            this.messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                } else if (e.key === 'Enter' && e.shiftKey) {
                    // Allow new line
                    return;
                }
            });
            this.messageInput.addEventListener('input', () => this.handleInputChange());
        }

        if (this.newChatBtn) {
            this.newChatBtn.addEventListener('click', () => this.startNewChat());
        }

        if (this.clearHistoryBtn) {
            this.clearHistoryBtn.addEventListener('click', () => this.clearAllConversations());
        }

        if (this.menuToggle) {
            this.menuToggle.addEventListener('click', () => this.toggleSidebar());
        }

        if (this.llmSelect) {
            this.llmSelect.addEventListener('change', () => this.handleLLMProviderChange());
        }

        if (this.attachBtn) {
            this.attachBtn.addEventListener('click', () => this.handleFileAttachment());
        }

        document.addEventListener('click', (e) => {
            if (
                window.innerWidth <= 768 &&
                this.sidebar &&
                this.menuToggle &&
                !this.sidebar.contains(e.target) &&
                !this.sidebarToggle.contains(e.target) &&
                this.sidebar.classList.contains('open')
            ) {
                this.sidebar.classList.remove('open');
            }
        });
    }

    createErrorBanner() {
        if (!this.mainContent) return;

        this.errorBanner = document.createElement('div');
        this.errorBanner.className = 'error-banner is-hidden';
        this.errorBanner.setAttribute('role', 'alert');

        this.errorMessageEl = document.createElement('span');
        this.errorMessageEl.className = 'error-banner__message';
        this.errorBanner.appendChild(this.errorMessageEl);

        const actionsWrapper = document.createElement('div');
        actionsWrapper.className = 'error-banner__actions';

        this.errorRetryButton = document.createElement('button');
        this.errorRetryButton.type = 'button';
        this.errorRetryButton.className = 'error-banner__retry';
        this.errorRetryButton.textContent = 'Retry';

        actionsWrapper.appendChild(this.errorRetryButton);
        this.errorBanner.appendChild(actionsWrapper);

        this.mainContent.prepend(this.errorBanner);
    }

    showError(message, { retryHandler = null } = {}) {
        if (!this.errorBanner || !this.errorMessageEl || !this.errorRetryButton) return;

        this.errorMessageEl.textContent = message;

        if (retryHandler) {
            this.errorRetryButton.onclick = retryHandler;
            this.errorRetryButton.classList.remove('is-hidden');
        } else {
            this.errorRetryButton.onclick = null;
            this.errorRetryButton.classList.add('is-hidden');
        }

        this.errorBanner.classList.remove('is-hidden');
    }

    hideError() {
        if (!this.errorBanner || !this.errorMessageEl || !this.errorRetryButton) return;

        this.errorMessageEl.textContent = '';
        this.errorRetryButton.onclick = null;
        this.errorRetryButton.classList.add('is-hidden');
        this.errorBanner.classList.add('is-hidden');
    }

    toggleSidebar() {
        if (!this.sidebar) return;
        this.sidebar.classList.toggle('open');
    }

    handleInputChange() {
        if (!this.messageInput || !this.sendBtn) return;

        const hasText = this.messageInput.value.trim().length > 0;
        this.sendBtn.disabled = !hasText;
        this.autoResizeTextarea();
        this.updateCharacterCount();
    }

    updateCharacterCount() {
        if (!this.messageInput || !this.charCount) return;
        
        const currentLength = this.messageInput.value.length;
        this.charCount.textContent = currentLength;
        
        // Change color based on character limit
        if (currentLength > 3500) {
            this.charCount.style.color = 'var(--md-error)';
        } else if (currentLength > 3000) {
            this.charCount.style.color = 'var(--md-secondary)';
        } else {
            this.charCount.style.color = 'var(--md-on-surface-variant)';
        }
    }

    handleLLMProviderChange() {
        if (!this.llmSelect) return;
        
        const selectedProvider = this.llmSelect.value;
        console.log(`LLM Provider changed to: ${selectedProvider}`);
        
        // Store the selection in localStorage
        localStorage.setItem('selectedLLMProvider', selectedProvider);
        
        // You can add provider-specific logic here
        // For now, we'll just log the change
    }

    handleFileAttachment() {
        // Placeholder for file attachment functionality
        console.log('File attachment clicked');
        // TODO: Implement file attachment modal or dialog
    }

    hideWelcomeScreen() {
        if (this.welcomeScreen) {
            this.welcomeScreen.style.display = 'none';
        }
    }

    showWelcomeScreen() {
        if (this.welcomeScreen) {
            this.welcomeScreen.style.display = 'flex';
        }
    }

    autoResizeTextarea() {
        if (!this.messageInput) return;

        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 200) + 'px';
    }

    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    startNewChat() {
        this.currentConversationId = this.generateId();
        this.clearChatDisplay();
        this.showWelcomeScreen();
        this.updateChatHistory();
        
        // Close sidebar on mobile after starting new chat
        if (window.innerWidth <= 768 && this.sidebar) {
            this.sidebar.classList.remove('open');
        }
    }

    clearChatDisplay() {
        if (!this.chatContainer) return;
        
        // Clear messages but keep the welcome screen
        const messages = this.chatContainer.querySelectorAll('.message');
        messages.forEach(message => message.remove());
        
        // Show welcome screen if no messages
        this.showWelcomeScreen();
    }

    showWelcomeMessage() {
        if (!this.chatContainer) return;

        this.chatContainer.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                        <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                        <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                    </svg>
                </div>
                <h2>Welcome to Code Chat Assistant</h2>
                <p>Hit me up with your questions about the codebase! I can help you understand code, find specific implementations, or explain how different parts work together.</p>
            </div>
        `;
    }

    async sendMessage() {
        if (!this.messageInput || !this.repoSelect) return;

        const query = this.messageInput.value.trim();
        if (!query) return;

        const selectedRepo = this.repoSelect.value;
        
        if (!this.apiEndpoint) {
            this.showError('API endpoint is not configured. Please update CODECHAT_API_ENDPOINT and try again.');
            return;
        }

        // Hide welcome screen when sending first message
        this.hideWelcomeScreen();

        this.addMessage(query, 'user');
        this.messageInput.value = '';
        this.handleInputChange();

        const conversation = this.getCurrentConversation();
        if (!conversation) {
            this.currentConversationId = this.generateId();
            this.conversations.push({
                id: this.currentConversationId,
                title: query.substring(0, 30),
                repo: selectedRepo,
                messages: [{ role: 'user', content: query }]
            });
            this.updateChatHistory();
        } else {
            conversation.messages.push({ role: 'user', content: query });
        }
        this.saveConversations();

        this.showTypingIndicator();

        try {
            const requestPayload = {
                query: query,
                conversation_id: this.currentConversationId
            };
            
            // Add repository selection if one is selected
            if (selectedRepo) {
                requestPayload.repositories = [selectedRepo];
            }
            
            // Add LLM provider selection if available
            if (this.llmSelect && this.llmSelect.value) {
                requestPayload.llm_provider = this.llmSelect.value;
            }

            const response = await fetch(`${this.apiEndpoint}/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestPayload)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
                throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
            }

            this.removeTypingIndicator();
            
            // Handle simple JSON response for now (not streaming)
            const data = await response.json();
            if (data.content) {
                this.addMessage(data.content, 'assistant');
                
                // Save the conversation
                const currentConvo = this.getCurrentConversation();
                if (currentConvo) {
                    currentConvo.messages.push({ role: 'assistant', content: data.content });
                    this.saveConversations();
                }
            } else if (data.error) {
                throw new Error(data.error);
            }

            /* TODO: Implement streaming response handling
            const assistantMessageDiv = this.addMessage('', 'assistant');
            const contentDiv = assistantMessageDiv.querySelector('.message-content');
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                buffer += decoder.decode(value, { stream: true });
                
                // Process complete JSON objects from the buffer
                let boundary;
                while ((boundary = buffer.indexOf('\n')) !== -1) {
                    const chunkStr = buffer.substring(0, boundary);
                    buffer = buffer.substring(boundary + 1);
                    
                    if (chunkStr.trim() === '') continue;

                    try {
                        const chunk = JSON.parse(chunkStr);
                        if (chunk.content) {
                            // Sanitize and append content
                            const sanitizedContent = this.sanitizeHtml(chunk.content);
                            contentDiv.innerHTML += sanitizedContent.replace(/\n/g, '<br>');
                            this.scrollToBottom();
                        }
                    } catch (e) {
                        console.error('Error parsing stream chunk:', e, 'Chunk:', chunkStr);
                    }
                }
            }

            // Save the complete assistant message
            const finalContent = contentDiv.innerHTML;
            const currentConvo = this.getCurrentConversation();
            if (currentConvo) {
                currentConvo.messages.push({ role: 'assistant', content: finalContent });
                this.saveConversations();
            }
            */

        } catch (error) {
            this.removeTypingIndicator();
            this.showError(`Error fetching response: ${error.message}`);
            console.error('Error:', error);
        }
    }

    addMessage(content, role) {
        if (!this.chatContainer) return null;

        const messageId = this.generateId();
        const messageElement = document.createElement('div');
        messageElement.className = `message message-${role}`;
        messageElement.dataset.messageId = messageId;

        if (role === 'user') {
            // User message structure
            messageElement.innerHTML = `
                <div class="message-content">
                    ${this.escapeHtml(content)}
                </div>
            `;
        } else {
            // Assistant message structure with avatar
            const processedContent = this.processCodeBlocks(content);
            messageElement.innerHTML = `
                <div class="message-avatar">AI</div>
                <div class="message-content">
                    ${processedContent}
                    ${content ? `
                        <div class="message-actions">
                            <button class="copy-btn" onclick="chatAssistant.copyMessage('${messageId}')">
                                <i class="material-icons">content_copy</i>
                                Copy
                            </button>
                        </div>
                    ` : ''}
                </div>
            `;
        }

        this.chatContainer.appendChild(messageElement);
        
        // Apply syntax highlighting to any new code blocks in this message
        if (role === 'assistant' && typeof hljs !== 'undefined') {
            const codeBlocks = messageElement.querySelectorAll('pre code');
            codeBlocks.forEach(block => {
                if (!block.classList.contains('hljs')) {
                    hljs.highlightElement(block);
                }
            });
        }
        
        this.scrollToBottom();

        return messageElement;
    }

    addLoadingMessage() {
        if (!this.chatContainer) return null;

        const loadingId = this.generateId();
        const loadingElement = document.createElement('div');
        loadingElement.className = 'message assistant';
        loadingElement.dataset.messageId = loadingId;

        loadingElement.innerHTML = `
            <div class="message-avatar">AI</div>
            <div class="message-content">
                <div class="loading">
                    <span>Thinking</span>
                    <div class="loading-dots">
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                    </div>
                </div>
            </div>
        `;

        this.chatContainer.appendChild(loadingElement);
        this.scrollToBottom();

        return loadingId;
    }

    removeLoadingMessage(loadingId) {
        const loadingElement = document.querySelector(`[data-message-id="${loadingId}"]`);
        if (loadingElement) {
            loadingElement.remove();
        }
    }

    processCodeBlocks(content) {
        // Configure marked.js for better rendering
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                highlight: function(code, lang) {
                    if (typeof hljs !== 'undefined' && lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value;
                        } catch (err) {
                            console.warn('Syntax highlighting failed:', err);
                        }
                    }
                    return code;
                },
                breaks: true,
                gfm: true
            });
            
            // Use marked.js to parse markdown
            let processedContent = marked.parse(content);
            
            // Add copy buttons to code blocks
            processedContent = this.addCopyButtonsToCodeBlocks(processedContent);
            
            return processedContent;
        }
        
        // Fallback: Simple code block detection and formatting
        const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
        const inlineCodeRegex = /`([^`]+)`/g;

        let processedContent = this.escapeHtml(content);

        // Process code blocks
        processedContent = processedContent.replace(codeBlockRegex, (match, language, code) => {
            const lang = language || 'text';
            const codeId = this.generateId();
            const highlightedCode = this.highlightCode(code, lang);
            
            return `
                <div class="code-block">
                    <div class="code-header">
                        <span class="code-language">${lang}</span>
                        <button class="code-copy-btn" onclick="chatAssistant.copyCode('${codeId}')">Copy</button>
                    </div>
                    <pre id="${codeId}"><code class="hljs language-${lang}">${highlightedCode}</code></pre>
                </div>
            `;
        });

        // Process inline code
        processedContent = processedContent.replace(inlineCodeRegex, '<code>$1</code>');

        // Convert line breaks to <br> tags
        processedContent = processedContent.replace(/\n/g, '<br>');

        return processedContent;
    }

    addCopyButtonsToCodeBlocks(htmlContent) {
        // Use DOM parsing to add copy buttons to existing pre/code blocks
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = htmlContent;
        
        const preElements = tempDiv.querySelectorAll('pre');
        preElements.forEach(pre => {
            const code = pre.querySelector('code');
            if (code) {
                const codeId = this.generateId();
                pre.id = codeId;
                
                // Determine language from class or use 'text'
                const langClass = Array.from(code.classList).find(cls => cls.startsWith('language-'));
                const lang = langClass ? langClass.replace('language-', '') : 'text';
                
                // Create header if it doesn't exist
                if (!pre.previousElementSibling || !pre.previousElementSibling.classList.contains('code-header')) {
                    const header = document.createElement('div');
                    header.className = 'code-header';
                    header.innerHTML = `
                        <span class="code-language">${lang}</span>
                        <button class="code-copy-btn" onclick="chatAssistant.copyCode('${codeId}')">Copy</button>
                    `;
                    pre.parentNode.insertBefore(header, pre);
                }
            }
        });
        
        return tempDiv.innerHTML;
    }

    highlightCode(code, language) {
        if (typeof hljs !== 'undefined' && language && hljs.getLanguage(language)) {
            try {
                return hljs.highlight(code, { language }).value;
            } catch (err) {
                console.warn('Syntax highlighting failed:', err);
            }
        }
        return this.escapeHtml(code);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    copyMessage(messageId) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"] .message-content`);
        if (messageElement) {
            const text = messageElement.textContent.replace(/Copy/g, '').trim();
            navigator.clipboard.writeText(text).then(() => {
                this.showCopyFeedback(messageElement.querySelector('.copy-btn'));
            });
        }
    }

    copyCode(codeId) {
        const codeElement = document.getElementById(codeId);
        if (codeElement) {
            const text = codeElement.textContent;
            navigator.clipboard.writeText(text).then(() => {
                // Look for the new code-copy-btn class first, then fallback to copy-btn
                const copyBtn = codeElement.parentElement.querySelector('.code-copy-btn') || 
                              codeElement.parentElement.querySelector('.copy-btn');
                this.showCopyFeedback(copyBtn);
            }).catch(err => {
                console.error('Failed to copy code:', err);
            });
        }
    }

    showCopyFeedback(button) {
        if (!button) return;
        
        const originalText = button.textContent;
        const originalClass = button.className;
        
        // Enhanced feedback for new copy button style
        if (button.classList.contains('code-copy-btn')) {
            button.textContent = 'Copied!';
            button.classList.add('copied');
            
            setTimeout(() => {
                button.textContent = originalText;
                button.classList.remove('copied');
            }, 2000);
        } else {
            // Fallback for original style
            button.innerHTML = `
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                Copied!
            `;
            setTimeout(() => {
                button.innerHTML = originalText;
            }, 2000);
        }
    }

    scrollToBottom() {
        if (!this.chatContainer) return;
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    async callAPI(message, repository) {
        // This method is now deprecated in favor of the streaming sendMessage function.
        // It is kept for potential future use or reference.
        console.warn("callAPI is deprecated and should not be used directly.");
    }

    async loadAvailableRepositories() {
        if (!this.repoSelect) return;

        this.repoSelect.disabled = true;

        if (!this.apiEndpoint) {
            console.warn('ChatAssistant: API endpoint is not configured.');
            if (!this.availableRepositories.length) {
                this.setFallbackRepositories();
                this.populateRepositorySelect();
            }
            this.showError('API endpoint is not configured. Set CODECHAT_API_ENDPOINT to enable repository loading.');
            this.repoSelect.disabled = false;
            return;
        }

        try {
            const response = await fetch(`${this.apiEndpoint}/repositories`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to load repositories: ${response.status}`);
            }

            const data = await response.json();
            const repositories = Array.isArray(data) ? data : data?.repositories || [];
            this.availableRepositories = repositories;
            console.log(`Loaded ${this.availableRepositories.length} repositories from API`);
            this.populateRepositorySelect();
            this.hideError();
        } catch (error) {
            console.error('Error loading repositories:', error);
            if (!this.availableRepositories.length) {
                this.setFallbackRepositories();
                this.populateRepositorySelect();
            }
            this.showError('Could not load repositories. Please try again.', {
                retryHandler: () => this.loadAvailableRepositories()
            });
        } finally {
            this.repoSelect.disabled = false;
        }
    }

    setFallbackRepositories() {
        this.availableRepositories = [
            "modelearth/webroot",
            "modelearth/cloud",
            "modelearth/codechat",
            "modelearth/community-forecasting",
            "modelearth/comparison",
            "modelearth/exiobase",
            "modelearth/feed",
            "modelearth/home",
            "modelearth/io",
            "modelearth/localsite",
            "modelearth/products",
            "modelearth/profile",
            "modelearth/projects",
            "modelearth/realitystream",
            "modelearth/reports",
            "modelearth/swiper",
            "modelearth/team"
        ];
    }

    populateRepositorySelect() {
        if (!this.repoSelect) return;

        const previousSelection = this.repoSelect.value;
        this.repoSelect.innerHTML = '';

        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'All Repositories';
        this.repoSelect.appendChild(defaultOption);

        const uniqueRepos = Array.from(new Set(this.availableRepositories));
        uniqueRepos.forEach((repo) => {
            const option = document.createElement('option');
            option.value = repo;
            // Display without the "ModelEarth_" prefix if present
            option.textContent = repo.replace(/^ModelEarth_/, '');
            this.repoSelect.appendChild(option);
        });

        if (previousSelection && uniqueRepos.includes(previousSelection)) {
            this.repoSelect.value = previousSelection;
        }
    }

    saveCurrentConversation() {
        if (!this.currentConversationId || !this.chatContainer) return;

        const messages = Array.from(this.chatContainer.querySelectorAll('.message')).map(msg => {
            const role = msg.classList.contains('user') ? 'user' : 'assistant';
            const content = msg.querySelector('.message-content').textContent.replace(/Copy/g, '').trim();
            return { role, content };
        });

        if (messages.length === 0) return;

        const conversation = {
            id: this.currentConversationId,
            title: messages[0]?.content.substring(0, 50) + (messages[0]?.content.length > 50 ? '...' : ''),
            messages,
            timestamp: Date.now()
        };

        const existingIndex = this.conversations.findIndex(c => c.id === this.currentConversationId);
        if (existingIndex >= 0) {
            this.conversations[existingIndex] = conversation;
        } else {
            this.conversations.unshift(conversation);
        }

        // Keep only last 50 conversations
        this.conversations = this.conversations.slice(0, 50);

        localStorage.setItem('chatConversations', JSON.stringify(this.conversations));
    }

    loadConversations() {
        this.updateChatHistory();
        if (this.conversations.length === 0) {
            this.startNewChat();
        }
    }

    updateChatHistory() {
        if (!this.chatHistory) return;

        this.chatHistory.innerHTML = '';
        
        this.conversations.forEach(conversation => {
            const chatItem = document.createElement('div');
            chatItem.className = 'chat-item';
            if (conversation.id === this.currentConversationId) {
                chatItem.classList.add('active');
            }
            chatItem.textContent = conversation.title;
            chatItem.addEventListener('click', () => this.loadConversation(conversation.id));
            this.chatHistory.appendChild(chatItem);
        });
    }

    loadConversation(conversationId) {
        const conversation = this.conversations.find(c => c.id === conversationId);
        if (!conversation) return;

        this.currentConversationId = conversationId;
        this.clearChatDisplay();

        conversation.messages.forEach(message => {
            this.addMessage(message.content, message.role);
        });

        this.updateChatHistory();
        
        // Close sidebar on mobile after loading conversation
        if (window.innerWidth <= 768 && this.sidebar) {
            this.sidebar.classList.remove('open');
        }
    }

    clearAllConversations() {
        if (confirm('Are you sure you want to clear all conversations? This action cannot be undone.')) {
            this.conversations = [];
            localStorage.removeItem('chatConversations');
            this.updateChatHistory();
            this.startNewChat();
        }
    }

    // Missing methods that were being called
    getCurrentConversation() {
        if (!this.currentConversationId) return null;
        return this.conversations.find(c => c.id === this.currentConversationId);
    }

    saveConversations() {
        localStorage.setItem('chatConversations', JSON.stringify(this.conversations));
    }

    showTypingIndicator() {
        if (!this.chatContainer) return;
        
        this.typingIndicatorId = this.addLoadingMessage();
    }

    removeTypingIndicator() {
        if (this.typingIndicatorId) {
            this.removeLoadingMessage(this.typingIndicatorId);
            this.typingIndicatorId = null;
        }
    }

    sanitizeHtml(text) {
        // Simple HTML sanitization - in production, use a proper library like DOMPurify
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the chat assistant when the page loads
let chatAssistant;
document.addEventListener('DOMContentLoaded', () => {
    // Initialize highlight.js if available
    if (typeof hljs !== 'undefined') {
        hljs.configure({
            languages: ['javascript', 'python', 'java', 'cpp', 'css', 'html', 'json', 'sql', 'bash', 'typescript']
        });
        
        // Highlight any existing code blocks
        hljs.highlightAll();
    }
    
    // Initialize marked.js if available
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            breaks: true,
            gfm: true,
            sanitize: false
        });
    }
    
    chatAssistant = new ChatAssistant();
});

