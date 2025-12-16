import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import theme from './theme';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import WarehouseManagement from './pages/WarehouseManagement';
import WarehouseDetail from './pages/WarehouseDetail';
import InventoryManagement from './pages/InventoryManagement';
import InventoryDetail from './pages/InventoryDetail';
import AllocationPlanner from './pages/AllocationPlanner';
import AllocationResults from './pages/AllocationResults';

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
              <Route path="inventory/:id" element={<InventoryDetail />} />
              <Route path="allocation" element={<AllocationPlanner />} />
              <Route path="results" element={<AllocationResults />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
