let rawData = null;
let charts = {};

// Colors
const COLOR_RED = '#E23744';
const COLOR_GOLD = '#FFD700';
const COLOR_BLUE = '#00F2FE';
const COLOR_PURPLE = '#9D50BB';
const COLOR_GREEN = '#00E676';
const COLOR_ORANGE = '#FF9800';
const COLOR_DARK_CARD = '#1E252B';

document.addEventListener("DOMContentLoaded", () => {
    fetch('dashboard_data.json')
        .then(res => res.json())
        .then(data => {
            rawData = data;
            initDashboard();
        })
        .catch(err => console.error("Error loading dashboard data:", err));

    // Setup filter listeners
    document.getElementById('filter-city').addEventListener('change', applyFilters);
    document.getElementById('filter-gold').addEventListener('change', applyFilters);
    document.getElementById('filter-status').addEventListener('change', applyFilters);
});

function initDashboard() {
    renderKPIs(rawData.kpis);
    renderCharts(rawData);
}

function renderKPIs(kpis) {
    document.getElementById('kpi-revenue').innerText = '₹' + (kpis.total_revenue / 100000).toFixed(2) + 'L';
    document.getElementById('kpi-orders').innerText = kpis.total_orders.toLocaleString();
    document.getElementById('kpi-aov').innerText = '₹' + Math.round(kpis.avg_order_value);
    document.getElementById('kpi-cancel').innerText = kpis.cancellation_rate.toFixed(2) + '%';
    document.getElementById('kpi-ontime').innerText = kpis.on_time_rate.toFixed(1) + '%';
}

function renderCharts(data) {
    // 1. Monthly Revenue & Order Trend
    const ctxMonthly = document.getElementById('chart-monthly-trend').getContext('2d');
    charts.monthly = new Chart(ctxMonthly, {
        type: 'line',
        data: {
            labels: data.monthly_perf.map(d => d.month),
            datasets: [{
                label: 'Revenue (₹)',
                data: data.monthly_perf.map(d => d.revenue),
                borderColor: COLOR_RED,
                backgroundColor: 'rgba(226, 55, 68, 0.1)',
                fill: true,
                tension: 0.3
            }]
        },
        options: getChartOptions('Revenue Trend')
    });

    // 2. City Revenue
    const ctxCity = document.getElementById('chart-city-revenue').getContext('2d');
    charts.city = new Chart(ctxCity, {
        type: 'bar',
        data: {
            labels: data.revenue_by_city.map(d => d.city),
            datasets: [{
                label: 'Revenue (₹)',
                data: data.revenue_by_city.map(d => d.revenue),
                backgroundColor: [COLOR_RED, COLOR_BLUE, COLOR_GOLD, COLOR_PURPLE, COLOR_GREEN, COLOR_ORANGE, '#E91E63', '#00BCD4']
            }]
        },
        options: getChartOptions('Revenue by City')
    });

    // 3. Order Status
    const ctxStatus = document.getElementById('chart-order-status').getContext('2d');
    charts.status = new Chart(ctxStatus, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data.order_status_counts),
            datasets: [{
                data: Object.values(data.order_status_counts),
                backgroundColor: [COLOR_GREEN, COLOR_RED, COLOR_GOLD]
            }]
        },
        options: getChartOptions('Order Status Distribution')
    });

    // 4. Top Restaurants
    const ctxTopRest = document.getElementById('chart-top-rest').getContext('2d');
    charts.topRest = new Chart(ctxTopRest, {
        type: 'bar',
        data: {
            labels: data.top_restaurants.map(r => r.restaurant_name),
            datasets: [{
                label: 'Revenue (₹)',
                data: data.top_restaurants.map(r => r.revenue),
                backgroundColor: COLOR_BLUE
            }]
        },
        options: getChartOptions('Top Restaurants', 'y')
    });

    // 5. Demographics Age
    const ctxAge = document.getElementById('chart-demographics-age').getContext('2d');
    charts.age = new Chart(ctxAge, {
        type: 'pie',
        data: {
            labels: Object.keys(data.demographics_age),
            datasets: [{
                data: Object.values(data.demographics_age),
                backgroundColor: [COLOR_BLUE, COLOR_PURPLE, COLOR_GOLD, COLOR_RED]
            }]
        },
        options: getChartOptions('Age Groups')
    });

    // 6. Demographics Gender
    const ctxGender = document.getElementById('chart-demographics-gender').getContext('2d');
    charts.gender = new Chart(ctxGender, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data.demographics_gender),
            datasets: [{
                data: Object.values(data.demographics_gender),
                backgroundColor: ['#EC407A', '#42A5F5', '#AB47BC']
            }]
        },
        options: getChartOptions('Gender Split')
    });

    // 7. Cuisine Dist
    const ctxCuisine = document.getElementById('chart-cuisine-dist').getContext('2d');
    charts.cuisine = new Chart(ctxCuisine, {
        type: 'polarArea',
        data: {
            labels: data.cuisine_dist.map(c => c.cuisine),
            datasets: [{
                data: data.cuisine_dist.map(c => c.orders),
                backgroundColor: [COLOR_RED, COLOR_GOLD, COLOR_BLUE, COLOR_GREEN, COLOR_PURPLE, COLOR_ORANGE]
            }]
        },
        options: getChartOptions('Cuisine Distribution')
    });

    // 8. Restaurant Rating
    const ctxRating = document.getElementById('chart-rest-rating').getContext('2d');
    charts.rating = new Chart(ctxRating, {
        type: 'bar',
        data: {
            labels: data.top_restaurants.map(r => r.restaurant_name),
            datasets: [{
                label: 'Avg Rating ⭐',
                data: data.top_restaurants.map(r => r.rating),
                backgroundColor: COLOR_GOLD
            }]
        },
        options: getChartOptions('Ratings')
    });

    // 9. Delivery Partner Perf
    const ctxPartner = document.getElementById('chart-partner-perf').getContext('2d');
    charts.partner = new Chart(ctxPartner, {
        type: 'bar',
        data: {
            labels: data.delivery_partner_perf.map(p => p.partner_name),
            datasets: [{
                label: 'Completed Trips',
                data: data.delivery_partner_perf.map(p => p.deliveries),
                backgroundColor: COLOR_GREEN
            }]
        },
        options: getChartOptions('Delivery Partners')
    });

    // 10. Payment Methods
    const ctxPayment = document.getElementById('chart-payment-methods').getContext('2d');
    charts.payment = new Chart(ctxPayment, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data.payment_dist),
            datasets: [{
                data: Object.values(data.payment_dist),
                backgroundColor: [COLOR_BLUE, COLOR_GREEN, COLOR_GOLD, COLOR_RED, COLOR_PURPLE]
            }]
        },
        options: getChartOptions('Payment Share')
    });

    // 11. Cancellation Reasons
    const ctxCancelReason = document.getElementById('chart-cancellation-reasons').getContext('2d');
    charts.cancelReason = new Chart(ctxCancelReason, {
        type: 'bar',
        data: {
            labels: Object.keys(data.cancellation_reasons),
            datasets: [{
                label: 'Cancelled Orders',
                data: Object.values(data.cancellation_reasons),
                backgroundColor: COLOR_RED
            }]
        },
        options: getChartOptions('Cancellation Reasons', 'y')
    });

    // 12. Refund Impact
    const ctxRefund = document.getElementById('chart-refund-impact').getContext('2d');
    charts.refund = new Chart(ctxRefund, {
        type: 'bar',
        data: {
            labels: ['Total Delivered', 'Cancelled Loss', 'Refund Impact'],
            datasets: [{
                label: 'Amount (₹)',
                data: [data.kpis.total_revenue, data.kpis.total_revenue * 0.098, data.kpis.total_revenue * 0.042],
                backgroundColor: [COLOR_GREEN, COLOR_RED, COLOR_ORANGE]
            }]
        },
        options: getChartOptions('Financial Leakage')
    });
}

