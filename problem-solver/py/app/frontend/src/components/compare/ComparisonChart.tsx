
import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { NeuralModelComparison } from '@/types/neural';

interface ComparisonChartProps {
  data: NeuralModelComparison[];
  metric: string;
  title: string;
  description?: string;
}

const ComparisonChart: React.FC<ComparisonChartProps> = ({
  data,
  metric,
  title,
  description
}) => {
  // Colors for different models
  const barColors = [
    'var(--neural-primary)',
    'var(--neural-secondary)',
    'var(--neural-accent)',
    'var(--neural-info)',
    'var(--neural-success)'
  ];
  
  // Format the data for the chart
  const chartData = data.map(item => ({
    name: item.name,
    [metric]: item.metrics[metric as keyof typeof item.metrics]
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent className="pt-2">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={chartData}
            margin={{
              top: 20,
              right: 30,
              left: 20,
              bottom: 30,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
            <XAxis 
              dataKey="name" 
              tick={{ fontSize: 12 }} 
              tickLine={false}
              axisLine={{ stroke: 'rgb(var(--muted-foreground))' }}
            />
            <YAxis 
              tick={{ fontSize: 12 }} 
              tickLine={false}
              axisLine={{ stroke: 'rgb(var(--muted-foreground))' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'var(--background)',
                borderColor: 'var(--border)',
                borderRadius: 'var(--radius)',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }} 
            />
            <Legend wrapperStyle={{ paddingTop: 10 }} />
            <Bar 
              dataKey={metric} 
              fill={barColors[0]} 
              name={metric.charAt(0).toUpperCase() + metric.slice(1)}
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default ComparisonChart;
