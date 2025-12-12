import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import theme from './theme';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import WarehouseManagement from './pages/WarehouseManagement';
import WarehouseDetail from './pages/WarehouseDetail';
import InventoryManagement from './pages/InventoryManagement';
import AllocationPlanner from './pages/AllocationPlanner';

// Create QueryClient for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<MainLayout />}>
              <Route index element={<Dashboard />} />
              <Route path="warehouses" element={<WarehouseManagement />} />
              <Route path="warehouses/:id" element={<WarehouseDetail />} />
              <Route path="inventory" element={<InventoryManagement />} />
              <Route path="allocation" element={<AllocationPlanner />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
