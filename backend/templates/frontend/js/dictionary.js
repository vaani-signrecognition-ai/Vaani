// Search ISL Dictionary
async function searchISL() {
  const query = document.getElementById('searchWord').value.trim();
  const resultDiv = document.getElementById('result');

  if (!query) {
    resultDiv.innerHTML = '<p class="text-muted">Please enter a word to search 👋</p>';
    return;
  }

  resultDiv.innerHTML = `
        <div class="text-center p-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Searching...</span>
            </div>
            <p class="mt-2 text-muted">Searching the VAANI dictionary...</p>
        </div>`;

  try {
    // Detect if running via file:// protocol (direct file open)
    let apiUrl = '/api/dictionary';
    if (window.location.protocol === 'file:') {
      apiUrl = 'http://127.0.0.1:5000/api/dictionary';
      console.warn("Detected file:// protocol. Using absolute URL for backend.");
    }

    const response = await fetch(`${apiUrl}?search=${encodeURIComponent(query)}`);
    if (!response.ok) {
      if (response.status === 404) throw new Error('Dictionary service not found');
      if (response.status === 500) throw new Error('Database connection failed');
      throw new Error('Failed to fetch from dictionary');
    }

    const matches = await response.json();

    if (matches.length === 0) {
      resultDiv.innerHTML = `
          <div class="alert alert-info">
            <i class="fas fa-search me-2"></i>
            No results found for "<strong>${query}</strong>". Try searching for a letter, number, or common word.
          </div>`;
      return;
    }

    // Build result cards
    let html = '';
    matches.forEach(entry => {
      const word = entry.word;
      // Use letter colors for variety
      const colors = ['#667eea', '#48bb78', '#f56565', '#ed8936', '#9f7aea', '#e91e63', '#38b2ac'];
      const categoryColor = colors[word.charCodeAt(0) % colors.length];

      const imageSrc = entry.image_path || entry.video_path || 'assets/placeholder-sign.png';

      html += `
          <div class="sign-result mb-4 p-4" style="border-radius: 12px; border-left: 5px solid ${categoryColor}; background: #f8f9fa; transition: transform 0.3s ease;">
            <div class="row align-items-center">
              <div class="col-md-4 text-center mb-3 mb-md-0">
                <div class="sign-image-container" style="background: white; padding: 10px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                    <img src="${imageSrc}" alt="${word} sign" 
                         class="img-fluid rounded" 
                         style="max-height: 250px; cursor: pointer;"
                         onclick="window.open(this.src, '_blank')"
                         onerror="this.onerror=null; this.src='https://via.placeholder.com/250x180?text=${word}';">
                </div>
              </div>
              <div class="col-md-8">
                <div class="d-flex justify-content-between align-items-start">
                  <h4 class="mb-2" style="text-transform: capitalize; color: #2d3748;">
                    <i class="fas fa-sign-language me-2" style="color: ${categoryColor};"></i>
                    ${word}
                  </h4>
                  <button class="btn btn-sm btn-outline-secondary rounded-circle" 
                          onclick="speakWord('${word}')" 
                          title="Listen to pronunciation">
                    <i class="fas fa-volume-up"></i>
                  </button>
                </div>
                <div class="d-flex align-items-center mb-3">
                    <span class="badge" style="background: ${categoryColor}; font-size: 0.85rem; padding: 6px 12px;">
                      ${isNaN(word) ? (word.length === 1 ? 'Letter' : 'Word') : 'Number'}
                    </span>
                    <small class="ms-3 text-muted"><i class="fas fa-info-circle me-1"></i> Indian Sign Language</small>
                </div>
                <p class="text-muted mt-2 mb-0">Discover the sign for "<strong>${word}</strong>". Click the volume icon to hear the word, or click the image to view it full size.</p>
              </div>
            </div>
          </div>`;
    });

    resultDiv.innerHTML = html;

  } catch (error) {
    console.error('Dictionary search error:', error);
    resultDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error searching the dictionary. Please try again later.
            </div>`;
  }
}

// Speak the word using Web Speech API
function speakWord(text) {
  if (!window.speechSynthesis) {
    alert("Target browser does not support text-to-speech.");
    return;
  }

  // Prettify text (remove underscores, etc)
  const cleanText = text.replace(/_/g, ' ').trim();
  const utterance = new SpeechSynthesisUtterance(cleanText);
  utterance.lang = 'en-IN';
  utterance.rate = 0.9;
  window.speechSynthesis.speak(utterance);
}

// Category color mapping
function getCategoryColor(category) {
  const colors = {
    greetings: '#667eea',
    food: '#48bb78',
    emergency: '#f56565',
    emotions: '#ed8936',
    numbers: '#9f7aea',
    family: '#e91e63',
    daily: '#38b2ac'
  };
  return colors[category] || '#667eea';
}

// Allow Enter key to trigger search
document.getElementById('searchWord').addEventListener('keypress', function (e) {
  if (e.key === 'Enter') {
    searchISL();
  }
});
