document.getElementById('poem-form').addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent the form from submitting the traditional way

    let poemTitle = document.getElementById('poem_title').value;
    let poemText = document.getElementById('poem_text').value;
    let analysisType = document.getElementById('analysis_type').value;

    // Show the loading spinner
    document.getElementById('loading').style.display = 'block';

    // Clear previous result
    document.getElementById('result').innerHTML = '';

    // Hide the form during analysis
    document.getElementById('poem-form').style.display = 'none';

    fetch('/analyze_poem', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            poem_text: poemText,
            poem_title: poemTitle,
            analysis_type: analysisType
        })
    })
    .then(response => response.json())
    .then(data => {
        // Hide the loading spinner
        document.getElementById('loading').style.display = 'none';

        // Show the two-column layout
        document.getElementById('analysis-container').style.display = 'flex';

        // Display the submitted poem on the left
        document.getElementById('displayed-poem-title').innerText = poemTitle || 'Untitled';
        document.getElementById('displayed-poem-text').innerText = poemText;

        // Display the analysis result on the right
        if (data.result) {
            document.getElementById('result').innerHTML = `<p>${data.result}</p>`;
        } else if (data.error) {
            document.getElementById('result').innerHTML = `<h3 class="text-danger">Error:</h3><p>${data.error}</p>`;
        }

        // Add visual components based on analysis type
        if (analysisType === 'themes') {
            displayThemeCloud(data.result);
        } else if (analysisType === 'sentiment') {
            displaySentimentMeter(data.result);
        } else if (analysisType === 'style') {
            displayStyleTimeline(data.result);
        }

        visualizePoemStructure();
    })
    .catch(error => {
        // Hide the loading spinner and show error
        document.getElementById('loading').style.display = 'none';
        document.getElementById('result').innerHTML = `
            <h3 class="text-danger">Error:</h3>
            <p>Failed to analyze the poem. Error details:</p>
            <pre>${error.message}\n\nStack trace:\n${error.stack}</pre>
        `;
        console.error('Error:', error);
    });
});

// Handle the "Back" button click to return to the form
document.getElementById('back-button').addEventListener('click', function() {
    // Hide the two-column layout
    document.getElementById('analysis-container').style.display = 'none';

    // Show the form again
    document.getElementById('poem-form').style.display = 'block';

    // Clear the result content and the displayed poem (optional)
    document.getElementById('result').innerHTML = '';
    document.getElementById('displayed-poem-title').innerText = '';
    document.getElementById('displayed-poem-text').innerText = '';
});

function visualizePoemStructure() {
    const poemText = document.getElementById('displayed-poem-text').textContent;
    const lines = poemText.split('\n');
    let visualization = '';

    lines.forEach((line, index) => {
        const lineLength = line.trim().length;
        visualization += `<div class="poem-line" style="width: ${lineLength * 5}px;">${index + 1}</div>`;
    });

    document.getElementById('poem-visualization').innerHTML = `
        <h5>Poem Structure</h5>
        <div class="poem-lines">${visualization}</div>
    `;
}

function displayThemeCloud(result) {
    // Implement theme cloud visualization
    // You might want to use a library like d3.js for this
}

function displaySentimentMeter(result) {
    let sentimentBar = document.getElementById('sentiment-bar');
    if (!sentimentBar) {
        const container = document.getElementById('sentiment-container');
        if (!container) {
            console.error('Sentiment container not found');
            return;
        }
        sentimentBar = document.createElement('div');
        sentimentBar.id = 'sentiment-bar';
        container.appendChild(sentimentBar);
    }
    
    const sentimentScore = extractSentimentScore(result);
    sentimentBar.style.width = `${sentimentScore}%`;
    sentimentBar.setAttribute('aria-valuenow', sentimentScore);
}

function displayStyleTimeline(result) {
    // Implement style timeline visualization
}

// Helper function to extract sentiment score from result
function extractSentimentScore(result) {
    // Implement logic to extract sentiment score
    // This depends on how your backend provides the sentiment information
    return 50; // Placeholder value
}

// Add these functions
function fetchRandomPoem() {
    fetch('/get_random_poem')
        .then(response => response.json())
        .then(poem => {
            document.getElementById('poem-display').innerHTML = `
                <h3>${poem.title}</h3>
                <h4>by ${poem.author}</h4>
                <pre>${poem.content}</pre>
                <input type="hidden" id="poem-id" value="${poem.id}">
                <div class="rating">
                    <button onclick="submitRating(${poem.id}, 1)">1</button>
                    <button onclick="submitRating(${poem.id}, 2)">2</button>
                    <button onclick="submitRating(${poem.id}, 3)">3</button>
                    <button onclick="submitRating(${poem.id}, 4)">4</button>
                    <button onclick="submitRating(${poem.id}, 5)">5</button>
                </div>
            `;
        });
}

function submitRating(poemId, rating) {
    fetch('/submit_rating', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            poem_id: poemId,
            rating: rating
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Rating submitted successfully!');
            fetchRandomPoem();  // Get a new poem after rating
        } else {
            alert('Failed to submit rating.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while submitting the rating.');
    });
}

// Call this when the page loads
document.addEventListener('DOMContentLoaded', fetchRandomPoem);
