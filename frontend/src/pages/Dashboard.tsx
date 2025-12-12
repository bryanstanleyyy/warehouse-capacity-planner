import { Box, Typography, Card, CardContent, Grid } from '@mui/material';

export default function Dashboard() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Welcome to Warehouse Capacity Planner
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Warehouses
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Manage your warehouse facilities and storage zones
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Inventory
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Upload and manage inventory data from Excel files
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Allocation
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Run allocation analysis and optimize space usage
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
