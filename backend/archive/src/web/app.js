// This file contains the JavaScript logic for the web frontend, handling user interactions and API calls.

document.addEventListener('DOMContentLoaded', function() {
    const queryForm = document.getElementById('query-form');
    const queryInput = document.getElementById('query-input');
    const resultsContainer = document.getElementById('results-container');

    queryForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const query = queryInput.value.trim();
        if (query) {
            await fetchResults(query);
        }
    });

    async function fetchResults(query) {
        resultsContainer.innerHTML = 'Loading...';
        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            displayResults(data);
        } catch (error) {
            resultsContainer.innerHTML = 'Error fetching results: ' + error.message;
        }
    }

    function displayResults(data) {
        resultsContainer.innerHTML = '';
        if (data && data.results && data.results.length > 0) {
            data.results.forEach(result => {
                const resultElement = document.createElement('div');
                resultElement.className = 'result';
                resultElement.innerHTML = `
                    <h3>${result.title}</h3>
                    <p>${result.content}</p>
                    <small>Source: ${result.source}</small>
                `;
                resultsContainer.appendChild(resultElement);
            });
        } else {
            resultsContainer.innerHTML = 'No results found.';
        }
    }
});