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
    })
    .catch(error => {
        // Hide the loading spinner and show error
        document.getElementById('loading').style.display = 'none';
        document.getElementById('result').innerHTML = `<h3 class="text-danger">Error:</h3><p>Failed to analyze the poem.</p>`;
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
