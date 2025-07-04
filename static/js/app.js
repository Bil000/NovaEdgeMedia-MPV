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
        
        this.init();
    }

    init() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        this.addInputValidation();
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
