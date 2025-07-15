// Stocker JavaScript - External Only
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Set up navigation
    setupNavigation();
    
    // Set up forms
    setupForms();
    
    // Set up specific page functionality
    const currentPage = getCurrentPage();
    
    switch(currentPage) {
        case 'index':
            setupHomePage();
            break;
        case 'login':
            setupLoginPage();
            break;
        case 'signup':
            setupSignupPage();
            break;
        case 'dashboard':
            setupDashboard();
            break;
        case 'trade':
            setupTradePage();
            break;
        case 'portfolio':
            setupPortfolioPage();
            break;
        case 'history':
            setupHistoryPage();
            break;
        case 'help':
            setupHelpPage();
            break;
        case 'admin_dashboard':
            setupAdminDashboard();
            break;
        case 'admin_portfolio':
            setupAdminPortfolioPage();
            break;
        case 'admin_history':
            setupAdminHistoryPage();
            break;
        case 'admin_manage':
            setupAdminManagePage();
            break;
    }
}

function getCurrentPage() {
    const path = window.location.pathname;
    if (path === '/' || path === '/index.html') return 'index';
    if (path.includes('login')) return 'login';
    if (path.includes('signup')) return 'signup';
    if (path.includes('dashboard')) return 'dashboard';
    if (path.includes('trade')) return 'trade';
    if (path.includes('portfolio')) return 'portfolio';
    if (path.includes('history')) return 'history';
    if (path.includes('help')) return 'help';
    if (path.includes('admin_dashboard')) return 'admin_dashboard';
    if (path.includes('admin_portfolio')) return 'admin_portfolio';
    if (path.includes('admin_history')) return 'admin_history';
    if (path.includes('admin_manage')) return 'admin_manage';
    return 'unknown';
}

function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-menu li');
    
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all items
            navItems.forEach(navItem => navItem.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Handle content switching
            const section = this.textContent.toLowerCase();
            switchContent(section);
        });
    });
}

function switchContent(section) {
    const contentSections = document.querySelectorAll('.content-section');
    
    contentSections.forEach(content => {
        content.classList.add('hidden');
    });
    
    const targetSection = document.getElementById(section + '-section');
    if (targetSection) {
        targetSection.classList.remove('hidden');
        targetSection.classList.add('fade-in');
    }
}

function setupForms() {
    // Password toggle functionality
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const passwordInput = this.previousElementSibling;
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                this.textContent = '👁️';
            } else {
                passwordInput.type = 'password';
                this.textContent = '👁️‍🗨️';
            }
        });
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            showError(input, 'This field is required');
            isValid = false;
        } else {
            clearError(input);
        }
        
        // Password validation
        if (input.type === 'password' && input.name === 'password') {
            if (!validatePassword(input.value)) {
                showError(input, 'Password must be at least 8 characters with 1 special character and 1 number');
                isValid = false;
            }
        }
    });
    
    return isValid;
}

function validatePassword(password) {
    const minLength = 8;
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    const hasNumber = /\d/.test(password);
    
    return password.length >= minLength && hasSpecialChar && hasNumber;
}

function showError(input, message) {
    clearError(input);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error';
    errorDiv.textContent = message;
    
    input.parentNode.appendChild(errorDiv);
    input.style.borderColor = '#f44336';
}

function clearError(input) {
    const errorDiv = input.parentNode.querySelector('.form-error');
    if (errorDiv) {
        errorDiv.remove();
    }
    input.style.borderColor = '#333';
}

function setupHomePage() {
    // Initialize home page content sections
    const sections = {
        'home': document.getElementById('home-section'),
        'about': document.getElementById('about-section'),
        'services': document.getElementById('services-section')
    };
    
    // Show home section by default
    Object.keys(sections).forEach(key => {
        if (sections[key]) {
            if (key === 'home') {
                sections[key].classList.remove('hidden');
            } else {
                sections[key].classList.add('hidden');
            }
        }
    });
    
    // Set up navigation
    const navItems = document.querySelectorAll('.nav-menu li');
    navItems.forEach(item => {
        if (item.textContent.toLowerCase() === 'home') {
            item.classList.add('active');
        }
    });
}

function setupLoginPage() {
    // Login form specific functionality
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const role = document.getElementById('role').value;
            
            if (!email || !password || !role) {
                e.preventDefault();
                alert('Please fill in all fields');
            }
        });
    }
}

function setupSignupPage() {
    // Username availability check
    const usernameInput = document.getElementById('username');
    if (usernameInput) {
        let checkTimeout;
        
        usernameInput.addEventListener('input', function() {
            const username = this.value.trim();
            
            clearTimeout(checkTimeout);
            checkTimeout = setTimeout(() => {
                if (username.length >= 3) {
                    checkUsernameAvailability(username);
                }
            }, 500);
        });
    }
    
    // Password strength indicator
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            showPasswordStrength(this.value);
        });
    }
}

