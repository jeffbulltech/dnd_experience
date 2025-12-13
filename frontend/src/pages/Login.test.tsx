import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, Mock } from 'vitest';
import Login from './Login';
import { useAuth } from '../contexts/AuthContext';

// Mock the AuthContext
vi.mock('../contexts/AuthContext', () => ({
    useAuth: vi.fn(),
}));

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
        ...actual,
        useNavigate: () => mockNavigate,
    };
});

describe('Login Page', () => {
    const mockLogin = vi.fn();

    beforeEach(() => {
        vi.clearAllMocks();
        (useAuth as Mock).mockReturnValue({
            login: mockLogin,
        });
    });

    const setup = () => {
        return render(
            <MemoryRouter>
                <Login />
            </MemoryRouter>
        );
    };

    test('renders login form', () => {
        setup();
        expect(screen.getByText(/Welcome back, adventurer/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Sign In/i })).toBeInTheDocument();
    });

    test('calls login with credentials on submit', async () => {
        setup();

        // Fill out form
        fireEvent.change(screen.getByLabelText(/Username/i), { target: { value: 'testuser' } });
        fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'password123' } });

        // Submit
        fireEvent.click(screen.getByRole('button', { name: /Sign In/i }));

        await waitFor(() => {
            expect(mockLogin).toHaveBeenCalledWith('testuser', 'password123');
        });

        // Check navigation on success
        expect(mockNavigate).toHaveBeenCalledWith('/campaigns', { replace: true });
    });

    test('displays error message on login failure', async () => {
        const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { });
        mockLogin.mockRejectedValue(new Error('Auth failed'));

        setup();

        // Fill out form
        fireEvent.change(screen.getByLabelText(/Username/i), { target: { value: 'testuser' } });
        fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'wrongpass' } });

        // Submit
        fireEvent.click(screen.getByRole('button', { name: /Sign In/i }));

        await waitFor(() => {
            expect(screen.getByText(/Invalid credentials, please try again/i)).toBeInTheDocument();
        });

        expect(mockNavigate).not.toHaveBeenCalled();
        consoleSpy.mockRestore();
    });
});
