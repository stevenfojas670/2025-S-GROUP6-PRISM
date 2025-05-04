import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LoginComponent from '@/components/LoginComponent';
import { signIn } from 'next-auth/react';

// Mock router
const push = jest.fn();

jest.mock('next/navigation', () => ({
	useRouter: () => ({
		push,
		replace: jest.fn(),
		refresh: jest.fn(),
		prefetch: jest.fn(),
	}),
}));

// Mock next-auth
jest.mock('next-auth/react', () => ({
	signIn: jest.fn(),
}));

// Mock AuthContext
jest.mock('@/context/AuthContext', () => ({
	useAuth: () => ({
		user: { isLoggedIn: false },
		login: jest.fn(),
	}),
}));

// Mock fetch
global.fetch = jest.fn(() =>
	Promise.resolve({
		ok: true,
		json: () => Promise.resolve({ user: { username: 'testuser' } }),
	})
);

describe('LoginComponent', () => {
	beforeEach(() => {
		jest.clearAllMocks();
	});

	test('renders login form with username and password fields', () => {
		render(<LoginComponent />);
		expect(screen.getByLabelText('Username')).toBeInTheDocument();
		expect(screen.getByLabelText('Password')).toBeInTheDocument();
		expect(screen.getByTestId('login-submit')).toBeInTheDocument();
		expect(screen.getByTestId('google-sign-in')).toBeInTheDocument();
	});

	test('allows the user to type in the username and password fields', () => {
		render(<LoginComponent />);
		const usernameInput = screen.getByLabelText('Username');
		const passwordInput = screen.getByLabelText('Password');
		fireEvent.change(usernameInput, { target: { value: 'testuser' } });
		fireEvent.change(passwordInput, { target: { value: 'password123' } });
		expect(usernameInput).toHaveValue('testuser');
		expect(passwordInput).toHaveValue('password123');
	});

	test('redirects to semesters on successful login', async () => {
		render(<LoginComponent />);
		fireEvent.change(screen.getByLabelText('Username'), {
			target: { value: 'testuser' },
		});
		fireEvent.change(screen.getByLabelText('Password'), {
			target: { value: 'password123' },
		});
		fireEvent.click(screen.getByTestId('login-submit'));

		await waitFor(() => {
			expect(push).toHaveBeenCalledWith('/semesters/');
		});
	});

	test('displays error message on failed login', async () => {
		global.fetch.mockImplementationOnce(() =>
			Promise.resolve({
				ok: false,
				json: () =>
					Promise.resolve({ non_field_errors: ['Invalid credentials'] }),
			})
		);
		render(<LoginComponent />);
		fireEvent.change(screen.getByLabelText('Username'), {
			target: { value: 'wronguser' },
		});
		fireEvent.change(screen.getByLabelText('Password'), {
			target: { value: 'wrongpassword' },
		});
		fireEvent.click(screen.getByTestId('login-submit'));

		await waitFor(() => {
			expect(screen.getByRole('alert')).toHaveTextContent(
				/invalid credentials/i
			);
		});
	});

	test('does not submit if fields are empty', async () => {
		render(<LoginComponent />);
		await waitFor(() => {
			expect(screen.getByTestId('login-submit')).toBeInTheDocument();
		});
		fireEvent.click(screen.getByTestId('login-submit'));
		expect(global.fetch).not.toHaveBeenCalled();
		expect(screen.getByRole('alert')).toHaveTextContent(
			/username and password are required/i
		);
	});

	test('disables login button during submission', async () => {
		render(<LoginComponent />);
		fireEvent.change(screen.getByLabelText('Username'), {
			target: { value: 'testuser' },
		});
		fireEvent.change(screen.getByLabelText('Password'), {
			target: { value: 'password123' },
		});

		const loginButton = screen.getByTestId('login-submit');
		fireEvent.click(loginButton);

		await waitFor(() => expect(loginButton).toBeDisabled(), { timeout: 500 });
		await waitFor(() => expect(loginButton).not.toBeDisabled(), {
			timeout: 1000,
		});
	});

	test('clicking Google Sign In calls signIn', () => {
		render(<LoginComponent />);
		const googleButton = screen.getByTestId('google-sign-in');
		fireEvent.click(googleButton);

		expect(signIn).toHaveBeenCalled();
	});
});
