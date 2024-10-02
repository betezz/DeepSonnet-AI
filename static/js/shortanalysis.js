document.addEventListener('DOMContentLoaded', function() {
    const shortstoryForm = document.getElementById('shortstory-form');
    if (shortstoryForm) {
        shortstoryForm.addEventListener('submit', function(event) {
            event.preventDefault();
            analyzeShortStory();
        });
    }

    const storyText = document.getElementById('story_text');
    if (storyText) {
        storyText.addEventListener('input', function() {
            updateWordCharCount('story_text', 'story-word-char-counter');
        });
    }
});

function updateWordCharCount(textAreaId, counterId) {
    const text = document.getElementById(textAreaId).value;
    const wordCount = text.trim().split(/\s+/).length;
    const charCount = text.length;
    document.getElementById(counterId).textContent = `Words: ${wordCount} | Characters: ${charCount}`;
}

function analyzeShortStory() {
    let storyTitle = document.getElementById('story_title').value;
    let storyText = document.getElementById('story_text').value;
    let analysisType = document.getElementById('analysis_type').value;

    // Show the loading spinner and hide everything else
    document.getElementById('loading').style.display = 'flex';
    document.getElementById('main-content').style.display = 'none';
    document.getElementById('analysis-container').style.display = 'none';
    document.querySelector('.feature-section').style.display = 'none';
    document.getElementById('about-section').style.display = 'none';

    // Clear previous result
    document.getElementById('result').innerHTML = '';

    fetch('/analyze_shortstory', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            story_title: storyTitle,
            story_text: storyText,
            analysis_type: analysisType
        })
    })
    .then(response => response.json())
    .then(data => {
        // Hide the loading spinner
        document.getElementById('loading').style.display = 'none';

        // Show the analysis container
        document.getElementById('analysis-container').style.display = 'flex';

        // Display the submitted story on the left
        document.getElementById('displayed-story-title').innerText = storyTitle || 'Untitled';
        document.getElementById('displayed-story-text').innerText = storyText;

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

        visualizeStoryStructure();
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('main-content').style.display = 'block';
        document.getElementById('result').innerHTML = `<h3 class="text-danger">Error:</h3><p>An error occurred while analyzing the short story. Please try again.</p>`;
    });
}

function resetView() {
    document.getElementById('main-content').style.display = 'block';
    document.getElementById('analysis-container').style.display = 'none';
    document.querySelector('.feature-section').style.display = 'block';
    document.getElementById('about-section').style.display = 'block';
}

document.getElementById('back-button').addEventListener('click', function() {
    resetView();
});

function visualizeStoryStructure() {
    const storyText = document.getElementById('displayed-story-text').textContent;
    const paragraphs = storyText.split('\n\n');
    let visualization = '';

    paragraphs.forEach((paragraph, index) => {
        const wordCount = paragraph.trim().split(/\s+/).length;
        visualization += `<div class="story-paragraph" style="width: ${wordCount * 2}px;">${index + 1}</div>`;
    });

    document.getElementById('story-visualization').innerHTML = `
        <h5>Story Structure</h5>
        <div class="story-paragraphs">${visualization}</div>
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

function extractSentimentScore(result) {
    // Implement logic to extract sentiment score
    // This depends on how your backend provides the sentiment information
    return 50; // Placeholder value
}