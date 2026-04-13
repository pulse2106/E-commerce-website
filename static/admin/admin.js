document.addEventListener('DOMContentLoaded', function() {
    // 1. Tooltip or Hover Effects for Tables
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.style.backgroundColor = 'rgba(212, 163, 115, 0.05)';
        });
        row.addEventListener('mouseleave', () => {
            row.style.backgroundColor = 'transparent';
        });
    });

    // 2. Responsive Chart Resizing
    window.addEventListener('resize', function() {
        const charts = document.querySelectorAll('.js-plotly-plot');
        charts.forEach(chart => {
            if (chart.id) {
                Plotly.Plots.resize(chart);
            }
        });
    });

    // 3. Simple Confirmation for Admin Actions
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (!confirm('Are you sure you want to delete this record? This action is permanent.')) {
                e.preventDefault();
            }
        });
    });
});