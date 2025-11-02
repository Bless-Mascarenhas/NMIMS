// Wait until DOM is ready, then wire UI
document.addEventListener('DOMContentLoaded', () => {
    const cityInput = document.getElementById('cityInput');
    const regionSelect = document.getElementById('regionSelect');
    const districtSelect = document.getElementById('districtSelect');
    const citySelect = document.getElementById('citySelect');
    const regionSearch = document.getElementById('regionSearch');
    const searchBtn = document.getElementById('searchBtn');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const currentWeather = document.getElementById('currentWeather');
    const forecastSection = document.getElementById('forecastSection');
    const alertsSection = document.getElementById('alertsSection');
    const recommendationsSection = document.getElementById('recommendationsSection');

    if (!cityInput || !searchBtn) {
        console.error('Weather UI: missing required DOM elements');
        return;
    }

    // Wire events
    searchBtn.addEventListener('click', () => searchWeather(cityInput, regionSelect, districtSelect, citySelect, regionSearch, { loading, error, currentWeather, forecastSection, alertsSection, recommendationsSection }));
    cityInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchWeather(cityInput, regionSelect, districtSelect, citySelect, regionSearch, { loading, error, currentWeather, forecastSection, alertsSection, recommendationsSection });
        }
    });

    // Populate district and city selects when a region is chosen
    const regionData = {
        'Punjab': { districts: ['Ludhiana','Amritsar','Jalandhar'], cities: ['Ludhiana','Amritsar'] },
        'Uttar Pradesh': { districts: ['Lucknow','Kanpur','Agra'], cities: ['Lucknow','Kanpur'] },
        'Maharashtra': { districts: ['Pune','Nagpur','Nashik'], cities: ['Pune','Mumbai'] }
    };

    if (regionSelect) {
        regionSelect.addEventListener('change', () => {
            const val = regionSelect.value;
            // Reset district and city
            districtSelect.innerHTML = '<option value="">-- Select district --</option>';
            citySelect.innerHTML = '<option value="">-- Select city --</option>';

            if (val && regionData[val]) {
                // populate districts
                regionData[val].districts.forEach(d => {
                    const o = document.createElement('option'); o.value = d; o.textContent = d; districtSelect.appendChild(o);
                });
                // populate cities
                regionData[val].cities.forEach(c => {
                    const o = document.createElement('option'); o.value = c; o.textContent = c; citySelect.appendChild(o);
                });

                districtSelect.classList.remove('hidden');
                citySelect.classList.remove('hidden');
                cityInput.classList.add('hidden');
            } else {
                districtSelect.classList.add('hidden');
                citySelect.classList.add('hidden');
                cityInput.classList.remove('hidden');
            }
        });
    }

    // Load default city
    cityInput.value = 'Mumbai';
    searchWeather(cityInput, regionSelect, districtSelect, citySelect, regionSearch, { loading, error, currentWeather, forecastSection, alertsSection, recommendationsSection });
});

// Search Weather Function
async function searchWeather(cityInput, regionSelect, els) {
    const city = cityInput?.value?.trim();
    const region = regionSelect?.value || '';
    const { loading, error, currentWeather, forecastSection, alertsSection, recommendationsSection } = els || {};

    if (!city) {
        showError('Please enter a city name', error);
        return;
    }

    showLoading(loading);
    hideError(error);
    hideAllSections({ currentWeather, forecastSection, alertsSection, recommendationsSection });

    try {
        let url;
        if (region && region !== '') {
            url = `/api/weather?region=${encodeURIComponent(region)}`;
        } else {
            url = `/api/weather?city=${encodeURIComponent(city)}`;
        }
        const response = await fetch(url);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch weather data');
        }

        hideLoading(loading);
        displayWeatherData(data);

    } catch (err) {
        hideLoading(loading);
        showError(err.message || 'An error occurred while fetching weather data', error);
    }
}

// Display Weather Data (full payload)
function displayWeatherData(data) {
    try {
        // Show whether data is live or mocked
        setDataSourceBadge(data.source);

        displayCurrentWeather(data.current);
        displayForecast(data.forecast);
        displayAlerts(data.alerts);
        displayRecommendations(data.recommendations);
    } catch (e) {
        console.error('displayWeatherData error', e);
    }
}

// Show a small badge indicating whether the data is live or mocked
function setDataSourceBadge(source) {
    const badge = document.getElementById('dataSourceBadge');
    if (!badge) return;
    if (!source || source !== 'live') {
        badge.textContent = 'Mock data';
        badge.classList.remove('hidden');
        badge.classList.remove('live');
        badge.classList.add('mock');
    } else {
        badge.textContent = 'Live data';
        badge.classList.remove('hidden');
        badge.classList.remove('mock');
        badge.classList.add('live');
    }
}

