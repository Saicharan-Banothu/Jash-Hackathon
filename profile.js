document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user) {
        window.location.href = 'login.html';
        return;
    }
    
    // Load profile data
    loadProfileData();
    loadRecentReports();
    
    // Profile form submission
    document.getElementById('profileForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const updateData = {
            age: document.getElementById('profileAge').value,
            gender: document.getElementById('profileGender').value
        };
        
        try {
            const response = await fetch(`${API_BASE}/update-profile`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updateData),
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (data.success) {
                document.getElementById('profileMessage').textContent = 'Profile updated successfully!';
                document.getElementById('profileMessage').style.color = 'green';
                
                // Update local storage
                const user = JSON.parse(localStorage.getItem('user'));
                user.age = updateData.age;
                user.gender = updateData.gender;
                localStorage.setItem('user', JSON.stringify(user));
            } else {
                document.getElementById('profileMessage').textContent = data.error;
            }
        } catch (error) {
            console.error('Profile update error:', error);
            document.getElementById('profileMessage').textContent = 'Update failed. Please try again.';
        }
    });
});

async function loadProfileData() {
    try {
        const response = await fetch(`${API_BASE}/user-profile`, {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            const user = data.user;
            document.getElementById('profileUsername').textContent = user.username;
            document.getElementById('profileEmail').textContent = user.email;
            document.getElementById('profileAge').value = user.age || '';
            document.getElementById('profileGender').value = user.gender || '';
            
            // Format join date
            const joinDate = new Date(user.joined_date);
            document.getElementById('memberSince').textContent = joinDate.getFullYear();
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

async function loadRecentReports() {
    try {
        const response = await fetch(`${API_BASE}/report-history`, {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        const recentReports = document.getElementById('recentReports');
        document.getElementById('totalReports').textContent = data.reports ? data.reports.length : 0;
        
        if (data.success && data.reports.length > 0) {
            // Show only last 5 reports
            const recent = data.reports.slice(0, 5);
            
            recentReports.innerHTML = recent.map(report => `
                <div class="history-item">
                    <div class="history-header">
                        <h4>${report.report_name}</h4>
                        <span class="history-date">${new Date(report.timestamp).toLocaleDateString()}</span>
                    </div>
                    <div class="analysis-preview">
                        ${report.analysis_result.substring(0, 150)}...
                    </div>
                </div>
            `).join('');
        } else {
            recentReports.innerHTML = '<div class="loading">No reports yet. Analyze your first report on the dashboard!</div>';
        }
    } catch (error) {
        console.error('Error loading recent reports:', error);
        recentReports.innerHTML = '<div class="loading">Error loading reports</div>';
    }
}