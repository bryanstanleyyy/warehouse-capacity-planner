import { Box, Typography } from '@mui/material';

export default function InventoryManagement() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Inventory Management
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Upload and manage inventory data from Excel files
      </Typography>
    </Box>
  );
}