function checkUsernameAvailability(username) {
    fetch(`/check_username/${username}`)
        .then(response => response.json())
        .then(data => {
            const usernameInput = document.getElementById('username');
            if (data.exists) {
                showError(usernameInput, 'Username already exists');
            } else {
                clearError(usernameInput);
                usernameInput.style.borderColor = '#4CAF50';
            }
        })
        .catch(error => {
            console.error('Error checking username:', error);
        });
}

function showPasswordStrength(password) {
    const strengthIndicator = document.getElementById('passwordStrength');
    if (!strengthIndicator) return;
    
    let strength = 0;
    let message = '';
    
    if (password.length >= 8) strength++;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[a-zA-Z]/.test(password)) strength++;
    
    switch(strength) {
        case 0:
        case 1:
            message = 'Weak';
            strengthIndicator.style.color = '#f44336';
            break;
        case 2:
            message = 'Fair';
            strengthIndicator.style.color = '#ff9800';
            break;
        case 3:
            message = 'Good';
            strengthIndicator.style.color = '#4CAF50';
            break;
        case 4:
            message = 'Strong';
            strengthIndicator.style.color = '#4CAF50';
            break;
    }
    
    strengthIndicator.textContent = message;
}

function setupDashboard() {
    // Load and display stock prices
    loadStockPrices();
    
    // Update prices every 10 seconds
    setInterval(loadStockPrices, 10000);
    
    // Set up buy/sell buttons
    setupTradingButtons();
}

function loadStockPrices() {
    fetch('/api/stock_prices')
        .then(response => response.json())
        .then(data => {
            displayStockPrices(data);
        })
        .catch(error => {
            console.error('Error loading stock prices:', error);
        });
}

function displayStockPrices(prices) {
    const stockGrid = document.getElementById('stockGrid');
    if (!stockGrid) return;
    
    stockGrid.innerHTML = '';
    
    Object.keys(prices).forEach(symbol => {
        const stock = prices[symbol];
        const stockCard = createStockCard(symbol, stock);
        stockGrid.appendChild(stockCard);
    });
}

function createStockCard(symbol, stock) {
    const card = document.createElement('div');
    card.className = 'stock-card slide-up';
    
    const changeClass = stock.change >= 0 ? 'positive' : 'negative';
    const changeSymbol = stock.change >= 0 ? '+' : '';
    
    card.innerHTML = `
        <div class="stock-header">
            <div>
                <div class="stock-symbol">${symbol}</div>
                <div class="stock-name">${stock.name}</div>
            </div>
            <div class="stock-price">$${stock.price}</div>
        </div>
        <div class="stock-change ${changeClass}">${changeSymbol}${stock.change}%</div>
        <div class="stock-actions">
            <button class="btn btn-primary" onclick="buyStock('${symbol}', ${stock.price})">Buy</button>
            <button class="btn btn-warning" onclick="sellStock('${symbol}', ${stock.price})">Sell</button>
        </div>
    `;
    
    return card;
}

function setupTradingButtons() {
    // Trading buttons are set up dynamically in createStockCard
}

function buyStock(symbol, price) {
    // Navigate to trade page with pre-filled data in same window
    window.location.assign(`/trade?symbol=${symbol}&price=${price}&type=buy`);
}

function sellStock(symbol, price) {
    // Navigate to trade page with pre-filled data in same window
    window.location.assign(`/trade?symbol=${symbol}&price=${price}&type=sell`);
}

function setupTradePage() {
    // Pre-fill form from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const symbol = urlParams.get('symbol');
    const price = urlParams.get('price');
    const type = urlParams.get('type');
    
    if (symbol && price && type) {
        const symbolSelect = document.getElementById('stock_symbol');
        const priceInput = document.getElementById('price');
        const typeSelect = document.getElementById('trade_type');
        
        if (symbolSelect) symbolSelect.value = symbol;
        if (priceInput) priceInput.value = price;
        if (typeSelect) typeSelect.value = type;
        
        updateTradeTotal();
    }
    
    // Set up real-time price updates
    loadStockPrices();
    setInterval(loadStockPrices, 10000);
    
    // Set up trade form
    setupTradeForm();
}

function setupTradeForm() {
    const tradeForm = document.getElementById('tradeForm');
    if (!tradeForm) return;
    
    // Update total when quantity or price changes
    const quantityInput = document.getElementById('quantity');
    const priceInput = document.getElementById('price');
    
    if (quantityInput) {
        quantityInput.addEventListener('input', updateTradeTotal);
    }
    
    if (priceInput) {
        priceInput.addEventListener('input', updateTradeTotal);
    }
    
    // Handle form submission
    tradeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        executeTrade();
    });
}

