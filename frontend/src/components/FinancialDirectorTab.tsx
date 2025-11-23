import { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface FinancialMetrics {
  npv: number;
  roi: number;
  irr: number;
  total_profit: number;
  total_investment: number;
  total_revenue: number;
  total_costs: number;
  profit_margin: number;
  turns: number;
}

interface HistoryEntry {
  year: number;
  profit: number;
  revenue: number;
  costs: number;
}

interface FinancialDirectorTabProps {
  history: HistoryEntry[];
}

export default function FinancialDirectorTab({ history }: FinancialDirectorTabProps) {
  const [metrics, setMetrics] = useState<FinancialMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
  }, [history]);

  const fetchMetrics = async () => {
    try {
      const response = await axios.get<FinancialMetrics>(`${API_BASE_URL}/financial_metrics`);
      setMetrics(response.data);
    } catch (error) {
      console.error('Error fetching financial metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  // Prepare data for cash flow waterfall chart
  const waterfallData = history.map((entry) => ({
    year: `Year ${entry.year}`,
    revenue: entry.revenue,
    costs: -Math.abs(entry.costs),
    profit: entry.profit,
  }));

  // Prepare data for cumulative profit chart
  const cumulativeData = history.reduce((acc, entry) => {
    const cumulative = acc.length > 0 ? acc[acc.length - 1].cumulative + entry.profit : entry.profit;
    acc.push({
      year: `Year ${entry.year}`,
      cumulative,
      profit: entry.profit,
    });
    return acc;
  }, [] as Array<{ year: string; cumulative: number; profit: number }>);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading financial metrics...</div>
      </div>
    );
  }

  const exportToCSV = () => {
    if (!metrics) return;

    // Calculate CO2 saved (assuming industry average of 100 per launch, no reduction)
    const industryAverageCO2 = history.length * 100; // 100 per launch
    const co2Saved = industryAverageCO2 - (metrics.total_costs > 0 ? (metrics.total_costs / 1_000_000) * 10 : 0); // Rough estimate
    
    // Prepare CSV content
    let csvContent = "M.A.R.S. Project - Financial Report\n\n";
    csvContent += "Final Metrics\n";
    csvContent += `NPV,${metrics.npv.toFixed(2)}\n`;
    csvContent += `ROI,${metrics.roi.toFixed(2)}%\n`;
    csvContent += `IRR,${metrics.irr.toFixed(2)}%\n`;
    csvContent += `Total Profit,${metrics.total_profit.toFixed(2)}\n`;
    csvContent += `Total Investment,${metrics.total_investment.toFixed(2)}\n`;
    csvContent += `Total Revenue,${metrics.total_revenue.toFixed(2)}\n`;
    csvContent += `Total Costs,${metrics.total_costs.toFixed(2)}\n`;
    csvContent += `Profit Margin,${metrics.profit_margin.toFixed(2)}%\n`;
    csvContent += `CO2 Impact,${(metrics.total_costs > 0 ? (metrics.total_costs / 1_000_000) * 10 : 0).toFixed(2)}\n`;
    csvContent += `Industry Average CO2,${industryAverageCO2.toFixed(2)}\n`;
    csvContent += `CO2 Saved,${co2Saved.toFixed(2)}\n\n`;
    
    csvContent += "Year-by-Year Decision Log\n";
    csvContent += "Year,Revenue,Costs,Profit,Cumulative Profit\n";
    
    let cumulativeProfit = 0;
    history.forEach((entry) => {
      cumulativeProfit += entry.profit;
      csvContent += `${entry.year},${entry.revenue.toFixed(2)},${entry.costs.toFixed(2)},${entry.profit.toFixed(2)},${cumulativeProfit.toFixed(2)}\n`;
    });

    // Create and download file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `mars_financial_report_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl font-bold">Financial Director Dashboard</h2>
        <button
          onClick={exportToCSV}
          className="bg-green-600 hover:bg-green-700 text-white font-semibold px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Export Report (CSV)
        </button>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-gray-400 text-sm mb-2">Net Present Value (NPV)</h3>
          <div className="text-3xl font-bold text-green-400">
            €{metrics?.npv ? (metrics.npv / 1_000_000).toFixed(2) : '0.00'}M
          </div>
          <p className="text-xs text-gray-500 mt-2">Discounted at 5%</p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-gray-400 text-sm mb-2">Return on Investment (ROI)</h3>
          <div className={`text-3xl font-bold ${(metrics?.roi || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {metrics?.roi ? metrics.roi.toFixed(2) : '0.00'}%
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Profit: €{metrics?.total_profit ? (metrics.total_profit / 1_000_000).toFixed(2) : '0.00'}M
          </p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-gray-400 text-sm mb-2">Internal Rate of Return (IRR)</h3>
          <div className="text-3xl font-bold text-blue-400">
            {metrics?.irr ? metrics.irr.toFixed(2) : '0.00'}%
          </div>
          <p className="text-xs text-gray-500 mt-2">Breakeven interest rate</p>
        </div>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-gray-400 text-xs mb-1">Total Revenue</h4>
          <div className="text-xl font-semibold text-green-400">
            €{metrics?.total_revenue ? (metrics.total_revenue / 1_000_000).toFixed(1) : '0.0'}M
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-gray-400 text-xs mb-1">Total Costs</h4>
          <div className="text-xl font-semibold text-red-400">
            €{metrics?.total_costs ? (metrics.total_costs / 1_000_000).toFixed(1) : '0.0'}M
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-gray-400 text-xs mb-1">Total Investment</h4>
          <div className="text-xl font-semibold text-yellow-400">
            €{metrics?.total_investment ? (metrics.total_investment / 1_000_000).toFixed(1) : '0.0'}M
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-gray-400 text-xs mb-1">Profit Margin</h4>
          <div className={`text-xl font-semibold ${(metrics?.profit_margin || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {metrics?.profit_margin ? metrics.profit_margin.toFixed(1) : '0.0'}%
          </div>
        </div>
      </div>

      {/* Cash Flow Waterfall Chart */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-bold mb-4">Cash Flow Waterfall</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={waterfallData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="year" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip
              contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
              formatter={(value: number) => `€${(value / 1_000_000).toFixed(2)}M`}
            />
            <Legend />
            <Bar dataKey="revenue" fill="#10B981" name="Revenue" />
            <Bar dataKey="costs" fill="#EF4444" name="Costs" />
            <Bar dataKey="profit" fill="#3B82F6" name="Profit" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Cumulative Profit Chart */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-bold mb-4">Cumulative Profit Over Time</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={cumulativeData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="year" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip
              contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
              formatter={(value: number) => `€${(value / 1_000_000).toFixed(2)}M`}
            />
            <Legend />
            <Line type="monotone" dataKey="cumulative" stroke="#3B82F6" strokeWidth={2} name="Cumulative Profit" />
            <Line type="monotone" dataKey="profit" stroke="#10B981" strokeWidth={2} name="Period Profit" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Transaction Ledger */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-bold mb-4">Transaction Ledger</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left p-2 text-gray-400">Year</th>
                <th className="text-right p-2 text-gray-400">Revenue</th>
                <th className="text-right p-2 text-gray-400">Costs</th>
                <th className="text-right p-2 text-gray-400">Profit</th>
                <th className="text-right p-2 text-gray-400">Cumulative</th>
              </tr>
            </thead>
            <tbody>
              {history.map((entry, index) => {
                const cumulative = history.slice(0, index + 1).reduce((sum, e) => sum + e.profit, 0);
                return (
                  <tr key={index} className="border-b border-gray-700 hover:bg-gray-700">
                    <td className="p-2">{entry.year}</td>
                    <td className="p-2 text-right text-green-400">€{(entry.revenue / 1_000_000).toFixed(2)}M</td>
                    <td className="p-2 text-right text-red-400">€{(Math.abs(entry.costs) / 1_000_000).toFixed(2)}M</td>
                    <td className={`p-2 text-right ${entry.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      €{(entry.profit / 1_000_000).toFixed(2)}M
                    </td>
                    <td className={`p-2 text-right ${cumulative >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      €{(cumulative / 1_000_000).toFixed(2)}M
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

