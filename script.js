// Search functionality
document.addEventListener('DOMContentLoaded', function() {
    const topBarSearch = document.getElementById('topBarSearch');
    const searchInput = topBarSearch ? topBarSearch.querySelector('.search-input') : null;
    
    if (topBarSearch && searchInput) {
        topBarSearch.addEventListener('click', function(e) {
            if (e.target === searchInput) return;
            this.classList.add('expanded');
            searchInput.focus();
        });
        
        searchInput.addEventListener('blur', function() {
            if (!this.value) {
                topBarSearch.classList.remove('expanded');
            }
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Update auth UI
    updateAuthUI();
});