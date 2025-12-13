import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Alert,
  Divider,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  PlayArrow as PlayArrowIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  ExpandMore as ExpandMoreIcon,
  Warehouse as WarehouseIcon,
  Inventory as InventoryIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { inventoryApi } from '../api/inventory';
import { warehouseApi } from '../api/warehouses';
import { allocationApi } from '../api/allocation';
import type { AllocationResult } from '../types/allocation';

export default function AllocationPlanner() {
  const queryClient = useQueryClient();

  const [selectedUploadId, setSelectedUploadId] = useState<number | ''>('');
  const [selectedWarehouseId, setSelectedWarehouseId] = useState<number | ''>('');
  const [bsfFactor, setBsfFactor] = useState('0.63');
  const [resultName, setResultName] = useState('');
  const [allocationResult, setAllocationResult] = useState<AllocationResult | null>(null);
  const [error, setError] = useState('');

  const { data: uploads = [] } = useQuery({
    queryKey: ['inventory-uploads'],
    queryFn: inventoryApi.getUploads,
  });

  const { data: warehouses = [] } = useQuery({
    queryKey: ['warehouses'],
    queryFn: warehouseApi.getAll,
  });

  const allocationMutation = useMutation({
    mutationFn: allocationApi.runAllocation,
    onSuccess: (data) => {
      setAllocationResult(data);
      setError('');
      queryClient.invalidateQueries({ queryKey: ['allocation-results'] });
    },
    onError: (error: any) => {
      setError(error.response?.data?.message || 'Failed to run allocation');
      setAllocationResult(null);
    },
  });

  const handleRunAllocation = () => {
    if (!selectedUploadId || !selectedWarehouseId) {
      setError('Please select both inventory upload and warehouse');
      return;
    }

    const bsfValue = parseFloat(bsfFactor);
    if (isNaN(bsfValue) || bsfValue < 0 || bsfValue > 1) {
      setError('BSF factor must be between 0.0 and 1.0');
      return;
    }

    allocationMutation.mutate({
      upload_id: selectedUploadId as number,
      warehouse_id: selectedWarehouseId as number,
      bsf_factor: bsfValue,
      result_name: resultName || undefined,
    });
  };

  const selectedUpload = uploads.find((u) => u.id === selectedUploadId);
  const selectedWarehouse = warehouses.find((w) => w.id === selectedWarehouseId);

  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Allocation Planner
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Optimize warehouse space usage with multi-constraint allocation analysis
        </Typography>

        <Grid container spacing={3}>
          {/* Left Panel - Control Panel */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Configuration
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <FormControl fullWidth margin="normal">
                <InputLabel>Inventory Upload</InputLabel>
                <Select
                  value={selectedUploadId}
                  onChange={(e) => setSelectedUploadId(e.target.value as number)}
                  label="Inventory Upload"
                >
                  {uploads.map((upload) => (
                    <MenuItem key={upload.id} value={upload.id}>
                      {upload.upload_name} ({upload.total_items} items)
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {selectedUpload && (
                <Card variant="outlined" sx={{ mt: 2, bgcolor: 'action.hover' }}>
                  <CardContent>
                    <Typography variant="caption" color="text.secondary">
                      Selected Inventory
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="body2">
                        <strong>Items:</strong> {selectedUpload.total_items}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Weight:</strong> {selectedUpload.total_weight.toLocaleString()} lbs
                      </Typography>
                      <Typography variant="body2">
                        <strong>Area:</strong> {selectedUpload.total_area.toLocaleString()} sq ft
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              )}

              <FormControl fullWidth margin="normal" sx={{ mt: 3 }}>
                <InputLabel>Warehouse</InputLabel>
                <Select
                  value={selectedWarehouseId}
                  onChange={(e) => setSelectedWarehouseId(e.target.value as number)}
                  label="Warehouse"
                >
                  {warehouses.map((warehouse) => (
                    <MenuItem key={warehouse.id} value={warehouse.id}>
                      {warehouse.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {selectedWarehouse && (
                <Card variant="outlined" sx={{ mt: 2, bgcolor: 'action.hover' }}>
                  <CardContent>
                    <Typography variant="caption" color="text.secondary">
                      Selected Warehouse
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="body2">
                        <strong>Area:</strong> {selectedWarehouse.total_area?.toLocaleString()} sq ft
                      </Typography>
                      <Typography variant="body2">
                        <strong>Volume:</strong> {selectedWarehouse.total_volume?.toLocaleString()} cu ft
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              )}

              <TextField
                label="BSF Factor"
                type="number"
                fullWidth
                value={bsfFactor}
                onChange={(e) => setBsfFactor(e.target.value)}
                margin="normal"
                inputProps={{ min: 0, max: 1, step: 0.01 }}
                helperText="Space utilization factor (0.0 - 1.0)"
                sx={{ mt: 3 }}
              />

              <TextField
                label="Result Name (Optional)"
                fullWidth
                value={resultName}
                onChange={(e) => setResultName(e.target.value)}
                margin="normal"
                helperText="Custom name for this allocation"
              />

              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}

              <Button
                variant="contained"
                fullWidth
                size="large"
                startIcon={<PlayArrowIcon />}
                onClick={handleRunAllocation}
                disabled={!selectedUploadId || !selectedWarehouseId || allocationMutation.isPending}
                sx={{ mt: 3 }}
              >
                {allocationMutation.isPending ? 'Running Analysis...' : 'Run Allocation'}
              </Button>
            </Paper>
          </Grid>

          {/* Right Panel - Results */}
          <Grid item xs={12} md={8}>
            {allocationMutation.isPending && (
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Running Allocation Analysis...
                </Typography>
                <LinearProgress sx={{ mt: 2 }} />
              </Paper>
            )}

            {allocationResult && (
              <Box>
                {/* Summary Cards */}
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Card>
                      <CardContent>
                        <Typography variant="caption" color="text.secondary">
                          Overall Fit
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                          {allocationResult.overall_fit ? (
                            <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                          ) : (
                            <ErrorIcon color="error" sx={{ mr: 1 }} />
                          )}
                          <Typography variant="h6">
                            {allocationResult.overall_fit ? 'Success' : 'Partial'}
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Card>
                      <CardContent>
                        <Typography variant="caption" color="text.secondary">
                          Allocated Items
                        </Typography>
                        <Typography variant="h5" sx={{ mt: 1 }}>
                          {allocationResult.total_allocated}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          of {allocationResult.allocation_data.summary.total_items} total
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Card>
                      <CardContent>
                        <Typography variant="caption" color="text.secondary">
                          Allocation Rate
                        </Typography>
                        <Typography variant="h5" sx={{ mt: 1 }}>
                          {allocationResult.allocation_data.summary.allocation_rate.toFixed(1)}%
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Card>
                      <CardContent>
                        <Typography variant="caption" color="text.secondary">
                          Space Utilization
                        </Typography>
                        <Typography variant="h5" sx={{ mt: 1 }}>
                          {allocationResult.allocation_data.summary.overall_utilization.toFixed(1)}%
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                {/* Zone Allocations */}
                <Paper sx={{ p: 3, mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Zone Allocations
                  </Typography>
                  {allocationResult.allocation_data.zone_allocations.map((zoneAlloc, idx) => (
                    <Accordion key={idx}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                          <WarehouseIcon sx={{ mr: 1, color: 'text.secondary' }} />
                          <Typography sx={{ flexGrow: 1 }}>
                            {zoneAlloc.zone_info.name}
                          </Typography>
                          <Chip
                            label={`${zoneAlloc.total_items} items`}
                            size="small"
                            sx={{ mr: 1 }}
                          />
                          <Chip
                            label={`${zoneAlloc.area_utilization.toFixed(1)}% used`}
                            size="small"
                            color={zoneAlloc.area_utilization > 80 ? 'warning' : 'default'}
                          />
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <TableContainer>
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell>Item</TableCell>
                                <TableCell>Category</TableCell>
                                <TableCell align="right">Qty</TableCell>
                                <TableCell align="right">Height (ft)</TableCell>
                                <TableCell align="right">Area (sq ft)</TableCell>
                                <TableCell align="right">Weight (lbs)</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {zoneAlloc.allocated_items.map((item, itemIdx) => (
                                <TableRow key={itemIdx}>
                                  <TableCell>{item.name}</TableCell>
                                  <TableCell>{item.category || '-'}</TableCell>
                                  <TableCell align="right">{item.quantity}</TableCell>
                                  <TableCell align="right">{item.height.toFixed(1)}</TableCell>
                                  <TableCell align="right">{item.total_area.toFixed(1)}</TableCell>
                                  <TableCell align="right">{item.total_weight.toLocaleString()}</TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Paper>

                {/* Failed Allocations */}
                {allocationResult.allocation_data.failures.length > 0 && (
                  <Paper sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom color="error">
                      Failed Allocations ({allocationResult.total_failed} items)
                    </Typography>
                    <TableContainer>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Item</TableCell>
                            <TableCell>Category</TableCell>
                            <TableCell align="right">Qty</TableCell>
                            <TableCell>Failure Reason</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {allocationResult.allocation_data.failures.map((failure, idx) => (
                            <TableRow key={idx}>
                              <TableCell>{failure.name}</TableCell>
                              <TableCell>{failure.category || '-'}</TableCell>
                              <TableCell align="right">{failure.quantity}</TableCell>
                              <TableCell>
                                <Typography variant="body2" color="error">
                                  {failure.failure_reason}
                                </Typography>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Paper>
                )}
              </Box>
            )}

            {!allocationMutation.isPending && !allocationResult && (
              <Paper sx={{ p: 6, textAlign: 'center' }}>
                <InventoryIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Ready to Run Allocation
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Select an inventory upload and warehouse, then click "Run Allocation" to begin
                </Typography>
              </Paper>
            )}
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
}
