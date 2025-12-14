import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import type { TooltipItem } from 'chart.js';
import { Box, Paper, Typography } from '@mui/material';
import type { ZoneAllocation } from '../../types/allocation';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface ZoneUtilizationChartProps {
  zoneAllocations: ZoneAllocation[];
}

export const ZoneUtilizationChart: React.FC<ZoneUtilizationChartProps> = ({
  zoneAllocations,
}) => {
  const data = {
    labels: zoneAllocations.map((zone) => zone.zone_info.name),
    datasets: [
      {
        label: 'Area Utilization (%)',
        data: zoneAllocations.map((zone) => zone.area_utilization),
        backgroundColor: zoneAllocations.map((zone) => {
          if (zone.area_utilization > 90) return 'rgba(211, 47, 47, 0.8)'; // Red
          if (zone.area_utilization > 75) return 'rgba(237, 108, 2, 0.8)'; // Orange
          if (zone.area_utilization > 50) return 'rgba(46, 125, 50, 0.8)'; // Green
          return 'rgba(25, 118, 210, 0.8)'; // Blue
        }),
        borderColor: zoneAllocations.map((zone) => {
          if (zone.area_utilization > 90) return 'rgba(211, 47, 47, 1)';
          if (zone.area_utilization > 75) return 'rgba(237, 108, 2, 1)';
          if (zone.area_utilization > 50) return 'rgba(46, 125, 50, 1)';
          return 'rgba(25, 118, 210, 1)';
        }),
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function (context: TooltipItem<'bar'>) {
            return `${context.parsed.y.toFixed(1)}% utilized`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: function (tickValue: string | number) {
            return tickValue + '%';
          },
        },
        title: {
          display: true,
          text: 'Utilization (%)',
        },
      },
      x: {
        title: {
          display: true,
          text: 'Storage Zones',
        },
      },
    },
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Zone Utilization
      </Typography>
      <Box sx={{ height: 300, mt: 2 }}>
        <Bar data={data} options={options} />
      </Box>
      <Box sx={{ mt: 2, display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ width: 16, height: 16, bgcolor: 'rgba(25, 118, 210, 0.8)' }} />
          <Typography variant="caption">Low (0-50%)</Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ width: 16, height: 16, bgcolor: 'rgba(46, 125, 50, 0.8)' }} />
          <Typography variant="caption">Medium (50-75%)</Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ width: 16, height: 16, bgcolor: 'rgba(237, 108, 2, 0.8)' }} />
          <Typography variant="caption">High (75-90%)</Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ width: 16, height: 16, bgcolor: 'rgba(211, 47, 47, 0.8)' }} />
          <Typography variant="caption">Critical (90-100%)</Typography>
        </Box>
      </Box>
    </Paper>
  );
};
