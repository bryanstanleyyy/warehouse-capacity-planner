import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Chip,
  Grid,
  Snackbar,
  Alert,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import DownloadIcon from '@mui/icons-material/Download';
import { useQuery } from '@tanstack/react-query';
import { inventoryApi } from '../api/inventory';

export default function InventoryDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const uploadId = parseInt(id || '0');

  const [downloading, setDownloading] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error',
  });

  // Query for upload details
  const { data: upload, isLoading: uploadLoading } = useQuery({
    queryKey: ['inventory-upload', uploadId],
    queryFn: () => inventoryApi.getUpload(uploadId),
    enabled: !!uploadId,
  });

  // Query for upload items
  const { data: items = [], isLoading: itemsLoading } = useQuery({
    queryKey: ['inventory-items', uploadId],
    queryFn: () => inventoryApi.getUploadItems(uploadId),
    enabled: !!uploadId,
  });

  // Query for upload summary
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['inventory-summary', uploadId],
    queryFn: () => inventoryApi.getUploadSummary(uploadId),
    enabled: !!uploadId,
  });

  if (uploadLoading || itemsLoading || summaryLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  const handleDownloadExcel = async () => {
    if (!upload) return;
    setDownloading(true);
    try {
      const blob = await inventoryApi.exportXLSX(uploadId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${upload.upload_name}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to download Excel file',
        severity: 'error',
      });
    } finally {
      setDownloading(false);
    }
  };

  if (!upload) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography>Upload not found</Typography>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/inventory')} sx={{ mt: 2 }}>
          Back to Inventory
        </Button>
      </Box>
    );
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/inventory')}
            sx={{ mb: 1 }}
          >
            Back to Inventory
          </Button>
          <Typography variant="h4" component="h1">
            {upload.upload_name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Uploaded: {formatDate(upload.upload_date)}
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<DownloadIcon />}
          onClick={handleDownloadExcel}
          disabled={downloading}
        >
          {downloading ? 'Downloading...' : 'Download Excel'}
        </Button>
      </Box>

      {/* Upload Details Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Upload Details
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">
                Filename
              </Typography>
              <Typography variant="body1">{upload.filename}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">
                Total Items
              </Typography>
              <Typography variant="body1">{upload.total_items}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">
                Total Weight
              </Typography>
              <Typography variant="body1">{upload.total_weight.toLocaleString()} lbs</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">
                Total Area
              </Typography>
              <Typography variant="body1">{upload.total_area.toLocaleString()} sq ft</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="text.secondary">
                BSF Factor
              </Typography>
              <Typography variant="body1">{upload.bsf_factor}</Typography>
            </Grid>
            {upload.site && (
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Primary Site
                </Typography>
                <Chip label={upload.site} size="small" />
              </Grid>
            )}
            {upload.site2 && (
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Secondary Site
                </Typography>
                <Chip label={upload.site2} size="small" />
              </Grid>
            )}
          </Grid>
        </CardContent>
      </Card>

      {/* Summary Statistics */}
      {summary && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Summary Statistics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Categories
                </Typography>
                <Typography variant="body1">{summary.total_categories || 0}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Avg Item Weight
                </Typography>
                <Typography variant="body1">
                  {summary.average_weight ? summary.average_weight.toFixed(2) : '0'} lbs
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Avg Item Area
                </Typography>
                <Typography variant="body1">
                  {summary.average_area ? summary.average_area.toFixed(2) : '0'} sq ft
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Total PSF
                </Typography>
                <Typography variant="body1">
                  {summary.total_psf ? summary.total_psf.toFixed(2) : '0'}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Items Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Items ({items.length})
          </Typography>
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell align="right">Quantity</TableCell>
                  <TableCell align="right">Height (ft)</TableCell>
                  <TableCell align="right">Area (sq ft)</TableCell>
                  <TableCell align="right">Weight (lbs)</TableCell>
                  <TableCell align="right">PSF</TableCell>
                  <TableCell>Service Branch</TableCell>
                  <TableCell align="center">Climate Control</TableCell>
                  <TableCell align="center">Special Handling</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {items.map((item) => (
                  <TableRow key={item.id} hover>
                    <TableCell>{item.name}</TableCell>
                    <TableCell>
                      {item.category && <Chip label={item.category} size="small" />}
                    </TableCell>
                    <TableCell align="right">{item.quantity}</TableCell>
                    <TableCell align="right">{item.height?.toFixed(2) || '0'}</TableCell>
                    <TableCell align="right">{item.area?.toFixed(2) || '0'}</TableCell>
                    <TableCell align="right">{item.weight?.toFixed(2) || '0'}</TableCell>
                    <TableCell align="right">{item.psf?.toFixed(2) || '0'}</TableCell>
                    <TableCell>
                      {item.service_branch && <Chip label={item.service_branch} size="small" />}
                    </TableCell>
                    <TableCell align="center">
                      {item.requires_climate_control && (
                        <Chip label="Yes" size="small" color="info" />
                      )}
                    </TableCell>
                    <TableCell align="center">
                      {item.requires_special_handling && (
                        <Chip label="Yes" size="small" color="warning" />
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