function updateTradeTotal() {
    const quantity = parseInt(document.getElementById('quantity').value) || 0;
    const price = parseFloat(document.getElementById('price').value) || 0;
    const total = quantity * price;
    
    const totalElement = document.getElementById('totalAmount');
    if (totalElement) {
        totalElement.textContent = `$${total.toFixed(2)}`;
    }
}

function executeTrade() {
    const formData = {
        stock_symbol: document.getElementById('stock_symbol').value,
        trade_type: document.getElementById('trade_type').value,
        quantity: parseInt(document.getElementById('quantity').value),
        price: parseFloat(document.getElementById('price').value)
    };
    
    fetch('/api/execute_trade', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Trade executed successfully!');
            // Reset form
            document.getElementById('tradeForm').reset();
            updateTradeTotal();
        } else {
            alert('Trade execution failed: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error executing trade:', error);
        alert('Trade execution failed');
    });
}

function setupPortfolioPage() {
    loadPortfolio();
    
    // Refresh portfolio every 30 seconds
    setInterval(loadPortfolio, 30000);
}

function loadPortfolio() {
    fetch('/api/portfolio')
        .then(response => response.json())
        .then(data => {
            displayPortfolio(data);
        })
        .catch(error => {
            console.error('Error loading portfolio:', error);
        });
}

function displayPortfolio(portfolio) {
    const portfolioTable = document.getElementById('portfolioTable');
    if (!portfolioTable) return;
    
    const tbody = portfolioTable.querySelector('tbody');
    tbody.innerHTML = '';
    
    let totalValue = 0;
    
    portfolio.forEach(item => {
        const row = document.createElement('tr');
        const profitLoss = item.total_value - (item.quantity * item.average_price);
        const profitLossClass = profitLoss >= 0 ? 'text-success' : 'text-danger';
        
        row.innerHTML = `
            <td>${item.symbol}</td>
            <td>${item.name}</td>
            <td>${item.quantity}</td>
            <td>$${item.average_price.toFixed(2)}</td>
            <td>$${item.current_price.toFixed(2)}</td>
            <td>$${item.total_value.toFixed(2)}</td>
            <td class="${profitLossClass}">$${profitLoss.toFixed(2)}</td>
            <td>${new Date(item.created_at).toLocaleDateString()}</td>
        `;
        
        tbody.appendChild(row);
        totalValue += item.total_value;
    });
    
    // Update total portfolio value
    const totalElement = document.getElementById('totalPortfolioValue');
    if (totalElement) {
        totalElement.textContent = `$${totalValue.toFixed(2)}`;
    }
}

function setupHistoryPage() {
    loadTradeHistory();
}

function loadTradeHistory() {
    fetch('/api/trade_history')
        .then(response => response.json())
        .then(data => {
            displayTradeHistory(data);
        })
        .catch(error => {
            console.error('Error loading trade history:', error);
        });
}

function displayTradeHistory(history) {
    const historyTable = document.getElementById('historyTable');
    if (!historyTable) return;
    
    const tbody = historyTable.querySelector('tbody');
    tbody.innerHTML = '';
    
    history.forEach(trade => {
        const row = document.createElement('tr');
        const typeClass = trade.trade_type === 'buy' ? 'text-success' : 'text-warning';
        
        row.innerHTML = `
            <td>${trade.symbol}</td>
            <td>${trade.name}</td>
            <td class="${typeClass}">${trade.trade_type.toUpperCase()}</td>
            <td>${trade.quantity}</td>
            <td>$${trade.price.toFixed(2)}</td>
            <td>$${trade.total_amount.toFixed(2)}</td>
            <td>${new Date(trade.created_at).toLocaleDateString()}</td>
        `;
        
        tbody.appendChild(row);
    });
}

function setupHelpPage() {
    // Set up FAQ toggles
    const faqQuestions = document.querySelectorAll('.faq-question');
    
    faqQuestions.forEach(question => {
        question.addEventListener('click', function() {
            const answer = this.nextElementSibling;
            const allAnswers = document.querySelectorAll('.faq-answer');
            
            // Close all other answers
            allAnswers.forEach(ans => {
                if (ans !== answer) {
                    ans.classList.remove('active');
                }
            });
            
            // Toggle current answer
            answer.classList.toggle('active');
        });
    });
}

// Admin Functions
function setupAdminDashboard() {
    loadAdminStats();
    
    // Refresh stats every 30 seconds
    setInterval(loadAdminStats, 30000);
}

function loadAdminStats() {
    fetch('/api/admin/stats')
        .then(response => response.json())
        .then(data => {
            displayAdminStats(data);
        })
        .catch(error => {
            console.error('Error loading admin stats:', error);
        });
}

