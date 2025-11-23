import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface HistoryData {
  year: number
  profit: number
  reputation: number
  budget: number
}

interface AnalyticsChartsProps {
  history: HistoryData[]
}

export default function AnalyticsCharts({ history }: AnalyticsChartsProps) {
  const formatCurrency = (value: number) => {
    if (value >= 1_000_000) {
      return `€${(value / 1_000_000).toFixed(1)}M`
    }
    return `€${value.toLocaleString()}`
  }

  if (history.length === 0) {
    return (
      <div className="p-6 text-center text-gray-400">
        No data yet. Play a turn to see analytics!
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold mb-4">Analytics Dashboard</h2>

      {/* Profit Over Time */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Profit Over Time</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={history}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="year" 
              stroke="#9CA3AF"
              label={{ value: 'Year', position: 'insideBottom', offset: -5, fill: '#9CA3AF' }}
            />
            <YAxis 
              stroke="#9CA3AF"
              tickFormatter={formatCurrency}
            />
            <Tooltip 
              formatter={(value: number) => formatCurrency(value)}
              contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="profit" 
              stroke="#10B981" 
              strokeWidth={2}
              name="Profit"
              dot={{ fill: '#10B981', r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Reputation Over Time */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Reputation Over Time</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={history}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="year" 
              stroke="#9CA3AF"
              label={{ value: 'Year', position: 'insideBottom', offset: -5, fill: '#9CA3AF' }}
            />
            <YAxis 
              stroke="#9CA3AF"
              domain={[0, 100]}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="reputation" 
              stroke="#FBBF24" 
              strokeWidth={2}
              name="Reputation"
              dot={{ fill: '#FBBF24', r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Budget Over Time */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Budget Over Time</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={history}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="year" 
              stroke="#9CA3AF"
              label={{ value: 'Year', position: 'insideBottom', offset: -5, fill: '#9CA3AF' }}
            />
            <YAxis 
              stroke="#9CA3AF"
              tickFormatter={formatCurrency}
            />
            <Tooltip 
              formatter={(value: number) => formatCurrency(value)}
              contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="budget" 
              stroke="#3B82F6" 
              strokeWidth={2}
              name="Budget"
              dot={{ fill: '#3B82F6', r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

