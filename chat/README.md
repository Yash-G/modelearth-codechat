# CodeChat Frontend

A modern chat interface for querying your codebase using AI. This frontend connects to the AWS Lambda backend to provide intelligent answers about your code repositories.

## Quick Start

1. **Open the chat interface**: Open `index.html` in your web browser
2. **Select a repository**: Choose from the dropdown menu
3. **Start chatting**: Ask questions about your codebase!

## Configuration

### API Endpoint

The frontend is pre-configured to use the deployed API endpoint: `https://l34oleekr5.execute-api.us-east-1.amazonaws.com/prod`

If you need to change the API endpoint, you have several options:

#### Option 1: Modify config.js
Edit the `API_ENDPOINT` constant in `config.js`:
```javascript
const API_ENDPOINT = 'https://your-new-endpoint.execute-api.region.amazonaws.com/stage';
```

#### Option 2: Set via JavaScript Console
In the browser console:
```javascript
setCodeChatApiEndpoint('https://your-new-endpoint.execute-api.region.amazonaws.com/stage');
```

#### Option 3: Set before loading scripts
In your HTML, before loading the scripts:
```html
<script>
    window.CODECHAT_API_ENDPOINT = 'https://your-new-endpoint.execute-api.region.amazonaws.com/stage';
</script>
<script src="config.js"></script>
<script src="script.js"></script>
```

### Available Helper Functions

Once the page is loaded, you can use these helper functions in the browser console:

- `getCodeChatApiEndpoint()` - Get the current API endpoint
- `setCodeChatApiEndpoint(url)` - Update the API endpoint and reload repositories

## Features

- **Modern Chat Interface**: ChatGPT-style UI with conversation history
- **Repository Selection**: Query specific repositories or search across all
- **Code Highlighting**: Automatic detection and formatting of code blocks
- **Copy to Clipboard**: One-click copying of code snippets and responses
- **Responsive Design**: Works on desktop and mobile devices
- **Local Storage**: Conversation history is saved locally
- **Error Handling**: Clear error messages with retry options

## File Structure

- `index.html` - Main HTML structure
- `script.js` - Core functionality and API integration
- `styles.css` - Complete styling and responsive design
- `config.js` - API endpoint configuration
- `README.md` - This documentation

## Troubleshooting

### "API endpoint is not configured" Error
If you see this error, the API endpoint needs to be configured. See the Configuration section above.

### "Could not load repositories" Error
This usually means:
1. The API endpoint is incorrect
2. The backend is not deployed or accessible
3. Network connectivity issues

Try clicking the "Retry" button or check the browser console for more details. The API should be accessible at: https://l34oleekr5.execute-api.us-east-1.amazonaws.com/prod

### Repository dropdown is empty
If the repository dropdown only shows "All Repositories":
1. Check that the backend `/repositories` endpoint is working
2. Verify the API endpoint configuration
3. Check browser console for error messages

## Development

### Local Testing
Simply open `index.html` in a web browser. No build process required.

### Deployment
Upload all files to your web server or use GitHub Pages:
1. Push files to your repository
2. Enable GitHub Pages in repository settings
3. Your chat interface will be available at `https://yourusername.github.io/yourrepo/chat/`

## Browser Support

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)