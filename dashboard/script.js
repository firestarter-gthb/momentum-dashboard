document.addEventListener('DOMContentLoaded', () => {
    try {
        if (typeof dashboardData === 'undefined') {
            const errStr = document.documentElement.lang === 'en' 
                ? "Could not load data. Make sure you ran refresh.bat." 
                : "Kon data niet inladen. Zorg dat je refresh.bat hebt gedraaid.";
            throw new Error(errStr);
        }
        const data = dashboardData;
        
        const lang = document.documentElement.lang || 'nl';
        const t = {
            'nl': {
                dateFormat: 'nl-NL',
                avgReturnTitle: 'Gemiddeld Rendement (%)',
                heavyLoss: 'Zwaar Verlies',
                loss: 'Verlies',
                profit: 'Winst',
                highProfit: 'Hoge Winst',
                errLoad: 'Fout bij laden van data: ',
                momentumIndexName: 'Momentum Index (Equal Weight)',
                months: ['Jan', 'Feb', 'Mrt', 'Apr', 'Mei', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
            },
            'en': {
                dateFormat: 'en-US',
                avgReturnTitle: 'Average Return (%)',
                heavyLoss: 'Heavy Loss',
                loss: 'Loss',
                profit: 'Profit',
                highProfit: 'High Profit',
                errLoad: 'Error loading data: ',
                momentumIndexName: 'Momentum Index (Equal Weight)',
                months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            }
        }[lang];

        const now = new Date();
        document.getElementById('update-time').innerText = now.toLocaleString(t.dateFormat);

        // DataSente styling variables
        const c_ink = '#111111';
        const c_muted = '#4a4a4a';
        const c_lime = '#c6f432';
        const c_violet = '#a78bfa';
        const c_pos = '#0f8a3c';
        const c_neg = '#d92d20';

        const commonOptions = {
            chart: {
                background: 'transparent',
                toolbar: { show: false },
                fontFamily: "'Space Grotesk', sans-serif"
            },
            theme: { mode: 'light' }
        };

        // Fix legend name for Momentum Index based on language
        let barSeries = JSON.parse(JSON.stringify(data.average_returns.series));
        barSeries.forEach(s => {
            if (s.id === 'Momentum_Index') {
                s.name = t.momentumIndexName;
            }
        });
        
        // Translate categories
        let barCategories = t.months;
        
        // Find months where Momentum > SPY to highlight them
        let momSeries = barSeries.find(s => s.id === 'Momentum_Index' || s.name === t.momentumIndexName);
        let spySeries = barSeries.find(s => s.name === 'SPY');
        let highlightAnnotations = [];
        
        if (momSeries && spySeries) {
            for (let i = 0; i < 12; i++) {
                if (momSeries.data[i] > spySeries.data[i]) {
                    highlightAnnotations.push({
                        x: barCategories[i],
                        y: momSeries.data[i],
                        seriesIndex: 0, // Attach precisely to the Momentum Index bar
                        marker: {
                            size: 0,
                        },
                        label: {
                            borderColor: 'transparent',
                            style: {
                                background: 'transparent',
                                fontSize: '22px'
                            },
                            text: '🔥',
                            offsetY: -15
                        }
                    });
                }
            }
        }

        // 1. Render Bar Chart (Average Returns)
        const barOptions = {
            ...commonOptions,
            annotations: {
                points: highlightAnnotations
            },
            chart: {
                type: 'bar',
                height: 400,
                background: 'transparent',
                toolbar: { show: false }
            },
            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: '70%',
                    borderRadius: 0,
                    colors: {
                        backgroundBarColors: ['transparent'],
                    }
                },
            },
            colors: [c_ink, c_violet, c_lime, '#ffb4a2', '#9fd8ff', c_pos],
            dataLabels: { enabled: false },
            stroke: { show: true, width: 3, colors: [c_ink] },
            xaxis: {
                categories: barCategories,
                labels: { style: { colors: c_ink, fontFamily: "'Space Mono', monospace", fontWeight: 700 } },
                axisBorder: { color: c_ink, height: 3 },
                axisTicks: { color: c_ink, height: 6 }
            },
            yaxis: {
                title: { text: t.avgReturnTitle, style: { color: c_ink, fontWeight: 700 } },
                labels: { style: { colors: c_ink, fontFamily: "'Space Mono', monospace" } },
                axisBorder: { show: true, color: c_ink, width: 3 },
            },
            grid: {
                borderColor: c_ink,
                strokeDashArray: 0,
            },
            fill: { opacity: 1 },
            tooltip: {
                y: { formatter: function (val) { return val + "%" } }
            },
            legend: {
                labels: { colors: c_ink },
                fontFamily: "'Space Mono', monospace",
                fontWeight: 700,
                position: 'top',
                markers: { strokeWidth: 2, strokeColor: c_ink, radius: 0 }
            },
            series: barSeries
        };
        new ApexCharts(document.querySelector("#bar-chart"), barOptions).render();

        // Map english months from JSON to localized months
        const engMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        
        // 2. Heatmap Render Function
        function renderHeatmap(selector, seriesData, height = 380, hideXAxisLabels = false) {
            if (!seriesData || !document.querySelector(selector)) return;
            
            // Translate X-axis (months) for heatmap
            let translatedSeries = JSON.parse(JSON.stringify(seriesData));
            translatedSeries.forEach(s => {
                s.data.forEach(d => {
                    let idx = engMonths.indexOf(d.x);
                    if(idx !== -1) d.x = t.months[idx];
                });
            });
            
            const heatmapOptions = {
                ...commonOptions,
                chart: {
                    height: height,
                    type: 'heatmap',
                    background: 'transparent',
                    toolbar: { show: false }
                },
                series: translatedSeries,
                dataLabels: {
                    enabled: true,
                    style: { fontFamily: "'Space Mono', monospace", fontWeight: 'bold' },
                    formatter: function(val, opts) {
                        const dataPoint = opts.w.config.series[opts.seriesIndex].data[opts.dataPointIndex];
                        if (dataPoint && dataPoint.hitRate !== undefined) {
                            return dataPoint.hitRate + '%';
                        }
                        return val;
                    }
                },
                tooltip: {
                    y: {
                        formatter: function(val, opts) {
                            // We need to safely check if dataPoint exists
                            if (opts && opts.w && opts.w.config) {
                                const dataPoint = opts.w.config.series[opts.seriesIndex].data[opts.dataPointIndex];
                                if (dataPoint && dataPoint.hitRate !== undefined) {
                                    return dataPoint.hitRate + '%';
                                }
                            }
                            return val + '%';
                        }
                    }
                },
                xaxis: {
                    labels: { 
                        show: !hideXAxisLabels,
                        style: { colors: c_ink, fontFamily: "'Space Mono', monospace", fontWeight: 700 } 
                    },
                    axisTicks: { show: false },
                    tooltip: { enabled: false }
                },
                yaxis: {
                    labels: { 
                        minWidth: 110,
                        maxWidth: 110,
                        style: { colors: c_ink, fontFamily: "'Space Mono', monospace", fontWeight: 700 } 
                    }
                },
                stroke: {
                    width: 2,
                    colors: [c_ink]
                },
                plotOptions: {
                    heatmap: {
                        shadeIntensity: 0.4,
                        radius: 0,
                        useFillColorAsStroke: false,
                        colorScale: {
                            ranges: [
                                { from: -100, to: -5, name: t.heavyLoss, color: c_neg },
                                { from: -5, to: 0, name: t.loss, color: '#ffb4a2' },
                                { from: 0.01, to: 5, name: t.profit, color: c_lime },
                                { from: 5.01, to: 100, name: t.highProfit, color: c_pos }
                            ]
                        }
                    }
                }
            };
            new ApexCharts(document.querySelector(selector), heatmapOptions).render();
        }

        renderHeatmap("#hitrate-index", data.hit_rates['Momentum_Index'], 120, true);
        renderHeatmap("#heatmap-index", data.heatmaps['Momentum_Index'], 380, false);
        
        renderHeatmap("#hitrate-mtum", data.hit_rates['MTUM'], 120, true);
        renderHeatmap("#heatmap-mtum", data.heatmaps['MTUM'], 380, false);
        
        renderHeatmap("#hitrate-qmom", data.hit_rates['QMOM'], 120, true);
        renderHeatmap("#heatmap-qmom", data.heatmaps['QMOM'], 380, false);
        
        renderHeatmap("#hitrate-dwas", data.hit_rates['DWAS'], 120, true);
        renderHeatmap("#heatmap-dwas", data.heatmaps['DWAS'], 380, false);
        
        renderHeatmap("#hitrate-pdp", data.hit_rates['PDP'], 120, true);
        renderHeatmap("#heatmap-pdp", data.heatmaps['PDP'], 380, false);
        
        renderHeatmap("#hitrate-spy", data.hit_rates['SPY'], 120, true);
        renderHeatmap("#heatmap-spy", data.heatmaps['SPY'], 380, false);

    } catch (error) {
        console.error("Error loading dashboard data:", error);
        document.getElementById('bar-chart').innerHTML = `<p style="color:red; text-align:center; font-weight:bold;">${error.message}</p>`;
    }
});
