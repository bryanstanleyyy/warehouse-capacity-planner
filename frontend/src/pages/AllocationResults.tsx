import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  CircularProgress,
  Snackbar,
  Alert,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  OpenInNew as OpenInNewIcon,
  TableChart as TableChartIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import { allocationApi } from '../api/allocation';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { exportToHTML, viewHTMLReport, exportToCSV } from '../utils/exportUtils';

export default function AllocationResults() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [exportingFormat, setExportingFormat] = useState<{ id: number; format: 'html' | 'view' | 'csv' } | null>(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error',
  });

  const { data: results = [], isLoading } = useQuery({
    queryKey: ['allocation-results'],
    queryFn: () => allocationApi.getAllResults(),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => allocationApi.deleteResult(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['allocation-results'] });
      setSnackbar({
        open: true,
        message: 'Allocation result deleted successfully',
        severity: 'success',
      });
      setDeleteConfirmOpen(false);
      setDeleteId(null);
    },
    onError: () => {
      setSnackbar({
        open: true,
        message: 'Failed to delete allocation result',
        severity: 'error',
      });
    },
  });

  const handleDeleteClick = (id: number) => {
    setDeleteId(id);
    setDeleteConfirmOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (deleteId !== null) {
      deleteMutation.mutate(deleteId);
    }
  };

  const handleViewReport = async (id: number) => {
    setExportingFormat({ id, format: 'view' });
    try {
      await viewHTMLReport(id);
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to view report',
        severity: 'error',
      });
    } finally {
      setExportingFormat(null);
    }
  };

  const handleExportHTML = async (id: number, name?: string) => {
    setExportingFormat({ id, format: 'html' });
    try {
      await exportToHTML(id, name);
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to export HTML',
        severity: 'error',
      });
    } finally {
      setExportingFormat(null);
    }
  };

  const handleExportCSV = async (id: number, name?: string) => {
    setExportingFormat({ id, format: 'csv' });
    try {
      await exportToCSV(id, name);
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to export CSV',
        severity: 'error',
      });
    } finally {
      setExportingFormat(null);
    }
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

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Typography variant="h4" component="h1">
            Allocation Results
          </Typography>
        </Box>

        {results.length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              No allocation results yet
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Run an allocation to see results here
            </Typography>
          </Paper>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Result Name</TableCell>
                  <TableCell>Upload ID</TableCell>
                  <TableCell>Warehouse ID</TableCell>
                  <TableCell align="right">BSF Factor</TableCell>
                  <TableCell align="right">Allocated</TableCell>
                  <TableCell align="right">Failed</TableCell>
                  <TableCell align="center">All Fit</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.map((result) => (
                  <TableRow key={result.id} hover>
                    <TableCell>
                      <Typography variant="body1" fontWeight="medium">
                        {result.result_name || `Result #${result.id}`}
                      </Typography>
                    </TableCell>
                    <TableCell>{result.upload_id}</TableCell>
                    <TableCell>{result.warehouse_id}</TableCell>
                    <TableCell align="right">{result.bsf_factor}</TableCell>
                    <TableCell align="right">{result.total_allocated}</TableCell>
                    <TableCell align="right">
                      {result.total_failed > 0 && (
                        <Chip
                          label={result.total_failed}
                          size="small"
                          color="error"
                          icon={<ErrorIcon />}
                        />
                      )}
                      {result.total_failed === 0 && result.total_failed}
                    </TableCell>
                    <TableCell align="center">
                      {result.overall_fit ? (
                        <CheckCircleIcon color="success" />
                      ) : (
                        <ErrorIcon color="error" />
                      )}
                    </TableCell>
                    <TableCell>{formatDate(result.created_at)}</TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => handleViewReport(result.id)}
                        title="View Report"
                        disabled={exportingFormat?.id === result.id}
                      >
                        <OpenInNewIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleExportHTML(result.id, result.result_name)}
                        title="Export HTML"
                        disabled={exportingFormat?.id === result.id}
                      >
                        <DownloadIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleExportCSV(result.id, result.result_name)}
                        title="Export CSV"
                        disabled={exportingFormat?.id === result.id}
                      >
                        <TableChartIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteClick(result.id)}
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

      <ConfirmDialog
        open={deleteConfirmOpen}
        title="Delete Allocation Result"
        message="Are you sure you want to delete this allocation result? This action cannot be undone."
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
