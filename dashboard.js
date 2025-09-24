document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user) {
        window.location.href = 'login.html';
        return;
    }
    
    // Initialize test results array
    let testResults = [];
    
    // Add test functionality
    document.querySelector('.add-test-btn').addEventListener('click', function() {
        const testType = document.querySelector('.test-type').value;
        const testValue = document.querySelector('.test-value').value;
        
        if (testType && testValue) {
            testResults.push({ test: testType, value: testValue });
            updateTestResultsList();
            
            // Clear inputs
            document.querySelector('.test-type').value = '';
            document.querySelector('.test-value').value = '';
        }
    });
    
    // Analysis form submission
    document.getElementById('analysisForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const reportName = document.getElementById('reportName').value;
        
        if (testResults.length === 0) {
            alert('Please add at least one test result');
            return;
        }
        
        // Convert test results to object format
        const testData = {};
        testResults.forEach(item => {
            testData[item.test] = item.value;
        });
        
        try {
            const response = await fetch(`${API_BASE}/analyze-report`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    report_name: reportName,
                    test_results: testData
                }),
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (data.success) {
                displayAnalysisResult(data.analysis);
                loadReportHistory(); // Refresh history
            } else {
                alert('Analysis failed: ' + data.error);
            }
        } catch (error) {
            console.error('Analysis error:', error);
            alert('Analysis failed. Please try again.');
        }
    });
    
    // Load report history
    loadReportHistory();
});

function updateTestResultsList() {
    const container = document.getElementById('testResults');
    container.innerHTML = '';
    
    testResults.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'test-item';
        div.innerHTML = `
            <span>${item.test}: ${item.value}</span>
            <span class="remove-test" onclick="removeTest(${index})">
                <i class="fas fa-times"></i>
            </span>
        `;
        container.appendChild(div);
    });
}

function removeTest(index) {
    testResults.splice(index, 1);
    updateTestResultsList();
}

function displayAnalysisResult(analysis) {
    const resultDiv = document.getElementById('analysisResult');
    const conditionElement = document.getElementById('resultCondition');
    const confidenceElement = document.getElementById('resultConfidence');
    const analysisElement = document.getElementById('resultAnalysis');
    const recommendationsElement = document.getElementById('resultRecommendations');
    
    conditionElement.textContent = analysis.condition;
    confidenceElement.textContent = analysis.confidence + '%';
    analysisElement.textContent = analysis.analysis;
    recommendationsElement.textContent = analysis.recommendations;
    
    resultDiv.style.display = 'block';
    
    // Scroll to results
    resultDiv.scrollIntoView({ behavior: 'smooth' });
}

async function loadReportHistory() {
    try {
        const response = await fetch(`${API_BASE}/report-history`, {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        const historyList = document.getElementById('historyList');
        
        if (data.success && data.reports.length > 0) {
            historyList.innerHTML = data.reports.map(report => `
                <div class="history-item">
                    <div class="history-header">
                        <h4>${report.report_name}</h4>
                        <span class="history-date">${new Date(report.timestamp).toLocaleDateString()}</span>
                    </div>
                    <div class="test-data">
                        <strong>Tests:</strong> ${Object.keys(report.test_data).join(', ')}
                    </div>
                    <div class="analysis-preview">
                        ${report.analysis_result.substring(0, 100)}...
                    </div>
                </div>
            `).join('');
        } else {
            historyList.innerHTML = '<div class="loading">No reports yet. Analyze your first report above!</div>';
        }
    } catch (error) {
        console.error('Error loading history:', error);
        document.getElementById('historyList').innerHTML = '<div class="loading">Error loading history</div>';
    }
}