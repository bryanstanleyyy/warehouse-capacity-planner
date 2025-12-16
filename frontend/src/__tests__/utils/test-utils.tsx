/**
 * Custom render utilities for testing React components.
 *
 * This module provides a custom render function that wraps components
 * with all necessary providers (QueryClient, Router, Theme).
 */

import { ReactElement, ReactNode } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';

/**
 * Create a wrapper component with all necessary providers.
 */
function createWrapper() {
  // Create a new QueryClient for each test to ensure isolation
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false, // Don't retry failed queries in tests
        gcTime: 0, // Don't cache query results
      },
      mutations: {
        retry: false, // Don't retry failed mutations in tests
      },
    },
  });

  const theme = createTheme();

  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ThemeProvider theme={theme}>
            {children}
          </ThemeProvider>
        </BrowserRouter>
      </QueryClientProvider>
    );
  };
}

/**
 * Custom render function that wraps components with all providers.
 *
 * Usage:
 * ```tsx
 * import { render, screen } from '@/__tests__/utils/test-utils';
 *
 * test('renders component', () => {
 *   render(<MyComponent />);
 *   expect(screen.getByText('Hello')).toBeInTheDocument();
 * });
 * ```
 */
function customRender(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) {
  return render(ui, { wrapper: createWrapper(), ...options });
}

// Re-export everything from React Testing Library
export * from '@testing-library/react';

// Export custom render as default render
export { customRender as render };
