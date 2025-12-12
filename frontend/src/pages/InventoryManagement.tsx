import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Snackbar,
  Alert,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  CloudUpload as CloudUploadIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { inventoryApi } from '../api/inventory';
import { FileUploadZone } from '../components/inventory/FileUploadZone';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import type { InventoryUploadInput } from '../types/inventory';

export default function InventoryManagement() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadName, setUploadName] = useState('');
  const [site, setSite] = useState('');
  const [site2, setSite2] = useState('');
  const [bsfFactor, setBsfFactor] = useState('0.63');
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error',
  });

  const { data: uploads = [], isLoading } = useQuery({
    queryKey: ['inventory-uploads'],
    queryFn: inventoryApi.getUploads,
  });

  const uploadMutation = useMutation({
    mutationFn: (data: InventoryUploadInput) => inventoryApi.uploadInventory(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory-uploads'] });
      setSnackbar({
        open: true,
        message: 'Inventory uploaded successfully',
        severity: 'success',
      });
      handleCloseUploadDialog();
    },
    onError: (error: any) => {
      setSnackbar({
        open: true,
        message: error.response?.data?.message || 'Failed to upload inventory',
        severity: 'error',
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => inventoryApi.deleteUpload(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory-uploads'] });
      setSnackbar({
        open: true,
        message: 'Inventory deleted successfully',
        severity: 'success',
      });
      setDeleteConfirmOpen(false);
      setDeleteId(null);
    },
    onError: () => {
      setSnackbar({
        open: true,
        message: 'Failed to delete inventory',
        severity: 'error',
      });
    },
  });

  const handleOpenUploadDialog = () => {
    setUploadDialogOpen(true);
  };

  const handleCloseUploadDialog = () => {
    setUploadDialogOpen(false);
    setSelectedFile(null);
    setUploadName('');
    setSite('');
    setSite2('');
    setBsfFactor('0.63');
  };

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    if (!uploadName) {
      setUploadName(file.name.replace(/\.[^/.]+$/, ''));
    }
  };

  const handleUpload = () => {
    if (!selectedFile) return;

    const bsfValue = parseFloat(bsfFactor);
    if (isNaN(bsfValue) || bsfValue < 0 || bsfValue > 1) {
      setSnackbar({
        open: true,
        message: 'BSF factor must be between 0.0 and 1.0',
        severity: 'error',
      });
      return;
    }

    uploadMutation.mutate({
      file: selectedFile,
      upload_name: uploadName,
      site,
      site2,
      bsf_factor: bsfValue,
    });
  };

  const handleDeleteClick = (id: number) => {
    setDeleteId(id);
    setDeleteConfirmOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (deleteId !== null) {
      deleteMutation.mutate(deleteId);
    }
  };

  const handleViewDetails = (id: number) => {
    navigate(`/inventory/${id}`);
  };

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
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Typography variant="h4" component="h1">
            Inventory Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleOpenUploadDialog}
          >
            Upload Inventory
          </Button>
        </Box>

        {isLoading ? (
          <Typography>Loading...</Typography>
        ) : uploads.length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <CloudUploadIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No inventory uploads yet
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Upload an Excel file to get started
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleOpenUploadDialog}
              sx={{ mt: 2 }}
            >
              Upload Inventory
            </Button>
          </Paper>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Filename</TableCell>
                  <TableCell>Site</TableCell>
                  <TableCell align="right">Items</TableCell>
                  <TableCell align="right">Weight (lbs)</TableCell>
                  <TableCell align="right">Area (sq ft)</TableCell>
                  <TableCell align="right">BSF</TableCell>
                  <TableCell>Upload Date</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {uploads.map((upload) => (
                  <TableRow key={upload.id} hover>
                    <TableCell>
                      <Typography variant="body1" fontWeight="medium">
                        {upload.upload_name}
                      </Typography>
                    </TableCell>
                    <TableCell>{upload.filename}</TableCell>
                    <TableCell>
                      {upload.site && <Chip label={upload.site} size="small" />}
                      {upload.site2 && <Chip label={upload.site2} size="small" sx={{ ml: 0.5 }} />}
                    </TableCell>
                    <TableCell align="right">{upload.total_items}</TableCell>
                    <TableCell align="right">{upload.total_weight.toLocaleString()}</TableCell>
                    <TableCell align="right">{upload.total_area.toLocaleString()}</TableCell>
                    <TableCell align="right">{upload.bsf_factor}</TableCell>
                    <TableCell>{formatDate(upload.upload_date)}</TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => handleViewDetails(upload.id)}
                        title="View Details"
                      >
                        <VisibilityIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteClick(upload.id)}
                        title="Delete"
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>

      <Dialog open={uploadDialogOpen} onClose={handleCloseUploadDialog} maxWidth="md" fullWidth>
        <DialogTitle>Upload Inventory</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <FileUploadZone
              onFileSelect={handleFileSelect}
              uploading={uploadMutation.isPending}
              disabled={uploadMutation.isPending}
            />
            <Box sx={{ mt: 3 }}>
              <TextField
                label="Upload Name"
                fullWidth
                value={uploadName}
                onChange={(e) => setUploadName(e.target.value)}
                margin="normal"
                helperText="Optional custom name for this upload"
              />
              <TextField
                label="Primary Site"
                fullWidth
                value={site}
                onChange={(e) => setSite(e.target.value)}
                margin="normal"
                helperText="Optional primary location/site"
              />
              <TextField
                label="Secondary Site"
                fullWidth
                value={site2}
                onChange={(e) => setSite2(e.target.value)}
                margin="normal"
                helperText="Optional secondary location/site"
              />
              <TextField
                label="BSF Factor"
                type="number"
                fullWidth
                value={bsfFactor}
                onChange={(e) => setBsfFactor(e.target.value)}
                margin="normal"
                inputProps={{ min: 0, max: 1, step: 0.01 }}
                helperText="Space utilization factor (0.0 - 1.0). Default: 0.63"
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseUploadDialog} disabled={uploadMutation.isPending}>
            Cancel
          </Button>
          <Button
            onClick={handleUpload}
            variant="contained"
            disabled={!selectedFile || uploadMutation.isPending}
            startIcon={<CloudUploadIcon />}
          >
            {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={deleteConfirmOpen}
        title="Delete Inventory Upload"
        message="Are you sure you want to delete this inventory upload? This will also delete all associated items and allocation results."
        onConfirm={handleDeleteConfirm}
        onCancel={() => {
          setDeleteConfirmOpen(false);
          setDeleteId(null);
        }}
      />

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
    </Container>
  );
}
