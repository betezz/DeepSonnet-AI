try {
    document.getElementById('poem-form').addEventListener('submit', function(event) {
        event.preventDefault();  // Prevent the form from submitting the traditional way

        let poemTitle = document.getElementById('poem_title').value;
        let poemText = document.getElementById('poem_text').value;
        let analysisType = document.getElementById('analysis_type').value;

        // Check if the test poem is requested
        if (poemText.trim() === "<test>") {
            poemTitle = "Malvern Prep March";
            poemText = `Yo Lawrenceville, you're soft as fluff,
Out here actin' like you're tough.
Talkin' smack, but can't keep pace,
You're just background noise in this race.

Your sticks? Weak. Your shots? A joke..
We torch your D like you're a smoke.
Watch us rip it—top-shelf, clean—
Your goalie? Can't even be seen.

You rock those ties, think you're elite,
But on the turf? We run the street.
You pull up scared, we see you sweat,
By halftime, you're not a threat.

Your "legacy" don't mean a thing,
When Malvern's kings, we own this ring.
We dominate, you fake the grind,
Your glory days? All left behind.

Your prissy ways, your fancy crest,
Still can't hang with Philly's best.
So go on, Laville, talk that smack,
But we'll leave you flat on your back`;
            console.log("DeepSonnet AI: Using test poem for analysis.");
        }

        // Show the loading spinner and hide everything else
        document.getElementById('loading').style.display = 'flex';
        document.getElementById('main-content').style.display = 'none';
        document.getElementById('analysis-container').style.display = 'none';
        document.querySelector('.feature-section').style.display = 'none';
        document.getElementById('about-section').style.display = 'none';

        // Clear previous result
        document.getElementById('result').innerHTML = '';

        console.log('Sending analysis request:', {poemText, poemTitle, analysisType});
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
        .then(response => {
            console.log('Received response:', response);
            return response.json();
        })
        .then(data => {
            console.log('Parsed data:', data);
            // Hide the loading spinner
            document.getElementById('loading').style.display = 'none';

            // Show the analysis container
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

            displayAnalysisResult(data);
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('loading').style.display = 'none';
            document.getElementById('main-content').style.display = 'block';
            document.getElementById('result').innerHTML = `<h3 class="text-danger">Error:</h3><p>An error occurred while analyzing the poem. Please try again.</p>`;
        });
    });

    // Add this event listener for the short story form
    document.addEventListener('DOMContentLoaded', function() {
        const shortstoryForm = document.getElementById('shortstory-form');
        if (shortstoryForm) {
            shortstoryForm.addEventListener('submit', function(event) {
                event.preventDefault();
                analyzeShortStory();
            });
        }
    });

    function analyzeShortStory() {
        // Show loading spinner
        document.getElementById('loading').style.display = 'flex';
        document.getElementById('main-content').style.display = 'none';

        let storyTitle = document.getElementById('story_title').value;
        let storyText = document.getElementById('story_text').value;
        let analysisType = document.getElementById('analysis_type').value;

        fetch('/analyze_shortstory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                story_title: storyTitle,
                story_text: storyText,
                analysis_type: analysisType
            })
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading spinner
            document.getElementById('loading').style.display = 'none';
            // Show analysis container
            document.getElementById('analysis-container').style.display = 'flex';

            // Display results
            document.getElementById('displayed-story-title').innerText = storyTitle || 'Untitled';
            document.getElementById('displayed-story-text').innerText = storyText;
            document.getElementById('result').innerHTML = data.result;

            // Display sentiment (if available)
            if (data.sentiment !== undefined) {
                displaySentiment(data.sentiment);
            }

            // Display theme cloud (if available)
            if (data.themes) {
                displayThemeCloud(data.themes);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('loading').style.display = 'none';
            document.getElementById('main-content').style.display = 'block';
            document.getElementById('result').innerHTML = `<h3 class="text-danger">Error:</h3><p>An error occurred while analyzing the short story. Please try again.</p>`;
        });
    }

    // Add a function to reset the view
    function resetView() {
        document.getElementById('main-content').style.display = 'block';
        document.getElementById('analysis-container').style.display = 'none';
        document.querySelector('.feature-section').style.display = 'block';
        document.getElementById('about-section').style.display = 'block';
    }

    // Modify the existing back button functionality
    document.getElementById('back-button').addEventListener('click', function() {
        resetView();
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

    // Comment out or remove the following functions:

    /*
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
                alert('DeepSonnet AI: Rating submitted successfully!');
                fetchRandomPoem();  // Get a new poem after rating
            } else {
                alert('DeepSonnet AI: Failed to submit rating.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('DeepSonnet AI: An error occurred while submitting the rating.');
        });
    }

    // Comment out this event listener
    document.addEventListener('DOMContentLoaded', fetchRandomPoem);
    */

    /* Dark Mode Toggle Functionality */
    function toggleDarkMode() {
        document.body.classList.toggle('dark-mode');
        const isDarkMode = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDarkMode ? 'enabled' : 'disabled');
        updateDarkModeButton(isDarkMode);
    }

    function updateDarkModeButton(isDarkMode) {
        const toggleButton = document.getElementById('dark-mode-toggle');
        if (toggleButton) {
            if (isDarkMode) {
                toggleButton.innerHTML = '<i class="fas fa-sun"></i> Light Mode';
            } else {
                toggleButton.innerHTML = '<i class="fas fa-moon"></i> Dark Mode';
            }
        }
    }

    function applyDarkMode() {
        const darkMode = localStorage.getItem('darkMode');
        if (darkMode === 'enabled') {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
        updateDarkModeButton(darkMode === 'enabled');
    }

    // Apply dark mode when the DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        applyDarkMode();

        // Add event listener to dark mode toggle button if it exists
        const darkModeToggle = document.getElementById('dark-mode-toggle');
        if (darkModeToggle) {
            darkModeToggle.addEventListener('click', toggleDarkMode);
        }

        // Rest of your DOMContentLoaded code...
    });

    /* Word and Character Counter Functionality */
    document.addEventListener('DOMContentLoaded', function() {
        const poemTextArea = document.getElementById('poem_text');
        const counterDisplay = document.getElementById('word-char-counter');

        if (poemTextArea && counterDisplay) {
            poemTextArea.addEventListener('input', function() {
                const text = poemTextArea.value;
                const wordCount = countWords(text);
                const charCount = text.length;
                counterDisplay.textContent = `Words: ${wordCount} | Characters: ${charCount}`;
            });
        }
    });

    // Helper function to count words
    function countWords(str) {
        return str.trim().split(/\s+/).filter(function(word) {
            return word.length > 0;
        }).length;
    }

    function displayAnalysisResult(data) {
        console.log("Analysis data:", data);
        if (data.word_details) {
            const poemDisplay = document.getElementById('displayed-poem-text');
            const lines = poemDisplay.innerText.split('\n');
            poemDisplay.innerHTML = lines.map(line => {
                const words = line.split(' ');
                const formattedWords = words.map(word => {
                    const details = data.word_details[word.toLowerCase()] || { poetic_device: 'none' };
                    if (details.poetic_device !== 'none') {
                        return `<span class="word ${details.poetic_device}">${word}</span>`;
                    }
                    return word; // Return the word without wrapping if no poetic device
                }).join(' ');
                return `<div class="poem-line">${formattedWords}</div>`;
            }).join('\n');

            // Add event listeners for hover
            poemDisplay.querySelectorAll('.word').forEach(wordSpan => {
                wordSpan.addEventListener('mouseover', showWordDetails);
                wordSpan.addEventListener('mouseout', hideWordDetails);
            });

            // Add legend
            addLegend();
        }
    }

    function showWordDetails(event) {
        const word = event.target;
        const device = word.className.split(' ')[1];

        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.innerHTML = `
            <strong>Word:</strong> ${word.innerText}<br>
            <strong>Poetic Device:</strong> ${device}
        `;

        word.appendChild(tooltip);
    }

    function hideWordDetails(event) {
        const tooltip = event.target.querySelector('.tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

    function addLegend() {
        const legend = document.createElement('div');
        legend.id = 'legend';
        legend.innerHTML = `
            <h5>Legend:</h5>
            <span class="alliteration">Alliteration</span>
            <span class="assonance">Assonance</span>
            <span class="none">No specific device</span>
        `;
        document.getElementById('analysis-container').appendChild(legend);
    }

    // Add these functions for sentiment and theme cloud display
    function displaySentiment(sentiment) {
        const sentimentContainer = document.getElementById('sentiment-container');
        sentimentContainer.innerHTML = `<h4>Sentiment Analysis</h4><div id="sentiment-bar"></div>`;
        const sentimentBar = document.getElementById('sentiment-bar');
        sentimentBar.style.width = `${(sentiment + 1) * 50}%`;
        sentimentBar.style.backgroundColor = sentiment > 0 ? '#4CAF50' : '#F44336';
        sentimentBar.innerText = `${(sentiment * 100).toFixed(2)}%`;
    }

    function displayThemeCloud(themes) {
        const themeCloud = document.getElementById('theme-cloud');
        themeCloud.innerHTML = '<h4>Theme Cloud</h4>';
        themes.forEach(theme => {
            const themeSpan = document.createElement('span');
            themeSpan.className = 'theme-tag';
            themeSpan.innerText = theme;
            themeCloud.appendChild(themeSpan);
        });
    }
} catch (error) {
    console.error("An error occurred in the JavaScript:", error);
}   