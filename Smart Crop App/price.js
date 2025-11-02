        // Sample data structure - In production, this would come from Python backend
        const marketData = [
            // Vegetables
            {name: "Tomato", type: "vegetables", icon: "🍅", current: 45, yesterday: 42, week: 48, month: 40, year: 38},
            {name: "Potato", type: "vegetables", icon: "🥔", current: 25, yesterday: 25, week: 26, month: 24, year: 22},
            {name: "Onion", type: "vegetables", icon: "🧅", current: 35, yesterday: 38, week: 36, month: 32, year: 30},
            {name: "Carrot", type: "vegetables", icon: "🥕", current: 40, yesterday: 39, week: 42, month: 38, year: 35},
            {name: "Cabbage", type: "vegetables", icon: "🥬", current: 30, yesterday: 28, week: 32, month: 29, year: 27},
            {name: "Cauliflower", type: "vegetables", icon: "🥦", current: 50, yesterday: 52, week: 48, month: 55, year: 45},
            {name: "Broccoli", type: "vegetables", icon: "🥦", current: 60, yesterday: 58, week: 62, month: 57, year: 52},
            {name: "Spinach", type: "vegetables", icon: "🥬", current: 35, yesterday: 35, week: 34, month: 36, year: 33},
            {name: "Bell Pepper", type: "vegetables", icon: "🫑", current: 70, yesterday: 68, week: 72, month: 65, year: 60},
            {name: "Cucumber", type: "vegetables", icon: "🥒", current: 38, yesterday: 40, week: 37, month: 39, year: 35},
            {name: "Eggplant", type: "vegetables", icon: "🍆", current: 42, yesterday: 41, week: 45, month: 40, year: 38},
            {name: "Pumpkin", type: "vegetables", icon: "🎃", current: 28, yesterday: 28, week: 30, month: 27, year: 25},
            {name: "Green Beans", type: "vegetables", icon: "🫘", current: 55, yesterday: 53, week: 57, month: 52, year: 48},
            {name: "Peas", type: "vegetables", icon: "🫛", current: 48, yesterday: 50, week: 46, month: 49, year: 45},
            {name: "Corn", type: "vegetables", icon: "🌽", current: 32, yesterday: 30, week: 33, month: 31, year: 28},
            
            // Fruits
            {name: "Apple", type: "fruits", icon: "🍎", current: 120, yesterday: 118, week: 122, month: 115, year: 110},
            {name: "Banana", type: "fruits", icon: "🍌", current: 50, yesterday: 52, week: 48, month: 51, year: 48},
            {name: "Orange", type: "fruits", icon: "🍊", current: 80, yesterday: 78, week: 82, month: 75, year: 70},
            {name: "Mango", type: "fruits", icon: "🥭", current: 90, yesterday: 92, week: 88, month: 95, year: 85},
            {name: "Grapes", type: "fruits", icon: "🍇", current: 100, yesterday: 98, week: 102, month: 97, year: 92},
            {name: "Watermelon", type: "fruits", icon: "🍉", current: 35, yesterday: 35, week: 36, month: 34, year: 32},
            {name: "Pineapple", type: "fruits", icon: "🍍", current: 65, yesterday: 63, week: 67, month: 62, year: 58},
            {name: "Strawberry", type: "fruits", icon: "🍓", current: 150, yesterday: 145, week: 155, month: 140, year: 130},
            {name: "Papaya", type: "fruits", icon: "🫐", current: 55, yesterday: 57, week: 53, month: 56, year: 52},
            {name: "Pomegranate", type: "fruits", icon: "🍎", current: 110, yesterday: 108, week: 112, month: 105, year: 100},
            {name: "Kiwi", type: "fruits", icon: "🥝", current: 180, yesterday: 182, week: 178, month: 185, year: 170},
            {name: "Pear", type: "fruits", icon: "🍐", current: 95, yesterday: 93, week: 97, month: 92, year: 88},
            {name: "Peach", type: "fruits", icon: "🍑", current: 105, yesterday: 107, week: 103, month: 108, year: 98},
            {name: "Lemon", type: "fruits", icon: "🍋", current: 70, yesterday: 68, week: 72, month: 67, year: 63},
            {name: "Avocado", type: "fruits", icon: "🥑", current: 140, yesterday: 138, week: 142, month: 135, year: 125}
        ];

        let currentFilter = 'all';
        let searchTerm = '';

        function init() {
            document.getElementById('currentDate').textContent = new Date().toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            renderItems();
            setupEventListeners();
        }

        function setupEventListeners() {
            document.getElementById('searchInput').addEventListener('input', (e) => {
                searchTerm = e.target.value.toLowerCase();
                renderItems();
            });

            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                    e.target.classList.add('active');
                    currentFilter = e.target.dataset.filter;
                    renderItems();
                });
            });
        }

        function calculateChange(current, previous) {
            const diff = current - previous;
            const percent = ((diff / previous) * 100).toFixed(2);
            return {diff, percent};
        }

        function getChangeClass(diff) {
            if (diff > 0) return 'positive';
            if (diff < 0) return 'negative';
            return 'neutral';
        }

        function filterItems(items) {
            return items.filter(item => {
                const matchesSearch = item.name.toLowerCase().includes(searchTerm);
                
                if (!matchesSearch) return false;

                if (currentFilter === 'all') return true;
                if (currentFilter === 'vegetables' || currentFilter === 'fruits') {
                    return item.type === currentFilter;
                }
                if (currentFilter === 'gaining') {
                    return item.current > item.yesterday;
                }
                if (currentFilter === 'losing') {
                    return item.current < item.yesterday;
                }
                return true;
            });
        }

        function renderItems() {
            const grid = document.getElementById('itemsGrid');
            const filtered = filterItems(marketData);
            
            grid.innerHTML = filtered.map(item => {
                const change = calculateChange(item.current, item.yesterday);
                const changeClass = getChangeClass(change.diff);
                const changeSymbol = change.diff > 0 ? '▲' : change.diff < 0 ? '▼' : '●';
                
                return `
                    <div class="card" onclick="showDetails('${item.name}')">
                        <div class="card-header">
                            <div class="item-name">${item.name}</div>
                            <div class="item-icon">${item.icon}</div>
                        </div>
                        <div class="current-price">₹${item.current}/kg</div>
                        <div class="price-change ${changeClass}">
                            ${changeSymbol} ${Math.abs(change.diff)} (${Math.abs(change.percent)}%)
                        </div>
                        <div class="historical-prices">
                            <div class="price-row">
                                <span class="price-label">Yesterday:</span>
                                <span class="price-value">₹${item.yesterday}</span>
                            </div>
                            <div class="price-row">
                                <span class="price-label">Last Week:</span>
                                <span class="price-value">₹${item.week}</span>
                            </div>
                            <div class="price-row">
                                <span class="price-label">Last Month:</span>
                                <span class="price-value">₹${item.month}</span>
                            </div>
                            <div class="price-row">
                                <span class="price-label">Last Year:</span>
                                <span class="price-value">₹${item.year}</span>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function showDetails(itemName) {
            const item = marketData.find(i => i.name === itemName);
            const modal = document.getElementById('detailModal');
            const modalBody = document.getElementById('modalBody');
            
            const dayChange = calculateChange(item.current, item.yesterday);
            const weekChange = calculateChange(item.current, item.week);
            const monthChange = calculateChange(item.current, item.month);
            const yearChange = calculateChange(item.current, item.year);
            
            modalBody.innerHTML = `
                <h2>${item.icon} ${item.name} - Detailed Analysis</h2>
                <div style="margin: 20px 0;">
                    <h3>Current Price: ₹${item.current}/kg</h3>
                </div>
                <div class="historical-prices">
                    <h4>Price Comparisons:</h4>
                    <div class="price-row">
                        <span class="price-label">vs Yesterday (₹${item.yesterday}):</span>
                        <span class="price-value ${getChangeClass(dayChange.diff)}">
                            ${dayChange.diff > 0 ? '+' : ''}₹${dayChange.diff} (${dayChange.percent}%)
                        </span>
                    </div>
                    <div class="price-row">
                        <span class="price-label">vs Last Week (₹${item.week}):</span>
                        <span class="price-value ${getChangeClass(weekChange.diff)}">
                            ${weekChange.diff > 0 ? '+' : ''}₹${weekChange.diff} (${weekChange.percent}%)
                        </span>
                    </div>
                    <div class="price-row">
                        <span class="price-label">vs Last Month (₹${item.month}):</span>
                        <span class="price-value ${getChangeClass(monthChange.diff)}">
                            ${monthChange.diff > 0 ? '+' : ''}₹${monthChange.diff} (${monthChange.percent}%)
                        </span>
                    </div>
                    <div class="price-row">
                        <span class="price-label">vs Last Year (₹${item.year}):</span>
                        <span class="price-value ${getChangeClass(yearChange.diff)}">
                            ${yearChange.diff > 0 ? '+' : ''}₹${yearChange.diff} (${yearChange.percent}%)
                        </span>
                    </div>
                </div>
                <div class="chart-container">
                    <canvas id="priceChart"></canvas>
                </div>
            `;
            
            modal.classList.add('active');
            drawChart(item);
        }

        function closeModal() {
            document.getElementById('detailModal').classList.remove('active');
        }

        function drawChart(item) {
            // Simple ASCII-style chart representation
            const canvas = document.getElementById('priceChart');
            if (!canvas) return;
            
            const ctx = canvas.getContext('2d');
            canvas.width = canvas.parentElement.clientWidth - 30;
            canvas.height = 170;
            
            const prices = [item.year, item.month, item.week, item.yesterday, item.current];
            const labels = ['Year Ago', 'Month Ago', 'Week Ago', 'Yesterday', 'Today'];
            const max = Math.max(...prices) * 1.2;
            const min = Math.min(...prices) * 0.8;
            const range = max - min;
            
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = '#667eea';
            ctx.fillStyle = '#667eea';
            ctx.lineWidth = 3;
            
            // Draw line
            ctx.beginPath();
            prices.forEach((price, i) => {
                const x = (canvas.width / (prices.length - 1)) * i;
                const y = canvas.height - ((price - min) / range * canvas.height);
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            });
            ctx.stroke();
            
            // Draw points
            prices.forEach((price, i) => {
                const x = (canvas.width / (prices.length - 1)) * i;
                const y = canvas.height - ((price - min) / range * canvas.height);
                ctx.beginPath();
                ctx.arc(x, y, 5, 0, Math.PI * 2);
                ctx.fill();
            });
        }

        // Close modal on outside click
        window.onclick = function(event) {
            const modal = document.getElementById('detailModal');
            if (event.target === modal) {
                closeModal();
            }
        }

        init();
