// 全局变量
let charts = {};
let filterOptions = {};
let selectedTargetings = [];

// 检查 Chart.js 是否已加载
function checkChartJS() {
    if (typeof Chart === 'undefined') {
        console.error('Chart.js 未加载，请检查 static/js/chart.umd.min.js 文件是否存在');
        alert('图表库加载失败，请检查应用文件是否完整。如果问题持续，请联系技术支持。');
        return false;
    }
    return true;
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    // 等待 Chart.js 加载完成
    if (typeof Chart === 'undefined') {
        // 如果 Chart.js 未加载，等待一段时间后重试
        setTimeout(function() {
            if (!checkChartJS()) {
                return;
            }
            loadFilterOptions();
            loadStatistics();
        }, 500);
    } else {
        loadFilterOptions();
        loadStatistics();
    }
});

// 加载筛选选项
async function loadFilterOptions() {
    try {
        const response = await fetch('/api/options');
        const result = await response.json();
        
        if (result.success) {
            filterOptions = result.options;
            populateFilters();
        }
    } catch (error) {
        console.error('加载筛选选项失败:', error);
    }
}

// 填充筛选器下拉框
function populateFilters() {
    // 填充代理商选项
    const agentSelect = document.getElementById('agent');
    if (filterOptions.agents && filterOptions.agents.length > 0) {
        filterOptions.agents.forEach(agent => {
            const option = document.createElement('option');
            option.value = agent;
            option.textContent = agent;
            agentSelect.appendChild(option);
        });
    }
    
    // 填充出价方式选项
    const biddingSelect = document.getElementById('bidding_method');
    if (filterOptions.bidding_methods && filterOptions.bidding_methods.length > 0) {
        filterOptions.bidding_methods.forEach(method => {
            const option = document.createElement('option');
            option.value = method;
            option.textContent = method;
            biddingSelect.appendChild(option);
        });
    }
    
    // 定向选项用于弹窗
    if (filterOptions.targetings && filterOptions.targetings.length > 0) {
        selectedTargetings = selectedTargetings.filter(value => filterOptions.targetings.includes(value));
        renderTargetingOptions();
    } else {
        selectedTargetings = [];
    }
    updateTargetingSummary();
    
    // 填充资源位选项
    const resourceSelect = document.getElementById('resource');
    if (filterOptions.resources && filterOptions.resources.length > 0) {
        filterOptions.resources.forEach(resource => {
            const option = document.createElement('option');
            option.value = resource;
            option.textContent = resource;
            resourceSelect.appendChild(option);
        });
    }
    
    // 填充素材样式选项
    const materialSelect = document.getElementById('material');
    if (filterOptions.materials && filterOptions.materials.length > 0) {
        filterOptions.materials.forEach(material => {
            const option = document.createElement('option');
            option.value = material;
            option.textContent = material;
            materialSelect.appendChild(option);
        });
    }

    // 填充利益点选项
    const benefitSelect = document.getElementById('benefit');
    if (filterOptions.benefits && filterOptions.benefits.length > 0) {
        filterOptions.benefits.forEach(benefit => {
            const option = document.createElement('option');
            option.value = benefit;
            option.textContent = benefit;
            benefitSelect.appendChild(option);
        });
    }
    
    // 设置日期范围
    if (filterOptions.dates && filterOptions.dates.length > 0) {
        const sortedDates = filterOptions.dates.sort();
        document.getElementById('date_from').value = sortedDates[0];
        document.getElementById('date_to').value = sortedDates[sortedDates.length - 1];
    }
}

// 应用筛选器
function applyFilters() {
    loadStatistics();
}

// 获取筛选参数
function getFilterParams() {
    return {
        date_from: document.getElementById('date_from').value || '',
        date_to: document.getElementById('date_to').value || '',
        agent: document.getElementById('agent').value || 'all',
        bidding_method: document.getElementById('bidding_method').value || 'all',
        targeting: selectedTargetings.join(','),
        resource: document.getElementById('resource').value || 'all',
        material: document.getElementById('material').value || 'all',
        benefit: document.getElementById('benefit').value || 'all'
    };
}

// 加载统计数据
async function loadStatistics() {
    const loadingEl = document.getElementById('loading');
    loadingEl.classList.remove('hidden');
    
    try {
        const params = getFilterParams();
        const queryString = new URLSearchParams(params).toString();
        const response = await fetch(`/api/statistics?${queryString}`);
        const result = await response.json();
        
        if (result.success) {
            updateMetrics(result);
            updateCharts(result);
        } else {
            alert('加载数据失败：' + result.message);
        }
    } catch (error) {
        console.error('加载统计数据失败:', error);
        alert('加载数据失败，请重试');
    } finally {
        loadingEl.classList.add('hidden');
    }
}

