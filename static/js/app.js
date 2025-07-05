// NovaEdge Media - AI Marketing Assistant JavaScript

class MarketingAssistant {
    constructor() {
        this.form = document.getElementById('campaignForm');
        this.submitBtn = this.form.querySelector('button[type="submit"]');
        this.btnText = this.submitBtn.querySelector('.btn-text');
        this.btnLoading = this.submitBtn.querySelector('.btn-loading');
        
        this.welcomeState = document.getElementById('welcomeState');
        this.loadingState = document.getElementById('loadingState');
        this.errorState = document.getElementById('errorState');
        this.reportContent = document.getElementById('reportContent');
        
        // Integration elements
        this.connectionStatus = {};
        this.googleCredentialsForm = document.getElementById('googleCredentialsForm');
        this.metaCredentialsForm = document.getElementById('metaCredentialsForm');
        
        this.init();
    }

    init() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        this.addInputValidation();
        this.initializeIntegrations();
    }

    addInputValidation() {
        const inputs = this.form.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', this.validateField.bind(this));
            input.addEventListener('input', this.clearFieldError.bind(this));
        });
    }

    validateField(event) {
        const field = event.target;
        const value = field.value.trim();
        
        // Remove existing error styling
        field.classList.remove('is-invalid');
        
        // Validate required fields
        if (field.hasAttribute('required') && !value) {
            this.showFieldError(field, 'This field is required');
            return false;
        }

        // Validate specific field types
        switch (field.name) {
            case 'budget':
                if (value && (isNaN(value) || parseFloat(value) <= 0)) {
                    this.showFieldError(field, 'Budget must be a positive number');
                    return false;
                }
                break;
            case 'duration':
                if (value && (isNaN(value) || parseInt(value) <= 0)) {
                    this.showFieldError(field, 'Duration must be a positive number');
                    return false;
                }
                break;
        }

        return true;
    }

    showFieldError(field, message) {
        field.classList.add('is-invalid');
        
        // Remove existing error message
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    clearFieldError(event) {
        const field = event.target;
        field.classList.remove('is-invalid');
        const errorMsg = field.parentNode.querySelector('.invalid-feedback');
        if (errorMsg) {
            errorMsg.remove();
        }
    }

    async handleSubmit(event) {
        event.preventDefault();

        // Validate all fields
        const inputs = this.form.querySelectorAll('input[required], textarea[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateField({ target: input })) {
                isValid = false;
            }
        });

        if (!isValid) {
            this.showError('Please fix the validation errors before submitting.');
            return;
        }

        // Collect form data
        const formData = new FormData(this.form);
        const data = Object.fromEntries(formData.entries());

        // Convert numeric fields
        data.budget = parseFloat(data.budget) || 0;
        data.duration = parseInt(data.duration) || 0;

        try {
            this.showLoading();
            const report = await this.generateReport(data);
            this.showReport(report);
        } catch (error) {
            console.error('Error generating report:', error);
            this.showError(error.message || 'Failed to generate report. Please try again.');
        }
    }

    async generateReport(data) {
        const response = await fetch('/generate-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Unknown error occurred');
        }

        return result.report;
    }

    showLoading() {
        this.setButtonLoading(true);
        this.hideAllStates();
        this.loadingState.classList.remove('d-none');
        this.loadingState.classList.add('fade-in');
    }

    showError(message) {
        this.setButtonLoading(false);
        this.hideAllStates();
        document.getElementById('errorMessage').textContent = message;
        this.errorState.classList.remove('d-none');
        this.errorState.classList.add('fade-in');
    }

    showReport(report) {
        this.setButtonLoading(false);
        this.hideAllStates();
        this.renderReport(report);
        this.reportContent.classList.remove('d-none');
        this.reportContent.classList.add('fade-in');
    }

    renderReport(report) {
        const metadata = report.campaign_metadata || {};
        
        const html = `
            <div class="report-header">
                <h3 class="report-title">
                    <i class="fas fa-chart-line me-2"></i>
                    Marketing Analysis Report
                </h3>
                <p class="report-subtitle">
                    Campaign: ${metadata.campaign_name || 'N/A'} | 
                    Budget: ${metadata.budget || 'N/A'} | 
                    Duration: ${metadata.duration || 'N/A'}
                </p>
            </div>

            ${this.renderSection('Executive Summary', report.executive_summary, 'fas fa-chart-bar')}
            
            ${this.renderBudgetAnalysis(report.budget_analysis)}
            
            ${this.renderAudienceInsights(report.audience_insights)}
            
            ${this.renderRecommendations('Strategy Recommendations', report.strategy_recommendations, 'fas fa-lightbulb')}
            
            ${this.renderChannelOptimization(report.channel_optimization)}
            
            ${this.renderKPIFramework(report.kpi_framework)}
            
            ${this.renderRiskAssessment(report.risk_assessment)}
            
            ${this.renderRecommendations('Next Steps', report.next_steps, 'fas fa-arrow-right')}
        `;

        this.reportContent.innerHTML = html;
    }

    renderSection(title, content, icon = 'fas fa-info-circle') {
        if (!content) return '';
        
        return `
            <div class="report-section">
                <h4><i class="${icon}"></i> ${title}</h4>
                <p>${content}</p>
            </div>
        `;
    }

    renderBudgetAnalysis(budgetData) {
        if (!budgetData) return '';

        return `
            <div class="report-section">
                <h4><i class="fas fa-dollar-sign"></i> Budget Analysis</h4>
                <div class="metric-grid">
                    ${budgetData.daily_budget ? `
                        <div class="metric-item">
                            <div class="metric-label">Daily Budget</div>
                            <div class="metric-value">${budgetData.daily_budget}</div>
                        </div>
                    ` : ''}
                    ${budgetData.channel_distribution ? `
                        <div class="metric-item">
                            <div class="metric-label">Channel Distribution</div>
                            <div class="metric-value">${budgetData.channel_distribution}</div>
                        </div>
                    ` : ''}
                    ${budgetData.roi_projection ? `
                        <div class="metric-item">
                            <div class="metric-label">ROI Projection</div>
                            <div class="metric-value">${budgetData.roi_projection}</div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    renderAudienceInsights(audienceData) {
        if (!audienceData) return '';

        return `
            <div class="report-section">
                <h4><i class="fas fa-users"></i> Audience Insights</h4>
                ${audienceData.demographics ? `<p><strong>Demographics:</strong> ${audienceData.demographics}</p>` : ''}
                ${audienceData.behaviors ? `<p><strong>Behaviors:</strong> ${audienceData.behaviors}</p>` : ''}
                ${audienceData.pain_points ? `<p><strong>Pain Points:</strong> ${audienceData.pain_points}</p>` : ''}
            </div>
        `;
    }

    renderRecommendations(title, recommendations, icon) {
        if (!recommendations || !Array.isArray(recommendations)) return '';

        const listItems = recommendations.map(item => `<li>${item}</li>`).join('');
        
        return `
            <div class="report-section">
                <h4><i class="${icon}"></i> ${title}</h4>
                <ul>${listItems}</ul>
            </div>
        `;
    }

    renderChannelOptimization(channelData) {
        if (!channelData) return '';

        return `
            <div class="report-section">
                <h4><i class="fas fa-broadcast-tower"></i> Channel Optimization</h4>
                ${channelData.primary_channels ? `<p><strong>Primary Channels:</strong> ${channelData.primary_channels}</p>` : ''}
                ${channelData.content_strategy ? `<p><strong>Content Strategy:</strong> ${channelData.content_strategy}</p>` : ''}
                ${channelData.timing_recommendations ? `<p><strong>Timing:</strong> ${channelData.timing_recommendations}</p>` : ''}
            </div>
        `;
    }

    renderKPIFramework(kpiData) {
        if (!kpiData) return '';

        return `
            <div class="report-section">
                <h4><i class="fas fa-chart-pie"></i> KPI Framework</h4>
                ${kpiData.primary_metrics ? `<p><strong>Primary Metrics:</strong> ${kpiData.primary_metrics}</p>` : ''}
                ${kpiData.success_benchmarks ? `<p><strong>Success Benchmarks:</strong> ${kpiData.success_benchmarks}</p>` : ''}
                ${kpiData.monitoring_frequency ? `<p><strong>Monitoring Frequency:</strong> ${kpiData.monitoring_frequency}</p>` : ''}
            </div>
        `;
    }

    renderRiskAssessment(riskData) {
        if (!riskData) return '';

        return `
            <div class="report-section">
                <h4><i class="fas fa-shield-alt"></i> Risk Assessment</h4>
                ${riskData.potential_challenges ? `<p><strong>Potential Challenges:</strong> ${riskData.potential_challenges}</p>` : ''}
                ${riskData.mitigation_strategies ? `<p><strong>Mitigation Strategies:</strong> ${riskData.mitigation_strategies}</p>` : ''}
            </div>
        `;
    }

    setButtonLoading(loading) {
        if (loading) {
            this.submitBtn.disabled = true;
            this.btnText.classList.add('d-none');
            this.btnLoading.classList.remove('d-none');
        } else {
            this.submitBtn.disabled = false;
            this.btnText.classList.remove('d-none');
            this.btnLoading.classList.add('d-none');
        }
    }

    hideAllStates() {
        [this.welcomeState, this.loadingState, this.errorState, this.reportContent].forEach(element => {
            element.classList.add('d-none');
            element.classList.remove('fade-in');
        });
    }

    // Integration Management Methods
    initializeIntegrations() {
        // Check connection status on page load
        this.checkConnectionStatus();
        
        // Set up integration form handlers
        if (this.googleCredentialsForm) {
            this.googleCredentialsForm.addEventListener('submit', this.handleGoogleCredentials.bind(this));
        }
        
        if (this.metaCredentialsForm) {
            this.metaCredentialsForm.addEventListener('submit', this.handleMetaCredentials.bind(this));
        }

        // Set up tab change handler to refresh status
        const integrationsTab = document.getElementById('integrations-tab');
        if (integrationsTab) {
            integrationsTab.addEventListener('shown.bs.tab', () => {
                this.checkConnectionStatus();
            });
        }
    }

    async checkConnectionStatus() {
        try {
            const response = await fetch('/ads/status');
            const data = await response.json();
            
            if (data.success) {
                this.connectionStatus = data.status;
                this.updateConnectionUI();
            }
        } catch (error) {
            console.error('Failed to check connection status:', error);
        }
    }

    updateConnectionUI() {
        // Update Google Ads status
        const googleStatus = document.getElementById('googleAdsStatus');
        if (googleStatus) {
            const isConnected = this.connectionStatus.google_ads?.connected || false;
            this.updateStatusBadge(googleStatus, isConnected, 'Google Ads');
            
            // Hide/show form based on connection status
            const googleForm = document.getElementById('googleAdsForm');
            if (googleForm) {
                googleForm.style.display = isConnected ? 'none' : 'block';
            }
        }

        // Update Meta Ads status
        const metaStatus = document.getElementById('metaAdsStatus');
        if (metaStatus) {
            const isConnected = this.connectionStatus.meta_ads?.connected || false;
            this.updateStatusBadge(metaStatus, isConnected, 'Meta Ads');
            
            // Hide/show form based on connection status
            const metaForm = document.getElementById('metaAdsForm');
            if (metaForm) {
                metaForm.style.display = isConnected ? 'none' : 'block';
            }
        }

        // Update overall status message
        this.updateOverallStatus();
    }

    updateStatusBadge(container, isConnected, platformName) {
        const badge = container.querySelector('.status-badge');
        if (badge) {
            badge.className = `status-badge ${isConnected ? 'status-connected' : 'status-disconnected'}`;
            badge.innerHTML = isConnected 
                ? `<i class="fas fa-check-circle me-1"></i>Connected`
                : `<i class="fas fa-times-circle me-1"></i>Disconnected`;
        }
    }

    updateOverallStatus() {
        const statusDiv = document.getElementById('connectionStatus');
        if (!statusDiv) return;

        const totalConnected = this.connectionStatus.total_connected || 0;
        const connectedPlatforms = this.connectionStatus.connected_platforms || [];

        if (totalConnected === 0) {
            statusDiv.innerHTML = `
                <div class="alert alert-warning mb-0">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    No advertising platforms connected. Add your credentials below to unlock data-driven insights.
                </div>
            `;
        } else {
            const platformList = connectedPlatforms.map(p => p.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())).join(', ');
            statusDiv.innerHTML = `
                <div class="alert alert-success mb-0">
                    <i class="fas fa-check-circle me-2"></i>
                    Connected to ${totalConnected} platform${totalConnected > 1 ? 's' : ''}: ${platformList}
                </div>
            `;
        }
    }

    async handleGoogleCredentials(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        
        // Update status to testing
        const googleStatus = document.getElementById('googleAdsStatus');
        this.updateStatusBadge(googleStatus, null, 'Google Ads', 'testing');
        
        try {
            const response = await fetch('/credentials/google-ads', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(Object.fromEntries(formData))
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Clear form
                event.target.reset();
                // Refresh status
                await this.checkConnectionStatus();
                this.showCredentialSuccess('Google Ads connected successfully!');
            } else {
                this.showCredentialError(result.error || 'Failed to connect Google Ads');
                this.updateStatusBadge(googleStatus, false, 'Google Ads');
            }
        } catch (error) {
            this.showCredentialError('Network error connecting to Google Ads');
            this.updateStatusBadge(googleStatus, false, 'Google Ads');
        }
    }

    async handleMetaCredentials(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        
        // Update status to testing
        const metaStatus = document.getElementById('metaAdsStatus');
        this.updateStatusBadge(metaStatus, null, 'Meta Ads', 'testing');
        
        try {
            const response = await fetch('/credentials/meta-ads', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(Object.fromEntries(formData))
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Clear form
                event.target.reset();
                // Refresh status
                await this.checkConnectionStatus();
                this.showCredentialSuccess('Meta Ads connected successfully!');
            } else {
                this.showCredentialError(result.error || 'Failed to connect Meta Ads');
                this.updateStatusBadge(metaStatus, false, 'Meta Ads');
            }
        } catch (error) {
            this.showCredentialError('Network error connecting to Meta Ads');
            this.updateStatusBadge(metaStatus, false, 'Meta Ads');
        }
    }

    showCredentialSuccess(message) {
        // You can implement a toast notification or alert here
        alert(message);
    }

    showCredentialError(message) {
        // You can implement a toast notification or alert here
        alert('Error: ' + message);
    }
}

// Global functions for credential testing
async function testGoogleConnection() {
    try {
        const response = await fetch('/credentials/google-ads/test', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            alert('Google Ads connection test successful!');
        } else {
            alert('Google Ads connection test failed: ' + (result.error || 'Unknown error'));
        }
    } catch (error) {
        alert('Network error testing Google Ads connection');
    }
}

async function testMetaConnection() {
    try {
        const response = await fetch('/credentials/meta-ads/test', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            alert('Meta Ads connection test successful!');
        } else {
            alert('Meta Ads connection test failed: ' + (result.error || 'Unknown error'));
        }
    } catch (error) {
        alert('Network error testing Meta Ads connection');
    }
}

// Global function for error state reset
function resetToWelcome() {
    const assistant = window.marketingAssistant;
    if (assistant) {
        assistant.hideAllStates();
        assistant.welcomeState.classList.remove('d-none');
        assistant.welcomeState.classList.add('fade-in');
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.marketingAssistant = new MarketingAssistant();
});
