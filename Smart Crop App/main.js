        const translations = {
            en: {
                title: 'Smart Crops',
                login: 'Login',
                weatherAlert: 'Weather Alert',
                alertMsg: 'Heavy rainfall expected in Punjab region - Next 48 hours',
                weatherForecast: 'Weather Forecast',
                weatherDesc: '7-day accurate predictions',
                cropPlanner: 'Crop Planner',
                plannerDesc: 'Plan your season',
                diseaseDetection: 'Disease Detection',
                diseaseDesc: 'Identify crop diseases',
                marketPrices: 'Market Prices',
                marketDesc: 'Live mandi rates',
                expertAdvisory: 'Expert Advisory',
                advisoryDesc: 'Get farming tips',
                govtSchemes: 'Govt. Schemes',
                schemesDesc: 'Available subsidies',
                heatmapTitle: 'Crop Disease Outbreak Heatmap'
            },
            hi: {
                title: 'स्मार्ट फसल',
                login: 'लॉगिन',
                weatherAlert: 'मौसम चेतावनी',
                alertMsg: 'पंजाब क्षेत्र में भारी बारिश की संभावना - अगले 48 घंटे',
                weatherForecast: 'मौसम पूर्वानुमान',
                weatherDesc: '7-दिन की सटीक भविष्यवाणी',
                cropPlanner: 'फसल योजनाकार',
                plannerDesc: 'अपने सीजन की योजना बनाएं',
                diseaseDetection: 'रोग पहचान',
                diseaseDesc: 'फसल रोगों की पहचान करें',
                marketPrices: 'बाजार मूल्य',
                marketDesc: 'लाइव मंडी दरें',
                expertAdvisory: 'विशेषज्ञ सलाह',
                advisoryDesc: 'खेती के टिप्स पाएं',
                govtSchemes: 'सरकारी योजनाएं',
                schemesDesc: 'उपलब्ध सब्सिडी',
                heatmapTitle: 'फसल रोग प्रकोप हीटमैप'
            },
            mr: {
                title: 'स्मार्ट पीक',
                login: 'लॉगिन',
                weatherAlert: 'हवामान सूचना',
                alertMsg: 'पंजाब प्रदेशात मुसळधार पाऊस अपेक्षित - पुढील 48 तास',
                weatherForecast: 'हवामान अंदाज',
                weatherDesc: '7-दिवसांचे अचूक अंदाज',
                cropPlanner: 'पीक नियोजक',
                plannerDesc: 'तुमच्या हंगामाची योजना करा',
                diseaseDetection: 'रोग ओळख',
                diseaseDesc: 'पीक रोग ओळखा',
                marketPrices: 'बाजार भाव',
                marketDesc: 'थेट मंडी दर',
                expertAdvisory: 'तज्ञ सल्ला',
                advisoryDesc: 'शेती टिप्स मिळवा',
                govtSchemes: 'सरकारी योजना',
                schemesDesc: 'उपलब्ध अनुदान',
                heatmapTitle: 'पीक रोग प्रादुर्भाव हीटमॅप'
            }
        };

        document.getElementById('langSelector').addEventListener('change', function(e) {
            const lang = e.target.value;
            updateLanguage(lang);
        });

        function updateLanguage(lang) {
            const t = translations[lang];
            document.querySelector('.logo h1').textContent = t.title;
            document.querySelector('.login-btn').textContent = t.login;
            document.querySelectorAll('.card')[0].querySelector('h2').textContent = t.weatherForecast;
            document.querySelectorAll('.card')[0].querySelector('p').textContent = t.weatherDesc;
            document.querySelectorAll('.card')[1].querySelector('h2').textContent = t.cropPlanner;
            document.querySelectorAll('.card')[1].querySelector('p').textContent = t.plannerDesc;
            document.querySelectorAll('.card')[2].querySelector('h2').textContent = t.diseaseDetection;
            document.querySelectorAll('.card')[2].querySelector('p').textContent = t.diseaseDesc;
            document.querySelectorAll('.card')[3].querySelector('h2').textContent = t.marketPrices;
            document.querySelectorAll('.card')[3].querySelector('p').textContent = t.marketDesc;
            document.querySelectorAll('.card')[4].querySelector('h2').textContent = t.expertAdvisory;
            document.querySelectorAll('.card')[4].querySelector('p').textContent = t.advisoryDesc;
            document.querySelectorAll('.card')[5].querySelector('h2').textContent = t.govtSchemes;
            document.querySelectorAll('.card')[5].querySelector('p').textContent = t.schemesDesc;
            document.querySelector('.alert-content h3').textContent = t.weatherAlert;
            document.querySelector('.alert-content p').textContent = t.alertMsg;
            document.querySelector('.heatmap-header h2').textContent = t.heatmapTitle;
        }

        function handleLogin() {
            alert('Login functionality - Connect to your authentication system');
        }

        function handleNavigation(section) {
            // Navigate to planner page when user clicks Crop Planner card
            if (section === 'planner') {
                // If running the Flask backend we serve the planner at /planner
                window.location.href = '/planner';
                return;
            }

            // The "market" card opens the heatmap page
            if (section === 'market') {
                // Navigate to the heatmap page which is served at /heatmap
                window.location.href = '/heatmap';
                return;
            }

            // Weather card opens the dedicated weather page
            if (section === 'weather') {
                window.location.href = '/weather';
                return;
            }

            // Disease detection page
            if (section === 'disease') {
                // Serve the disease detection UI at /disease
                window.location.href = '/disease';
                return;
            }

            // Government schemes page
            if (section === 'schemes') {
                window.location.href = '/schemes';
                return;
            }

            // Advisory / Market Prices
            if (section === 'advisory') {
                window.location.href = '/advisory';
                return;
            }

            alert(`Navigating to ${section} section - Connect to your routing system`);
        }