// 更新指标卡片
function updateMetrics(data) {
    // 格式化数字（统一为两行显示）
    function formatNumber(num) {
        const n = Number(num) || 0;
        if (n >= 100000000) {
            return (n / 100000000).toFixed(2) + '<br><span style="font-size: 0.5em;">亿</span>';
        } else if (n >= 10000) {
            return (n / 10000).toFixed(2) + '<br><span style="font-size: 0.5em;">万</span>';
        }
        return n.toLocaleString('zh-CN', { maximumFractionDigits: 2 });
    }
    
    function formatCurrency(num) {
        const n = Number(num) || 0;
        if (n >= 100000000) {
            return (n / 100000000).toFixed(2) + '<br><span style="font-size: 0.5em;">亿元</span>';
        } else if (n >= 10000) {
            return (n / 10000).toFixed(2) + '<br><span style="font-size: 0.5em;">万元</span>';
        }
        return n.toLocaleString('zh-CN', { maximumFractionDigits: 2 }) + '<br><span style="font-size: 0.5em;">元</span>';
    }

    function formatPercentValue(num) {
        const n = Number(num) || 0;
        return n.toFixed(2) + '<br><span style="font-size: 0.5em;">%</span>';
    }
    
    // 更新总指标
    document.getElementById('total_spend').innerHTML = formatCurrency(data.total_spend || 0);
    document.getElementById('total_settlement').innerHTML = formatCurrency(data.total_settlement || 0);
    
    // 计算总曝光、点击等（从每日数据汇总）
    let totalImpressions = 0;
    let totalClicks = 0;
    let totalDownloads = 0;
    
    if (data.daily_stats) {
        data.daily_stats.forEach(day => {
            totalImpressions += day.曝光量 || 0;
            totalClicks += day.点击量 || 0;
            totalDownloads += day.下载量 || 0;
        });
    }
    
    document.getElementById('total_impressions').innerHTML = formatNumber(totalImpressions);
    document.getElementById('total_clicks').innerHTML = formatNumber(totalClicks);
    document.getElementById('total_downloads').innerHTML = formatNumber(totalDownloads);
    
    // 更新转化数据
    document.getElementById('total_register').innerHTML = formatNumber(data.total_register || 0);
    document.getElementById('total_entry').innerHTML = formatNumber(data.total_entry || 0);
    document.getElementById('total_credit').innerHTML = formatNumber(data.total_credit || 0);
    document.getElementById('total_loan').innerHTML = formatNumber(data.total_loan || 0);
    document.getElementById('total_loan_orders').innerHTML = formatNumber(data.total_loan_orders || 0);
    document.getElementById('total_loan_amount').innerHTML = formatCurrency(data.total_loan_amount || 0);
    document.getElementById('total_credit_amount').innerHTML = formatCurrency(data.total_credit_amount || 0);
    document.getElementById('avg_credit_amount').innerHTML = formatCurrency(data.avg_credit_amount || 0);
    document.getElementById('avg_loan_per_order').innerHTML = formatCurrency(data.avg_loan_per_order || 0);
    document.getElementById('avg_exec_rate').innerHTML = formatPercentValue(data.avg_exec_rate || 0);
    
    // 更新成本指标
    const costMetrics = data.cost_metrics || {};
    document.getElementById('download_cost').innerHTML = formatCurrency(costMetrics.下载成本 || 0);
    document.getElementById('register_cost').innerHTML = formatCurrency(costMetrics.注册成本 || 0);
    document.getElementById('entry_cost').innerHTML = formatCurrency(costMetrics.进件成本 || 0);
    document.getElementById('credit_cost').innerHTML = formatCurrency(costMetrics.授信成本 || 0);
    document.getElementById('loan_cost').innerHTML = formatCurrency(costMetrics.支用成本 || 0);
}

// 更新图表
function updateCharts(data) {
    if (!checkChartJS()) {
        return;
    }
    updateDailySpendChart(data.daily_stats || []);
    updateDailyTrafficChart(data.daily_stats || []);
    updateAgentSpendChart(data.agent_stats || [], data.agent_bidding_mix || []);
    updateBiddingMethodChart(data.bidding_stats || []);
    updateTargetingSpendChart(data.targeting_spend || []);
    updateResourceSpendChart(data.resource_spend || []);
    updateRateTrendChart(data.rate_trend || []);
}