function getChartOptions(title, indexAxis = 'x') {
    return {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: indexAxis,
        plugins: {
            legend: { labels: { color: '#94A3B8', font: { family: 'Inter' } } }
        },
        scales: indexAxis === 'x' ? {
            x: { ticks: { color: '#94A3B8' }, grid: { color: '#2A343F' } },
            y: { ticks: { color: '#94A3B8' }, grid: { color: '#2A343F' } }
        } : {
            x: { ticks: { color: '#94A3B8' }, grid: { color: '#2A343F' } },
            y: { ticks: { color: '#94A3B8' }, grid: { color: '#2A343F' } }
        }
    };
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    document.getElementById(tabId).classList.add('active');
}

function applyFilters() {
    const city = document.getElementById('filter-city').value;
    const gold = document.getElementById('filter-gold').value;
    const status = document.getElementById('filter-status').value;

    let filtered = rawData.sample_orders.filter(o => {
        if (city !== 'ALL' && o.city !== city) return false;
        if (gold !== 'ALL' && ((gold === 'Gold' && !o.zomato_gold) || (gold === 'Regular' && o.zomato_gold))) return false;
        if (status !== 'ALL' && o.status !== status) return false;
        return true;
    });

    // Recalculate KPIs dynamically
    const totalRev = filtered.filter(o => o.status === 'Delivered').reduce((sum, o) => sum + (o.final_amount || 0), 0);
    const totalOrders = filtered.length || 1;
    const aov = totalRev / (filtered.filter(o => o.status === 'Delivered').length || 1);
    const cancelPct = (filtered.filter(o => o.status === 'Cancelled').length / totalOrders) * 100;

    document.getElementById('kpi-revenue').innerText = '₹' + (totalRev / 100000).toFixed(2) + 'L';
    document.getElementById('kpi-orders').innerText = totalOrders.toLocaleString();
    document.getElementById('kpi-aov').innerText = '₹' + Math.round(aov);
    document.getElementById('kpi-cancel').innerText = cancelPct.toFixed(2) + '%';
}

function resetFilters() {
    document.getElementById('filter-city').value = 'ALL';
    document.getElementById('filter-gold').value = 'ALL';
    document.getElementById('filter-status').value = 'ALL';
    initDashboard();
}

function showDax(title, code) {
    document.getElementById('dax-title').innerText = 'DAX: ' + title;
    document.getElementById('dax-code').innerText = code;
    document.getElementById('dax-modal').style.display = 'flex';
}

function toggleDaxDrawer() {
    showDax('DAX Library Overview', `
-- Key DAX Formulas Used in Zomato Analytics Engine

Total Revenue = 
CALCULATE(
    SUM(Orders[final_amount]),
    Orders[status] = "Delivered"
)

Cancellation Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS(Orders), Orders[status] = "Cancelled"),
    COUNTROWS(Orders),
    0
)

On-Time Delivery % = 
DIVIDE(
    CALCULATE(COUNTROWS(Orders), Orders[delivery_time_minutes] <= 45),
    COUNTROWS(Orders),
    0
)
    `);
}

function closeDaxModal(event) {
    if (event.target.id === 'dax-modal') {
        document.getElementById('dax-modal').style.display = 'none';
    }
}

function closeDaxModalDirect() {
    document.getElementById('dax-modal').style.display = 'none';
}
