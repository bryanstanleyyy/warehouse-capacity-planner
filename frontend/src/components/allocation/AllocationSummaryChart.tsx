import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Box, Paper, Typography, Grid } from '@mui/material';
import { CheckCircle as CheckCircleIcon, Error as ErrorIcon } from '@mui/icons-material';
import type { AllocationSummary } from '../../types/allocation';

ChartJS.register(ArcElement, Tooltip, Legend);

interface AllocationSummaryChartProps {
  summary: AllocationSummary;
}

export const AllocationSummaryChart: React.FC<AllocationSummaryChartProps> = ({ summary }) => {
  const data = {
    labels: ['Allocated', 'Failed'],
    datasets: [
      {
        data: [summary.total_allocated, summary.total_failed],
        backgroundColor: ['rgba(46, 125, 50, 0.8)', 'rgba(211, 47, 47, 0.8)'],
        borderColor: ['rgba(46, 125, 50, 1)', 'rgba(211, 47, 47, 1)'],
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
      tooltip: {
        callbacks: {
          label: function (context: any) {
            const label = context.label || '';
            const value = context.parsed || 0;
            const total = summary.total_items;
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value} items (${percentage}%)`;
          },
        },
      },
    },
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Allocation Summary
      </Typography>
      <Grid container spacing={2} sx={{ mt: 1 }}>
        <Grid item xs={12} sm={6}>
          <Box sx={{ height: 200 }}>
            <Doughnut data={data} options={options} />
          </Box>
        </Grid>
        <Grid item xs={12} sm={6}>
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              height: '100%',
              gap: 2,
            }}
          >
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                <CheckCircleIcon color="success" fontSize="small" />
                <Typography variant="body2" fontWeight="medium">
                  Allocated Items
                </Typography>
              </Box>
              <Typography variant="h5" color="success.main">
                {summary.total_allocated}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {summary.allocation_rate.toFixed(1)}% of total
              </Typography>
            </Box>
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                <ErrorIcon color="error" fontSize="small" />
                <Typography variant="body2" fontWeight="medium">
                  Failed Items
                </Typography>
              </Box>
              <Typography variant="h5" color="error.main">
                {summary.total_failed}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {((summary.total_failed / summary.total_items) * 100).toFixed(1)}% of total
              </Typography>
            </Box>
          </Box>
        </Grid>
      </Grid>
      <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Typography variant="caption" color="text.secondary">
              Total Items
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              {summary.total_items}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="caption" color="text.secondary">
              Space Used
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              {summary.total_used_area.toLocaleString()} sq ft
            </Typography>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
};
