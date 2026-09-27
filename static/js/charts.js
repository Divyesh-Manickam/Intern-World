/**
 * InternWorld Analytics & Chart.js Helpers
 */

function getChartColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
        text: isDark ? '#e8e2f8' : '#1e293b',
        grid: isDark ? '#2d2640' : '#f1f5f9',
        tooltipBg: isDark ? '#1a1625' : '#1e293b',
        tooltipBorder: isDark ? '#2d2640' : 'transparent',
        primary: isDark ? '#8b5cf6' : '#7c3aed',
        primaryBg: isDark ? 'rgba(139, 92, 246, 0.1)' : 'rgba(124, 58, 237, 0.08)',
        secondary: isDark ? '#a78bfa' : '#8b5cf6',
        accent: isDark ? '#22d3ee' : '#06b6d4',
        border: isDark ? '#2d2640' : '#ffffff'
    };
}

let activeCharts = {};

function registerChart(id, chartInstance) {
    if (activeCharts[id]) {
        activeCharts[id].destroy();
    }
    activeCharts[id] = chartInstance;
}

// Re-render charts when theme changes
window.addEventListener('themeChanged', () => {
    Object.values(activeCharts).forEach(chart => {
        const colors = getChartColors();
        
        // Update general options
        if (chart.options.scales && chart.options.scales.x) {
            chart.options.scales.x.ticks = chart.options.scales.x.ticks || {};
            chart.options.scales.x.ticks.color = colors.text;
            chart.options.scales.x.grid = chart.options.scales.x.grid || {};
            chart.options.scales.x.grid.color = colors.grid;
        }
        
        if (chart.options.scales && chart.options.scales.y) {
            chart.options.scales.y.ticks = chart.options.scales.y.ticks || {};
            chart.options.scales.y.ticks.color = colors.text;
            chart.options.scales.y.grid = chart.options.scales.y.grid || {};
            chart.options.scales.y.grid.color = colors.grid;
        }

        if (chart.options.plugins && chart.options.plugins.tooltip) {
            chart.options.plugins.tooltip.backgroundColor = colors.tooltipBg;
            chart.options.plugins.tooltip.borderColor = colors.tooltipBorder;
            chart.options.plugins.tooltip.borderWidth = 1;
        }
        
        if (chart.options.plugins && chart.options.plugins.legend) {
            chart.options.plugins.legend.labels = chart.options.plugins.legend.labels || {};
            chart.options.plugins.legend.labels.color = colors.text;
        }

        chart.update();
    });
});

function renderMonthlyApplicationsChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    const colors = getChartColors();

    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Applications Submitted',
                data: data,
                borderColor: colors.primary,
                backgroundColor: colors.primaryBg,
                fill: true,
                tension: 0.35,
                borderWidth: 2.5,
                pointBackgroundColor: colors.primary,
                pointRadius: 4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: colors.tooltipBg,
                    titleFont: { size: 13 },
                    bodyFont: { size: 12 },
                    padding: 10,
                    cornerRadius: 8,
                    borderColor: colors.tooltipBorder,
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0, stepSize: 1, color: colors.text },
                    grid: { color: colors.grid }
                },
                x: {
                    ticks: { color: colors.text },
                    grid: { display: false }
                }
            }
        }
    });
    
    registerChart(canvasId, chart);
}

function renderFunnelChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const colors = getChartColors();

    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Candidate Count',
                data: data,
                backgroundColor: [
                    '#3b82f6', // Applied
                    colors.accent, // Under Review
                    '#f59e0b', // Shortlisted
                    colors.primary, // Interview
                    '#10b981', // Selected
                    '#ef4444', // Rejected
                ],
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: colors.tooltipBg,
                    borderColor: colors.tooltipBorder,
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0, color: colors.text },
                    grid: { color: colors.grid }
                },
                x: {
                    ticks: { color: colors.text },
                    grid: { display: false }
                }
            }
        }
    });
    
    registerChart(canvasId, chart);
}

function renderPopularSkillsChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const colors = getChartColors();

    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    colors.primary, colors.accent, '#f59e0b', '#3b82f6',
                    colors.secondary, '#ec4899', '#10b981', '#64748b'
                ],
                borderWidth: 2,
                borderColor: colors.border
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { boxWidth: 12, padding: 12, color: colors.text }
                },
                tooltip: {
                    backgroundColor: colors.tooltipBg,
                    borderColor: colors.tooltipBorder,
                    borderWidth: 1
                }
            },
            cutout: '65%'
        }
    });
    
    registerChart(canvasId, chart);
}