// 每日花费趋势图
function updateDailySpendChart(dailyStats) {
    const ctx = document.getElementById('dailySpendChart').getContext('2d');
    const labels = dailyStats.map(d => d.时间).sort();
    const spendData = labels.map(date => {
        const day = dailyStats.find(d => d.时间 === date);
        return day ? (day.花费 || 0) : 0;
    });
    const settlementData = labels.map(date => {
        const day = dailyStats.find(d => d.时间 === date);
        return day ? (day.结算花费 || 0) : 0;
    });
    
    if (charts.dailySpend) {
        charts.dailySpend.destroy();
    }
    
    charts.dailySpend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '花费（元）',
                data: spendData,
                borderColor: 'rgb(102, 126, 234)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: '结算花费（元）',
                data: settlementData,
                borderColor: 'rgb(255, 159, 64)',
                backgroundColor: 'rgba(255, 159, 64, 0.1)',
                tension: 0.4,
                fill: false,
                borderDash: [6, 6]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value >= 10000 ? (value / 10000).toFixed(1) + '万' : value;
                        }
                    }
                }
            }
        }
    });
}

// 每日曝光/点击趋势图
function updateDailyTrafficChart(dailyStats) {
    const ctx = document.getElementById('dailyTrafficChart').getContext('2d');
    const labels = dailyStats.map(d => d.时间).sort();
    const impressionsData = labels.map(date => {
        const day = dailyStats.find(d => d.时间 === date);
        return day ? (day.曝光量 || 0) : 0;
    });
    const clicksData = labels.map(date => {
        const day = dailyStats.find(d => d.时间 === date);
        return day ? (day.点击量 || 0) : 0;
    });
    
    if (charts.dailyTraffic) {
        charts.dailyTraffic.destroy();
    }
    
    charts.dailyTraffic = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '曝光量',
                data: impressionsData,
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                yAxisID: 'y',
                tension: 0.4
            }, {
                label: '点击量',
                data: clicksData,
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                yAxisID: 'y1',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    beginAtZero: true,
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            }
        }
    });
}

// 代理商花费对比图（堆叠显示出价方式）
function updateAgentSpendChart(agentStats, agentMix) {
    const ctx = document.getElementById('agentSpendChart').getContext('2d');
    const labels = agentStats.length > 0
        ? agentStats.map(a => a.代理商来源)
        : Array.from(new Set(agentMix.map(item => item.代理商来源)));
    
    const categories = ['OCPC', 'CPC', 'OTHER'];
    const datasets = categories.map((category, index) => {
        const colors = [
            'rgba(102, 126, 234, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(200, 200, 200, 0.6)'
        ];
        return {
            label: category === 'OTHER' ? '其他' : category,
            data: labels.map(agent => {
                const record = agentMix.find(item => item.代理商来源 === agent && item.出价类别 === category);
                return record ? (record.花费 || 0) : 0;
            }),
            backgroundColor: colors[index],
            stack: 'bidding'
        };
    }).filter(dataset => dataset.data.some(value => value > 0));
    
    if (charts.agentSpend) {
        charts.agentSpend.destroy();
    }
    
    if (datasets.length === 0) {
        return;
    }
    
    // 计算每个代理商的OCPC和CPC占比
    const agentTotals = {};
    labels.forEach(agent => {
        agentTotals[agent] = datasets.reduce((sum, dataset) => {
            const idx = labels.indexOf(agent);
            return sum + (dataset.data[idx] || 0);
        }, 0);
    });
    
    charts.agentSpend = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y || 0;
                            const agent = labels[context.dataIndex];
                            const total = agentTotals[agent] || 0;
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(2) : '0.00';
                            return `${label}: ${value.toLocaleString('zh-CN')}元 (${percentage}%)`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value >= 10000 ? (value / 10000).toFixed(1) + '万' : value;
                        }
                    }
                }
            }
        }
    });
}

