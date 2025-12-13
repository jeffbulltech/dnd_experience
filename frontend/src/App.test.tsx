import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';
import App from './App';

const queryClient = new QueryClient();

test('smoke test: renders login page by default', () => {
    render(
        <QueryClientProvider client={queryClient}>
            <AuthProvider>
                <MemoryRouter>
                    <App />
                </MemoryRouter>
            </AuthProvider>
        </QueryClientProvider>
    );

    expect(screen.getByText(/Welcome back, adventurer/i)).toBeInTheDocument();
});
