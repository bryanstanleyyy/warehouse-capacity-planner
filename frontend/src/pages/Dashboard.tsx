import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Paper,
  Divider,
} from '@mui/material';
import {
  Warehouse as WarehouseIcon,
  Inventory as InventoryIcon,
  Assessment as AssessmentIcon,
  Add as AddIcon,
  CloudUpload as CloudUploadIcon,
  PlayArrow as PlayArrowIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { warehouseApi } from '../api/warehouses';
import { inventoryApi } from '../api/inventory';
import { allocationApi } from '../api/allocation';

export default function Dashboard() {
  const navigate = useNavigate();

  const { data: warehouses = [] } = useQuery({
    queryKey: ['warehouses'],
    queryFn: warehouseApi.getAll,
  });

  const { data: uploads = [] } = useQuery({
    queryKey: ['inventory-uploads'],
    queryFn: inventoryApi.getUploads,
  });

  const { data: allocationResults = [] } = useQuery({
    queryKey: ['allocation-results'],
    queryFn: () => allocationApi.getAllResults(),
  });

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Welcome to Warehouse Capacity Planner
        </Typography>

        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <WarehouseIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                  <Box>
                    <Typography variant="h3">{warehouses.length}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Warehouses
                    </Typography>
                  </Box>
                </Box>
                <Divider sx={{ my: 2 }} />
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<AddIcon />}
                  onClick={() => navigate('/warehouses')}
                >
                  Manage Warehouses
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <InventoryIcon sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
                  <Box>
                    <Typography variant="h3">{uploads.length}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Inventory Uploads
                    </Typography>
                  </Box>
                </Box>
                <Divider sx={{ my: 2 }} />
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<CloudUploadIcon />}
                  onClick={() => navigate('/inventory')}
                >
                  Upload Inventory
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <AssessmentIcon sx={{ fontSize: 40, color: 'warning.main', mr: 2 }} />
                  <Box>
                    <Typography variant="h3">{allocationResults.length}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Allocation Results
                    </Typography>
                  </Box>
                </Box>
                <Divider sx={{ my: 2 }} />
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<PlayArrowIcon />}
                  onClick={() => navigate('/allocation')}
                >
                  Run Allocation
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Quick Start Guide */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Quick Start Guide
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Get started with warehouse capacity planning in three simple steps:
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Box
                  sx={{
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    bgcolor: 'primary.main',
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 'bold',
                    flexShrink: 0,
                  }}
                >
                  1
                </Box>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Create a Warehouse
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Define your warehouse with storage zones, specifying area, height, and floor
                    strength for each zone
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Box
                  sx={{
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    bgcolor: 'success.main',
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 'bold',
                    flexShrink: 0,
                  }}
                >
                  2
                </Box>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Upload Inventory
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Import your inventory data from an Excel file with item dimensions, weights,
                    and quantities
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Box
                  sx={{
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    bgcolor: 'warning.main',
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 'bold',
                    flexShrink: 0,
                  }}
                >
                  3
                </Box>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Run Allocation
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Execute the optimization algorithm to allocate items to zones and view detailed
                    results
                  </Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      </Box>
    </Container>
  );
}
