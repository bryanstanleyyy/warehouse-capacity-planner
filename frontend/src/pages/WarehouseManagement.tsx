import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Snackbar,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import WarehouseIcon from '@mui/icons-material/Warehouse';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { warehouseApi } from '../api/warehouses';
import type { Warehouse, WarehouseInput } from '../types/warehouse';
import ConfirmDialog from '../components/common/ConfirmDialog';

export default function WarehouseManagement() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedWarehouse, setSelectedWarehouse] = useState<Warehouse | null>(null);
  const [formData, setFormData] = useState<WarehouseInput>({
    name: '',
    warehouse_type: '',
    description: '',
    is_custom: true,
  });
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });

  // Query for fetching warehouses
  const { data: warehouses = [], isLoading } = useQuery({
    queryKey: ['warehouses'],
    queryFn: () => warehouseApi.getAll(),
  });

  // Mutation for creating warehouse
  const createMutation = useMutation({
    mutationFn: (data: WarehouseInput) => warehouseApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
      setDialogOpen(false);
      setSnackbar({ open: true, message: 'Warehouse created successfully', severity: 'success' });
      resetForm();
    },
    onError: (error: any) => {
      setSnackbar({ open: true, message: error.response?.data?.message || 'Error creating warehouse', severity: 'error' });
    },
  });

  // Mutation for updating warehouse
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: WarehouseInput }) =>
      warehouseApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
      setDialogOpen(false);
      setSnackbar({ open: true, message: 'Warehouse updated successfully', severity: 'success' });
      resetForm();
    },
    onError: (error: any) => {
      setSnackbar({ open: true, message: error.response?.data?.message || 'Error updating warehouse', severity: 'error' });
    },
  });

  // Mutation for deleting warehouse
  const deleteMutation = useMutation({
    mutationFn: (id: number) => warehouseApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
      setDeleteDialogOpen(false);
      setSnackbar({ open: true, message: 'Warehouse deleted successfully', severity: 'success' });
      setSelectedWarehouse(null);
    },
    onError: (error: any) => {
      setSnackbar({ open: true, message: error.response?.data?.message || 'Error deleting warehouse', severity: 'error' });
    },
  });

  const handleOpenDialog = (warehouse?: Warehouse) => {
    if (warehouse) {
      setSelectedWarehouse(warehouse);
      setFormData({
        name: warehouse.name,
        warehouse_type: warehouse.warehouse_type || '',
        description: warehouse.description || '',
        is_custom: warehouse.is_custom,
      });
    } else {
      resetForm();
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    resetForm();
  };

  const handleSubmit = () => {
    if (selectedWarehouse) {
      updateMutation.mutate({ id: selectedWarehouse.id!, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleDelete = (warehouse: Warehouse) => {
    setSelectedWarehouse(warehouse);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (selectedWarehouse?.id) {
      deleteMutation.mutate(selectedWarehouse.id);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      warehouse_type: '',
      description: '',
      is_custom: true,
    });
    setSelectedWarehouse(null);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Warehouse Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Create Warehouse
        </Button>
      </Box>

      <Typography variant="body1" color="text.secondary" paragraph>
        Manage warehouse facilities and storage zones
      </Typography>

      {isLoading ? (
        <Typography>Loading warehouses...</Typography>
      ) : warehouses.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 8 }}>
            <WarehouseIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No Warehouses Yet
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Create your first warehouse to get started
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleOpenDialog()}
            >
              Create Warehouse
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {warehouses.map((warehouse) => (
            <Grid item xs={12} md={6} lg={4} key={warehouse.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" component="div">
                      {warehouse.name}
                    </Typography>
                    <Box>
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog(warehouse)}
                        aria-label="edit"
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(warehouse)}
                        aria-label="delete"
                        color="error"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Box>
                  </Box>

                  {warehouse.warehouse_type && (
                    <Chip
                      label={warehouse.warehouse_type}
                      size="small"
                      sx={{ mb: 1 }}
                    />
                  )}

                  {warehouse.description && (
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {warehouse.description}
                    </Typography>
                  )}

                  <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <Box>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Zones
                      </Typography>
                      <Typography variant="body2" fontWeight="medium">
                        {warehouse.zone_count || 0}
                      </Typography>
                    </Box>
                    {warehouse.total_area && (
                      <Box>
                        <Typography variant="caption" color="text.secondary" display="block">
                          Total Area
                        </Typography>
                        <Typography variant="body2" fontWeight="medium">
                          {warehouse.total_area.toLocaleString()} sq ft
                        </Typography>
                      </Box>
                    )}
                  </Box>
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    onClick={() => navigate(`/warehouses/${warehouse.id}`)}
                  >
                    View Details
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {selectedWarehouse ? 'Edit Warehouse' : 'Create Warehouse'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Warehouse Name"
              fullWidth
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
            <TextField
              label="Warehouse Type"
              fullWidth
              value={formData.warehouse_type}
              onChange={(e) => setFormData({ ...formData, warehouse_type: e.target.value })}
              placeholder="e.g., Distribution Center, Cold Storage"
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={!formData.name || createMutation.isPending || updateMutation.isPending}
          >
            {selectedWarehouse ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={deleteDialogOpen}
        title="Delete Warehouse"
        message={`Are you sure you want to delete "${selectedWarehouse?.name}"? This will also delete all zones in this warehouse.`}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteDialogOpen(false)}
        confirmText="Delete"
      />

      {/* Snackbar for notifications */}
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
