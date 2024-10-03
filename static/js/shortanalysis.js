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

    // Initialize counter on page load
    updateWordCharCount('story_text', 'story-word-char-counter');
});

function updateWordCharCount(textAreaId, counterId) {
    const text = document.getElementById(textAreaId).value;
    const wordCount = text.trim().split(/\s+/).filter(word => word.length > 0).length;
    const charCount = text.length;
    document.getElementById(counterId).textContent = `Words: ${wordCount} | Characters: ${charCount}`;
}

function analyzeShortStory() {
    let storyTitle = document.getElementById('story_title').value;
    let storyText = document.getElementById('story_text').value;
    let analysisType = document.getElementById('analysis_type').value;
    let storyFile = document.getElementById('story_file').files[0];

    // Show loading spinner and hide content
    document.getElementById('loading').style.display = 'flex';
    document.getElementById('main-content').style.display = 'none';
    document.getElementById('analysis-container').style.display = 'none';
    document.querySelector('.feature-section').style.display = 'none';
    document.getElementById('about-section').style.display = 'none';

    let formData = new FormData();
    formData.append('story_title', storyTitle);
    formData.append('story_text', storyText);
    formData.append('analysis_type', analysisType);
    if (storyFile) {
        formData.append('story_file', storyFile);
    }

    fetch('/analyze_shortstory', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Hide loading spinner
        document.getElementById('loading').style.display = 'none';

        // Show analysis container
        document.getElementById('analysis-container').style.display = 'flex';

        // Display results
        document.getElementById('displayed-story-title').innerText = storyTitle || 'Untitled';
        document.getElementById('displayed-story-text').innerText = data.story_text || storyText;

        if (data.result) {
            document.getElementById('result').innerHTML = data.result;
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
        const wordCount = paragraph.trim().split(/\s+/).filter(word => word.length > 0).length;
        visualization += `<div class="story-paragraph" style="width: ${wordCount * 2}px;">${index + 1}</div>`;
    });

    document.getElementById('story-visualization').innerHTML = `
        <h5>Story Structure</h5>
        <div class="story-paragraphs">${visualization}</div>
    `;
}

function displayThemeCloud(result) {
    // Implement theme cloud visualization using the result data
    // Example using D3.js
    if (!result) {
        console.error('No result provided for theme cloud');
        return;
    }

    // Placeholder implementation
    const themes = extractThemesFromResult(result);
    const themeContainer = document.getElementById('theme-cloud');
    themeContainer.innerHTML = '<h5>Theme Cloud</h5><ul>' + themes.map(theme => `<li>${theme}</li>`).join('') + '</ul>';
}

function displaySentimentMeter(result) {
    if (!result) {
        console.error('No result provided for sentiment analysis');
        return;
    }

    let sentimentBar = document.getElementById('sentiment-bar');
    if (!sentimentBar) {
        const container = document.getElementById('sentiment-container');
        if (!container) {
            console.error('Sentiment container not found');
            return;
        }
        sentimentBar = document.createElement('div');
        sentimentBar.id = 'sentiment-bar';
        sentimentBar.classList.add('sentiment-meter');
        container.appendChild(sentimentBar);
    }
    
    const sentimentScore = extractSentimentScore(result);
    sentimentBar.style.width = `${sentimentScore}%`;
    sentimentBar.setAttribute('aria-valuenow', sentimentScore);
}

function displayStyleTimeline(result) {
    // Implement style timeline visualization using the result data
    // Example using D3.js
    if (!result) {
        console.error('No result provided for style timeline');
        return;
    }

    const styleContainer = document.getElementById('analysis-highlights');
    styleContainer.innerHTML = '<h5>Style Highlights</h5><p>' + result + '</p>';
}

function extractSentimentScore(result) {
    if (typeof result !== 'string') {
        console.error('Invalid result type for sentiment extraction');
        return 50; // Default to neutral
    }

    const match = result.match(/Sentiment Score: (-?\d+(\.\d+)?)/);
    if (match) {
        const score = parseFloat(match[1]);
        // Convert the score from [-1, 1] range to [0, 100] range
        return ((score + 1) / 2) * 100;
    }
    console.warn('Sentiment score not found in the result');
    return 50; // Default to neutral if no score found
}

function extractThemesFromResult(result) {
    // Extract themes from the result
    // This can be customized based on the backend response format
    const match = result.match(/Main Themes: (.+)/);
    if (match) {
        return match[1].split(',').map(theme => theme.trim());
    }
    return [];
}

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode ? 'enabled' : 'disabled');
    updateDarkModeButton(isDarkMode);
}

function updateDarkModeButton(isDarkMode) {
    const toggleButton = document.getElementById('dark-mode-toggle');
    if (toggleButton) {
        toggleButton.innerHTML = isDarkMode ? '<i class="fas fa-sun"></i> Light Mode' : '<i class="fas fa-moon"></i> Dark Mode';
    }
}

function applyDarkMode() {
    const darkMode = localStorage.getItem('darkMode');
    if (darkMode === 'enabled') {
        document.body.classList.add('dark-mode');
    }
    updateDarkModeButton(darkMode === 'enabled');
}

document.addEventListener('DOMContentLoaded', function() {
    applyDarkMode();
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
    }
});