// 出价方式花费分布图
function updateBiddingMethodChart(biddingStats) {
    const ctx = document.getElementById('biddingMethodChart').getContext('2d');
    const labels = biddingStats.map(b => b.出价方式);
    const spendData = biddingStats.map(b => b.花费 || 0);
    
    if (charts.biddingMethod) {
        charts.biddingMethod.destroy();
    }
    
    if (labels.length === 0) {
        return;
    }
    
    const totalSpend = spendData.reduce((a, b) => a + b, 0);
    
    charts.biddingMethod = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: spendData,
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const percentage = totalSpend > 0 ? ((value / totalSpend) * 100).toFixed(2) : '0.00';
                            return `${label}: ${value.toLocaleString('zh-CN')}元 (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// 定向花费分布
function updateTargetingSpendChart(targetingStats) {
    const ctx = document.getElementById('targetingSpendChart').getContext('2d');
    const labels = targetingStats.map(item => item.定向);
    const spendData = targetingStats.map(item => item.花费 || 0);

    if (charts.targetingSpend) {
        charts.targetingSpend.destroy();
    }

    if (labels.length === 0) {
        return;
    }

    const totalTargetingSpend = spendData.reduce((a, b) => a + b, 0);
    
    charts.targetingSpend = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: spendData,
                backgroundColor: labels.map((_, idx) => {
                    const colors = [
                        '#667eea', '#54c5f8', '#ffb84d', '#ff6f91',
                        '#6bcB77', '#845ec2', '#ffc75f', '#0081cf'
                    ];
                    return colors[idx % colors.length] + 'cc';
                })
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const percentage = totalTargetingSpend > 0 ? ((value / totalTargetingSpend) * 100).toFixed(2) : '0.00';
                            return `${label}: ${value.toLocaleString('zh-CN')}元 (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// 资源位花费分布
function updateResourceSpendChart(resourceStats) {
    const ctx = document.getElementById('resourceSpendChart').getContext('2d');
    const labels = resourceStats.map(item => item.资源位);
    const spendData = resourceStats.map(item => item.花费 || 0);

    if (charts.resourceSpend) {
        charts.resourceSpend.destroy();
    }

    if (labels.length === 0) {
        return;
    }

    const totalResourceSpend = spendData.reduce((a, b) => a + b, 0);
    
    charts.resourceSpend = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '花费（元）',
                data: spendData,
                backgroundColor: 'rgba(102, 126, 234, 0.8)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed.y || 0;
                            const percentage = totalResourceSpend > 0 ? ((value / totalResourceSpend) * 100).toFixed(2) : '0.00';
                            return `花费: ${value.toLocaleString('zh-CN')}元 (${percentage}%)`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value >= 10000 ? (value / 10000).toFixed(1) + '万' : value;
                        }
                    }
                }
            }
        }
    });
}

// 通过率趋势
function updateRateTrendChart(rateStats) {
    const ctx = document.getElementById('rateTrendChart').getContext('2d');
    const labels = Array.from(new Set(rateStats.map(item => item.时间))).sort();

    const entryRate = labels.map(date => {
        const day = rateStats.find(item => item.时间 === date);
        return day && day.准入通过率 != null ? Number((day.准入通过率 * 100).toFixed(2)) : null;
    });
    const creditRate = labels.map(date => {
        const day = rateStats.find(item => item.时间 === date);
        return day && day.授信通过率 != null ? Number((day.授信通过率 * 100).toFixed(2)) : null;
    });
    const loanRate = labels.map(date => {
        const day = rateStats.find(item => item.时间 === date);
        return day && day.支用通过率 != null ? Number((day.支用通过率 * 100).toFixed(2)) : null;
    });

    if (charts.rateTrend) {
        charts.rateTrend.destroy();
    }

    charts.rateTrend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '准入通过率',
                    data: entryRate,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102,126,234,0.15)',
                    tension: 0.4
                },
                {
                    label: '授信通过率',
                    data: creditRate,
                    borderColor: '#ff6f91',
                    backgroundColor: 'rgba(255,111,145,0.15)',
                    tension: 0.4
                },
                {
                    label: '支用通过率',
                    data: loanRate,
                    borderColor: '#2ec4b6',
                    backgroundColor: 'rgba(46,196,182,0.15)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// 定向弹窗逻辑
function renderTargetingOptions() {
    const container = document.getElementById('targetingOptions');
    if (!container) return;
    container.innerHTML = '';
    if (!filterOptions.targetings || filterOptions.targetings.length === 0) {
        container.innerHTML = '<p class="empty-tip">暂无定向可选</p>';
        return;
    }
    filterOptions.targetings.forEach(targeting => {
        const option = document.createElement('label');
        option.className = 'modal-option';
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = targeting;
        checkbox.checked = selectedTargetings.includes(targeting);
        option.appendChild(checkbox);
        const span = document.createElement('span');
        span.textContent = targeting;
        option.appendChild(span);
        container.appendChild(option);
    });
}

function openTargetingModal() {
    renderTargetingOptions();
    document.getElementById('targetingModal').classList.remove('hidden');
}

function closeTargetingModal() {
    document.getElementById('targetingModal').classList.add('hidden');
}

function applyTargetingSelection() {
    const inputs = document.querySelectorAll('#targetingOptions input[type="checkbox"]');
    selectedTargetings = Array.from(inputs).filter(input => input.checked).map(input => input.value);
    updateTargetingSummary();
    closeTargetingModal();
    applyFilters();
}

function clearTargetingSelection() {
    selectedTargetings = [];
    renderTargetingOptions();
    updateTargetingSummary();
    applyFilters();
}

function updateTargetingSummary() {
    const summary = document.getElementById('targetingSummary');
    if (!summary) return;
    summary.textContent = selectedTargetings.length ? selectedTargetings.join('、') : '全部';
}

// 导出数据
function exportData() {
    window.location.href = '/api/export';
}

