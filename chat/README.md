# Model Earth Chat Assistant

A ChatGPT-style interface for querying your codebase using RAG (Retrieval-Augmented Generation). This frontend connects to your AWS Lambda backend to provide intelligent answers about your code repositories.

## Features

- 🎨 **ChatGPT-style Interface** - Clean, modern UI that users are familiar with
- 💬 **Conversation History** - Locally stored chat history with easy navigation
- 📋 **Copy Code Snippets** - One-click copying of code blocks and messages
- 🔍 **Repository Filtering** - Query specific repositories or search across all
- 📱 **Responsive Design** - Works perfectly on desktop and mobile devices
- 🚀 **GitHub Pages Ready** - Static files ready for immediate deployment

## Quick Setup

1. **Clone or Download** these files to your GitHub repository
2. **Update API Endpoint** in `script.js`:
   ```javascript
   this.apiEndpoint = 'YOUR_AWS_LAMBDA_ENDPOINT_HERE';
   ```
3. **Enable GitHub Pages** in your repository settings
4. **Deploy** - Your chat assistant will be live!

## File Structure

```
├── index.html          # Main HTML structure
├── styles.css          # Complete styling (ChatGPT-inspired)
├── script.js           # All functionality and API integration
└── README.md           # This file
```

## Configuration

### API Integration

Replace the placeholder in `script.js`:

```javascript
// In the ChatAssistant constructor
this.apiEndpoint = 'https://your-lambda-endpoint.amazonaws.com/your-function';
```

### Repository Options

The repository dropdown is automatically populated from your Pinecone database namespaces. Your AWS Lambda should provide a `/repositories` endpoint that returns:

```json
{
    "repositories": ["modelearth/localsite", "modelearth/community", "modelearth/io"]
}
```

This should return all available Pinecone namespace names where your repository data is stored.

## API Expected Format

Your AWS Lambda function should have two endpoints:

### 1. Main Chat Endpoint (POST)
Expects:

```json
{
    "question": "User's question here",
    "repository": "pinecone-namespace-name" // null if querying all repos
}
```

And return:

```json
{
    "answer": "AI response here"
}
```

### 2. Repository List Endpoint (GET `/repositories`)
Should return:

```json
{
    "repositories": ["namespace1", "namespace2", "namespace3"]
}
```

This endpoint should return all available Pinecone namespace names where your repository data is stored.
## Features in Detail

### Conversation Management
- Conversations are automatically saved to localStorage
- Up to 50 recent conversations are kept
- Each conversation gets a title from the first message
- Easy switching between conversations

### Code Handling
- Automatic detection of code blocks (```language)
- Syntax highlighting placeholder (easily extensible)
- Copy buttons for all code snippets
- Inline code formatting

### Responsive Design
- Mobile-first approach
- Collapsible sidebar on mobile
- Touch-friendly interface
- Optimized for all screen sizes

## Customization

### Styling
All styles are in `styles.css`. Key CSS custom properties you might want to adjust:

- Colors: Update the color scheme by modifying the background colors
- Fonts: Change the font family in the body selector
- Spacing: Adjust padding and margins throughout

### Functionality
Key areas in `script.js` you might want to customize:

- `callAPI()` - Modify API call structure
- `processCodeBlocks()` - Enhance code formatting
- `addMessage()` - Customize message display
- Repository list - Update in both HTML and any validation logic

## Browser Support

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## GitHub Pages Deployment

1. Push these files to your GitHub repository
2. Go to Settings → Pages
3. Select source: "Deploy from a branch"
4. Choose "main" branch and "/ (root)" folder
5. Your site will be available at `https://yourusername.github.io/yourrepo`

## Local Development

Simply open `index.html` in your browser, or use a local server:

```bash
# Python
python -m http.server 8000

# Node.js
npx serve .

# Or any other static file server
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use this in your projects.