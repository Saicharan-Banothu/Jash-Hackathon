const API_BASE = 'http://localhost:5000/api';

// Check authentication status
function checkAuth() {
    const user = localStorage.getItem('user');
    if (user && window.location.pathname.includes('login.html')) {
        window.location.href = 'dashboard.html';
    } else if (!user && window.location.pathname.includes('dashboard.html')) {
        window.location.href = 'login.html';
    }
}

// Tab functionality
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    
    // Tab switching
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            
            // Update active tab button
            tabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Show corresponding tab content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${tabName}-tab`) {
                    content.classList.add('active');
                }
            });
        });
    });
    
    // Login form submission
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            
            try {
                const response = await fetch(`${API_BASE}/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password }),
                    credentials: 'include'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    localStorage.setItem('user', JSON.stringify(data.user));
                    window.location.href = 'dashboard.html';
                } else {
                    document.getElementById('loginError').textContent = data.error;
                }
            } catch (error) {
                console.error('Login error:', error);
                document.getElementById('loginError').textContent = 'Login failed. Please try again.';
            }
        });
    }
    
    // Register form submission
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const userData = {
                username: document.getElementById('regUsername').value,
                email: document.getElementById('regEmail').value,
                password: document.getElementById('regPassword').value,
                age: document.getElementById('regAge').value,
                gender: document.getElementById('regGender').value
            };
            
            try {
                const response = await fetch(`${API_BASE}/register`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(userData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Auto-login after registration
                    localStorage.setItem('user', JSON.stringify(data.user));
                    window.location.href = 'dashboard.html';
                } else {
                    document.getElementById('registerError').textContent = data.error;
                }
            } catch (error) {
                console.error('Registration error:', error);
                document.getElementById('registerError').textContent = 'Registration failed. Please try again.';
            }
        });
    }
    
    // Logout functionality
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async function() {
            try {
                await fetch(`${API_BASE}/logout`, {
                    method: 'POST',
                    credentials: 'include'
                });
                
                localStorage.removeItem('user');
                window.location.href = 'login.html';
            } catch (error) {
                console.error('Logout error:', error);
            }
        });
    }
    
    // Update UI based on login status
    updateAuthUI();
});

function updateAuthUI() {
    const user = JSON.parse(localStorage.getItem('user'));
    const loginBtn = document.getElementById('loginBtn');
    const profileBtn = document.getElementById('profileBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    
    if (user) {
        if (loginBtn) loginBtn.textContent = 'Logout';
        if (profileBtn) profileBtn.style.display = 'inline-block';
        if (logoutBtn) logoutBtn.style.display = 'inline-block';
        
        // Update welcome message
        const welcomeElement = document.getElementById('userWelcome');
        if (welcomeElement) {
            welcomeElement.textContent = `Welcome back, ${user.username}!`;
        }
    } else {
        if (loginBtn) loginBtn.textContent = 'Login';
        if (profileBtn) profileBtn.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'none';
    }
}