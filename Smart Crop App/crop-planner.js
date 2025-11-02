// API Configuration
const API_URL = 'http://localhost:5000/api';

// Global variables
let currentStream = null;
let capturedImage = null;

// Form submission
document.getElementById('cropForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading">Analyzing</span>';
    
    try {
        const formData = new FormData(e.target);
        
        // Add captured image if exists
        if (capturedImage) {
            formData.set('image', capturedImage);
        }
        
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
            document.getElementById('results').style.display = 'block';
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to analyze. Please make sure the backend server is running.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span>🚀 Analyze & Get Recommendations</span>';
    }
});

// Display results
function displayResults(data) {
    // Weather Card
    const weatherCard = document.getElementById('weatherCard');
    weatherCard.innerHTML = `
        <h3>🌤️ Current Weather</h3>
        <p><strong>Temperature:</strong> ${data.weather.temperature}°C</p>
        <p><strong>Humidity:</strong> ${data.weather.humidity}%</p>
        <p><strong>Conditions:</strong> ${data.weather.description}</p>
    `;
    
    // pH Card
    const phCard = document.getElementById('phCard');
    const phStatusClass = data.ph_analysis.status === 'Optimal' ? 'status-optimal' : 'status-adjust';
    phCard.innerHTML = `
        <h3>🔬 Soil pH Analysis</h3>
        <p><strong>pH Value:</strong> ${data.ph_analysis.value} 
        <span class="status-badge ${phStatusClass}">${data.ph_analysis.status}</span></p>
        <p><strong>Recommendation:</strong> ${data.ph_analysis.advice}</p>
    `;
    
    // Disease Card
    if (data.disease_analysis && data.disease_analysis.length > 0) {
        const diseaseCard = document.getElementById('diseaseCard');
        diseaseCard.style.display = 'block';
        diseaseCard.innerHTML = `
            <h3>🔍 Disease Analysis</h3>
            ${data.disease_analysis.map(item => `<p>• ${item}</p>`).join('')}
        `;
    }
    
    // Crop Recommendations
    const cropRecommendations = document.getElementById('cropRecommendations');
    if (data.crop_recommendations && data.crop_recommendations.length > 0) {
        cropRecommendations.innerHTML = data.crop_recommendations.map((crop, index) => `
            <div class="crop-card" style="animation: fadeIn 0.5s ${index * 0.1}s both;">
                <h4>🌱 ${crop.name}</h4>
                <div class="metric">
                    <span>Yield per Acre:</span>
                    <span>${crop.yield_per_acre} quintals</span>
                </div>
                <div class="metric">
                    <span>Total Yield:</span>
                    <span>${crop.total_yield.toFixed(1)} quintals</span>
                </div>
                <div class="metric">
                    <span>Price per Quintal:</span>
                    <span>₹${crop.price_per_quintal.toLocaleString()}</span>
                </div>
                <div class="metric">
                    <span>Est. Revenue:</span>
                    <span>₹${crop.estimated_revenue.toLocaleString()}</span>
                </div>
                <div class="metric">
                    <span>Est. Profit:</span>
                    <span style="color: ${crop.profit > 0 ? '#48bb78' : '#f56565'}">
                        ₹${crop.profit.toLocaleString()}
                    </span>
                </div>
                <div class="metric">
                    <span>ROI:</span>
                    <span>${crop.roi}%</span>
                </div>
                <div class="score">
                    Suitability Score: ${crop.suitability_score}/100
                </div>
            </div>
        `).join('');
    } else {
        cropRecommendations.innerHTML = `
            <p style="color: #718096; text-align: center;">
                No suitable crops found for the selected conditions. 
                Try adjusting your inputs or consider soil amendments.
            </p>
        `;
    }
    
    // Planting Calendar
    const plantingCalendar = document.getElementById('plantingCalendar');
    if (data.planting_calendar && data.planting_calendar.length > 0) {
        plantingCalendar.innerHTML = data.planting_calendar.map(item => `
            <div class="calendar-item">
                <h4>${item.crop}</h4>
                <p><strong>🌱 Planting Time:</strong> ${item.planting_time}</p>
                <p><strong>🌾 Harvest Time:</strong> ${item.harvest_time}</p>
                <p><strong>⏱️ Duration:</strong> ${item.duration}</p>
            </div>
        `).join('');
    }
}

// File input handling
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            displayPreview(e.target.result);
        };
        reader.readAsDataURL(file);
        capturedImage = null; // Clear captured image if file is selected
    }
}

// Camera functions
function openCamera() {
    const modal = document.getElementById('cameraModal');
    const video = document.getElementById('video');
    
    modal.style.display = 'block';
    
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        .then(stream => {
            currentStream = stream;
            video.srcObject = stream;
        })
        .catch(err => {
            alert('Unable to access camera: ' + err.message);
            closeCamera();
        });
}

function closeCamera() {
    const modal = document.getElementById('cameraModal');
    const video = document.getElementById('video');
    
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
        currentStream = null;
    }
    
    video.srcObject = null;
    modal.style.display = 'none';
}

function capturePhoto() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);
    
    canvas.toBlob(blob => {
        capturedImage = new File([blob], 'captured-photo.jpg', { type: 'image/jpeg' });
        
        const dataUrl = canvas.toDataURL('image/jpeg');
        displayPreview(dataUrl);
        
        // Clear file input
        document.getElementById('fileInput').value = '';
        
        closeCamera();
    }, 'image/jpeg', 0.8);
}

function displayPreview(imageUrl) {
    const preview = document.getElementById('imagePreview');
    preview.innerHTML = `
        <img src="${imageUrl}" alt="Preview" class="preview-image">
        <p style="margin-top: 0.5rem; color: #718096;">Image uploaded successfully ✓</p>
    `;
}

// Animation keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);

// Form validation helpers
document.getElementById('ph').addEventListener('input', function(e) {
    const value = parseFloat(e.target.value);
    if (value < 4 || value > 10) {
        e.target.setCustomValidity('pH must be between 4 and 10');
    } else {
        e.target.setCustomValidity('');
    }
});

document.getElementById('acres').addEventListener('input', function(e) {
    const value = parseFloat(e.target.value);
    if (value <= 0) {
        e.target.setCustomValidity('Area must be greater than 0');
    } else {
        e.target.setCustomValidity('');
    }
});

document.getElementById('budget').addEventListener('input', function(e) {
    const value = parseFloat(e.target.value);
    if (value < 1000) {
        e.target.setCustomValidity('Budget must be at least ₹1000');
    } else {
        e.target.setCustomValidity('');
    }
});

// Initialize
console.log('Smart Crop Planner initialized. Make sure Flask backend is running on http://localhost:5000');