function displayAdminStats(stats) {
    const totalTradersElement = document.getElementById('totalTraders');
    const totalTradesElement = document.getElementById('totalTrades');
    const totalValueElement = document.getElementById('totalPortfolioValue');
    
    if (totalTradersElement) totalTradersElement.textContent = stats.total_traders;
    if (totalTradesElement) totalTradesElement.textContent = stats.total_trades;
    if (totalValueElement) totalValueElement.textContent = `$${stats.total_portfolio_value.toFixed(2)}`;
}

function setupAdminPortfolioPage() {
    loadAdminPortfolios();
}

function loadAdminPortfolios() {
    fetch('/api/admin/all_portfolios')
        .then(response => response.json())
        .then(data => {
            displayAdminPortfolios(data);
        })
        .catch(error => {
            console.error('Error loading admin portfolios:', error);
        });
}

function displayAdminPortfolios(portfolios) {
    const portfolioTable = document.getElementById('adminPortfolioTable');
    if (!portfolioTable) return;
    
    const tbody = portfolioTable.querySelector('tbody');
    tbody.innerHTML = '';
    
    portfolios.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.username}</td>
            <td>${item.symbol}</td>
            <td>${item.name}</td>
            <td>${item.quantity}</td>
            <td>$${item.average_price.toFixed(2)}</td>
            <td>$${item.current_price.toFixed(2)}</td>
            <td>$${item.total_value.toFixed(2)}</td>
            <td>${new Date(item.created_at).toLocaleDateString()}</td>
        `;
        
        tbody.appendChild(row);
    });
}

function setupAdminHistoryPage() {
    loadAdminTradeHistory();
}

function loadAdminTradeHistory() {
    fetch('/api/admin/all_trades')
        .then(response => response.json())
        .then(data => {
            displayAdminTradeHistory(data);
        })
        .catch(error => {
            console.error('Error loading admin trade history:', error);
        });
}

function displayAdminTradeHistory(trades) {
    const historyTable = document.getElementById('adminHistoryTable');
    if (!historyTable) return;
    
    const tbody = historyTable.querySelector('tbody');
    tbody.innerHTML = '';
    
    trades.forEach(trade => {
        const row = document.createElement('tr');
        const typeClass = trade.trade_type === 'buy' ? 'text-success' : 'text-warning';
        
        row.innerHTML = `
            <td>${trade.username}</td>
            <td>${trade.symbol}</td>
            <td>${trade.name}</td>
            <td class="${typeClass}">${trade.trade_type.toUpperCase()}</td>
            <td>${trade.quantity}</td>
            <td>$${trade.price.toFixed(2)}</td>
            <td>$${trade.total_amount.toFixed(2)}</td>
            <td>${new Date(trade.created_at).toLocaleDateString()}</td>
        `;
        
        tbody.appendChild(row);
    });
}

function setupAdminManagePage() {
    loadAdminUsers();
    loadAdminMessages();
}

function loadAdminUsers() {
    fetch('/api/admin/users')
        .then(response => response.json())
        .then(data => {
            displayAdminUsers(data);
        })
        .catch(error => {
            console.error('Error loading admin users:', error);
        });
}

function displayAdminUsers(users) {
    const usersTable = document.getElementById('adminUsersTable');
    if (!usersTable) return;
    
    const tbody = usersTable.querySelector('tbody');
    tbody.innerHTML = '';
    
    users.forEach(user => {
        const row = document.createElement('tr');
        const roleClass = user.role === 'Admin' ? 'text-warning' : 'text-success';
        
        row.innerHTML = `
            <td>${user.username}</td>
            <td>${user.email}</td>
            <td class="${roleClass}">${user.role}</td>
            <td>${new Date(user.created_at).toLocaleDateString()}</td>
        `;
        
        tbody.appendChild(row);
    });
}

function loadAdminMessages() {
    fetch('/api/admin/messages')
        .then(response => response.json())
        .then(data => {
            displayAdminMessages(data);
        })
        .catch(error => {
            console.error('Error loading admin messages:', error);
        });
}

function displayAdminMessages(messages) {
    const messagesContainer = document.getElementById('adminMessages');
    if (!messagesContainer) return;
    
    messagesContainer.innerHTML = '';
    
    messages.forEach(message => {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message-item';
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="message-user">${message.username}</span>
                <span class="message-time">${new Date(message.created_at).toLocaleString()}</span>
            </div>
            <div class="message-content">${message.message}</div>
        `;
        
        messagesContainer.appendChild(messageDiv);
    });
}

// Utility Functions
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showNotification('An error occurred. Please try again.', 'error');
});

// Global unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    showNotification('An error occurred. Please try again.', 'error');
});