// Display Current Weather
function displayCurrentWeather(current) {
    const cityNameEl = document.getElementById('cityName');
    const weatherDescEl = document.getElementById('weatherDesc');
    const weatherIconEl = document.getElementById('weatherIcon');
    const temperatureEl = document.getElementById('temperature');
    const feelsLikeEl = document.getElementById('feelsLike');
    const humidityEl = document.getElementById('humidity');
    const windSpeedEl = document.getElementById('windSpeed');
    const pressureEl = document.getElementById('pressure');
    const visibilityEl = document.getElementById('visibility');
    const cloudsEl = document.getElementById('clouds');
    const sunTimesEl = document.getElementById('sunTimes');

    cityNameEl.textContent = `${current.city || ''}, ${current.country || ''}`;
    weatherDescEl.textContent = current.description || '';
    if (current.icon) weatherIconEl.src = `https://openweathermap.org/img/wn/${current.icon}@2x.png`;
    temperatureEl.textContent = (current.temperature !== undefined) ? current.temperature : '--';
    feelsLikeEl.textContent = (current.feels_like !== undefined) ? current.feels_like : '--';
    humidityEl.textContent = (current.humidity !== undefined) ? `${current.humidity}%` : '--';
    windSpeedEl.textContent = (current.wind_speed !== undefined) ? `${current.wind_speed} km/h` : '--';
    pressureEl.textContent = (current.pressure !== undefined) ? `${current.pressure} hPa` : '--';
    visibilityEl.textContent = (current.visibility !== undefined) ? `${current.visibility} km` : '--';
    cloudsEl.textContent = (current.clouds !== undefined) ? `${current.clouds}%` : '--';
    sunTimesEl.textContent = `${current.sunrise || '--'} / ${current.sunset || '--'}`;

    const currentWeatherEl = document.getElementById('currentWeather');
    if (currentWeatherEl) currentWeatherEl.classList.remove('hidden');
}

// Display 5-Day Forecast
function displayForecast(forecast) {
    const container = document.getElementById('forecastContainer');
    container.innerHTML = '';
    
    forecast.forEach(day => {
        const card = document.createElement('div');
        card.className = 'forecast-card';
        card.innerHTML = `
            <div class="forecast-date">${day.date}</div>
            <div class="forecast-icon">
                <img src="https://openweathermap.org/img/wn/${day.icon}@2x.png" alt="${day.description}">
            </div>
            <div class="forecast-temp">
                ${day.temp_max}° / ${day.temp_min}°
            </div>
            <div class="forecast-desc">${day.description}</div>
            <div class="forecast-details">
                <div class="forecast-detail">
                    <i class="fas fa-tint"></i> ${day.humidity}%
                </div>
                <div class="forecast-detail">
                    <i class="fas fa-wind"></i> ${day.wind_speed} km/h
                </div>
                <div class="forecast-detail">
                    <i class="fas fa-cloud-rain"></i> ${day.rain_probability}%
                </div>
            </div>
        `;
        container.appendChild(card);
    });
    
    const forecastSectionEl = document.getElementById('forecastSection');
    if (forecastSectionEl) forecastSectionEl.classList.remove('hidden');
}

// Display Weather Alerts
function displayAlerts(alerts) {
    const alertsSectionEl = document.getElementById('alertsSection');
    const container = document.getElementById('alertsContainer');
    if (!alerts || alerts.length === 0) {
        if (alertsSectionEl) alertsSectionEl.classList.add('hidden');
        return;
    }

    if (!container) return;
    container.innerHTML = '';

    alerts.forEach(alert => {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert-item';
        alertDiv.innerHTML = `
            <h3><i class="fas fa-exclamation-circle"></i> ${alert.event}</h3>
            <p>${alert.description}</p>
            <div class="alert-time">
                <strong>Start:</strong> ${alert.start} | <strong>End:</strong> ${alert.end}
            </div>
        `;
        container.appendChild(alertDiv);
    });

    if (alertsSectionEl) alertsSectionEl.classList.remove('hidden');
}

// Display Farming Recommendations
function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendationsContainer');
    const recSection = document.getElementById('recommendationsSection');
    if (!container) return;
    container.innerHTML = '';

    // If there are no recommendations from API, show helpful farming tips
    const defaultRecs = [
        { type: 'info', title: 'Soil Health', message: 'Test soil pH regularly. Add lime for acidic soil and organic matter for alkaline soils.' },
        { type: 'info', title: 'Irrigation', message: 'Monitor soil moisture; irrigate during dry spells and avoid waterlogging.' },
        { type: 'info', title: 'Pest & Disease', message: 'Scout fields weekly and remove infected plants early to prevent spread.' }
    ];

    const items = (recommendations && recommendations.length) ? recommendations : defaultRecs;

    items.forEach(rec => {
        const card = document.createElement('div');
        card.className = `recommendation-card ${rec.type || ''}`;
        card.innerHTML = `
            <h3>${rec.title || 'Recommendation'}</h3>
            <p>${rec.message || ''}</p>
        `;
        container.appendChild(card);
    });

    if (recSection) recSection.classList.remove('hidden');
}

// Helper Functions
function showLoading(el) { if (el) el.classList.remove('hidden'); }
function hideLoading(el) { if (el) el.classList.add('hidden'); }
function showError(message, el) { if (!el) return; el.textContent = message; el.classList.remove('hidden'); }
function hideError(el) { if (!el) return; el.classList.add('hidden'); }
function hideAllSections(els) {
    if (!els) return;
    const { currentWeather, forecastSection, alertsSection, recommendationsSection } = els;
    if (currentWeather) currentWeather.classList.add('hidden');
    if (forecastSection) forecastSection.classList.add('hidden');
    if (alertsSection) alertsSection.classList.add('hidden');
    if (recommendationsSection) recommendationsSection.classList.add('hidden');
}

// Wire the sample recommendations CTA button
document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('suggestionsBtn');
    if (!btn) return;
    btn.addEventListener('click', () => {
        const sample = [
            { type: 'info', title: 'Soil Tip', message: 'Apply compost to improve soil organic matter and structure.' },
            { type: 'info', title: 'Water Management', message: 'Schedule irrigation in early morning to reduce evaporation losses.' },
            { type: 'warning', title: 'Pest Alert', message: 'Check for aphids and caterpillars; use neem oil if infestation is observed.' }
        ];
        displayRecommendations(sample);
        setDataSourceBadge('mock');
        // scroll to recommendations
        const recSection = document.getElementById('recommendationsSection');
        if (recSection) recSection.scrollIntoView({ behavior: 'smooth' });
    });
});