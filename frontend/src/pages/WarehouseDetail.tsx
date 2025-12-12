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
  IconButton,
  Chip,
  Paper,
  Alert,
  Snackbar,
  CircularProgress,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import AcUnitIcon from '@mui/icons-material/AcUnit';
import WarningIcon from '@mui/icons-material/Warning';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { warehouseApi } from '../api/warehouses';
import type { Zone, ZoneInput } from '../types/warehouse';
import ZoneDialog from '../components/warehouse/ZoneDialog';
import ConfirmDialog from '../components/common/ConfirmDialog';

export default function WarehouseDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const warehouseId = parseInt(id || '0');

  const [zoneDialogOpen, setZoneDialogOpen] = useState(false);
  const [selectedZone, setSelectedZone] = useState<Zone | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  }>({
    open: false,
    message: '',
    severity: 'success',
  });

  // Query for warehouse details
  const { data: warehouse, isLoading } = useQuery({
    queryKey: ['warehouse', warehouseId],
    queryFn: () => warehouseApi.getById(warehouseId),
    enabled: !!warehouseId,
  });

  // Mutation for creating zone
  const createZoneMutation = useMutation({
    mutationFn: (data: ZoneInput) => warehouseApi.createZone(warehouseId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouse', warehouseId] });
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
      setZoneDialogOpen(false);
      setSnackbar({ open: true, message: 'Zone created successfully', severity: 'success' });
    },
    onError: (error: any) => {
      setSnackbar({
        open: true,
        message: error.response?.data?.message || 'Error creating zone',
        severity: 'error',
      });
    },
  });

  // Mutation for updating zone
  const updateZoneMutation = useMutation({
    mutationFn: ({ zoneId, data }: { zoneId: number; data: ZoneInput }) =>
      warehouseApi.updateZone(warehouseId, zoneId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouse', warehouseId] });
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
      setZoneDialogOpen(false);
      setSnackbar({ open: true, message: 'Zone updated successfully', severity: 'success' });
    },
    onError: (error: any) => {
      setSnackbar({
        open: true,
        message: error.response?.data?.message || 'Error updating zone',
        severity: 'error',
      });
    },
  });

  // Mutation for deleting zone
  const deleteZoneMutation = useMutation({
    mutationFn: (zoneId: number) => warehouseApi.deleteZone(warehouseId, zoneId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouse', warehouseId] });
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
      setDeleteDialogOpen(false);
      setSnackbar({ open: true, message: 'Zone deleted successfully', severity: 'success' });
      setSelectedZone(null);
    },
    onError: (error: any) => {
      setSnackbar({
        open: true,
        message: error.response?.data?.message || 'Error deleting zone',
        severity: 'error',
      });
    },
  });

  const handleOpenZoneDialog = (zone?: Zone) => {
    setSelectedZone(zone || null);
    setZoneDialogOpen(true);
  };

  const handleZoneSubmit = (data: ZoneInput) => {
    if (selectedZone?.id) {
      updateZoneMutation.mutate({ zoneId: selectedZone.id, data });
    } else {
      createZoneMutation.mutate(data);
    }
  };

  const handleDeleteZone = (zone: Zone) => {
    setSelectedZone(zone);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (selectedZone?.id) {
      deleteZoneMutation.mutate(selectedZone.id);
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!warehouse) {
    return (
      <Box>
        <Alert severity="error">Warehouse not found</Alert>
        <Button onClick={() => navigate('/warehouses')} sx={{ mt: 2 }}>
          Back to Warehouses
        </Button>
      </Box>
    );
  }

  const zones = warehouse.zones || [];

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <IconButton onClick={() => navigate('/warehouses')} sx={{ mr: 1 }}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" sx={{ flexGrow: 1 }}>
          {warehouse.name}
        </Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenZoneDialog()}>
          Add Zone
        </Button>
      </Box>

      {warehouse.warehouse_type && (
        <Chip label={warehouse.warehouse_type} sx={{ mb: 2 }} />
      )}

      {warehouse.description && (
        <Typography variant="body1" color="text.secondary" paragraph>
          {warehouse.description}
        </Typography>
      )}

      {/* Summary Cards */}
      <Box sx={{ display: 'flex', gap: 2, mb: 4, flexWrap: 'wrap' }}>
        <Card sx={{ minWidth: 200 }}>
          <CardContent>
            <Typography variant="caption" color="text.secondary" display="block">
              Total Zones
            </Typography>
            <Typography variant="h4">{zones.length}</Typography>
          </CardContent>
        </Card>
        <Card sx={{ minWidth: 200 }}>
          <CardContent>
            <Typography variant="caption" color="text.secondary" display="block">
              Total Area
            </Typography>
            <Typography variant="h4">
              {warehouse.total_area ? warehouse.total_area.toLocaleString() : '0'}{' '}
              <Typography variant="caption" component="span">
                sq ft
              </Typography>
            </Typography>
          </CardContent>
        </Card>
        <Card sx={{ minWidth: 200 }}>
          <CardContent>
            <Typography variant="caption" color="text.secondary" display="block">
              Total Volume
            </Typography>
            <Typography variant="h4">
              {warehouse.total_volume ? warehouse.total_volume.toLocaleString() : '0'}{' '}
              <Typography variant="caption" component="span">
                cu ft
              </Typography>
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Zones Table */}
      <Typography variant="h5" gutterBottom>
        Storage Zones
      </Typography>

      {zones.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="h6" gutterBottom>
              No Zones Yet
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Add storage zones to define capacity specifications
            </Typography>
            <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenZoneDialog()}>
              Add Zone
            </Button>
          </CardContent>
        </Card>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Zone Name</TableCell>
                <TableCell align="right">Area (sq ft)</TableCell>
                <TableCell align="right">Height (ft)</TableCell>
                <TableCell align="right">Strength (PSF)</TableCell>
                <TableCell align="right">Volume (cu ft)</TableCell>
                <TableCell>Features</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {zones
                .sort((a, b) => (a.zone_order || 0) - (b.zone_order || 0))
                .map((zone) => (
                  <TableRow key={zone.id}>
                    <TableCell component="th" scope="row">
                      {zone.name}
                    </TableCell>
                    <TableCell align="right">{zone.area?.toLocaleString()}</TableCell>
                    <TableCell align="right">{zone.height?.toLocaleString()}</TableCell>
                    <TableCell align="right">
                      {zone.strength ? zone.strength.toLocaleString() : '-'}
                    </TableCell>
                    <TableCell align="right">
                      {zone.volume ? zone.volume.toLocaleString() : '-'}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        {zone.climate_controlled && (
                          <Chip icon={<AcUnitIcon />} label="Climate" size="small" color="info" />
                        )}
                        {zone.special_handling && (
                          <Chip icon={<WarningIcon />} label="Special" size="small" color="warning" />
                        )}
                        {zone.is_weather_zone && (
                          <Chip label="Outdoor" size="small" variant="outlined" />
                        )}
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <IconButton size="small" onClick={() => handleOpenZoneDialog(zone)}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteZone(zone)}
                        color="error"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Zone Dialog */}
      <ZoneDialog
        open={zoneDialogOpen}
        zone={selectedZone}
        onClose={() => setZoneDialogOpen(false)}
        onSubmit={handleZoneSubmit}
        isLoading={createZoneMutation.isPending || updateZoneMutation.isPending}
      />

      {/* Delete Confirmation */}
      <ConfirmDialog
        open={deleteDialogOpen}
        title="Delete Zone"
        message={`Are you sure you want to delete "${selectedZone?.name}"?`}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteDialogOpen(false)}
        confirmText="Delete"
      />

      {/* Snackbar */}
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
