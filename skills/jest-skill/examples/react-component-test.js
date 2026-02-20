/**
 * React组件测试示例
 * 
 * 展示如何使用Jest和React Testing Library测试React组件
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserProfile } from '../components/UserProfile';
import { api } from '../services/api';

// Mock API模块
jest.mock('../services/api', () => ({
  api: {
    getUser: jest.fn(),
    updateUser: jest.fn()
  }
}));

describe('UserProfile Component', () => {
  const mockUser = {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    avatar: 'https://example.com/avatar.jpg'
  };

  beforeEach(() => {
    jest.clearAllMocks();
    api.getUser.mockResolvedValue({ data: mockUser });
  });

  describe('Rendering', () => {
    test('should render user information correctly', async () => {
      // Arrange
      render(<UserProfile userId={1} />);

      // Assert
      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
        expect(screen.getByText('john@example.com')).toBeInTheDocument();
      });
    });

    test('should display loading state initially', () => {
      // Arrange
      render(<UserProfile userId={1} />);

      // Assert
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });

    test('should match snapshot', async () => {
      // Arrange
      const { container } = render(<UserProfile userId={1} />);

      // Assert
      await waitFor(() => {
        expect(container.firstChild).toMatchSnapshot();
      });
    });
  });

  describe('Interactions', () => {
    test('should call updateUser when save button is clicked', async () => {
      // Arrange
      api.updateUser.mockResolvedValue({ data: { ...mockUser, name: 'Jane Doe' } });
      render(<UserProfile userId={1} />);

      await waitFor(() => screen.getByText('John Doe'));

      // Act
      const editButton = screen.getByRole('button', { name: /edit/i });
      fireEvent.click(editButton);

      const nameInput = screen.getByLabelText(/name/i);
      await userEvent.clear(nameInput);
      await userEvent.type(nameInput, 'Jane Doe');

      const saveButton = screen.getByRole('button', { name: /save/i });
      fireEvent.click(saveButton);

      // Assert
      await waitFor(() => {
        expect(api.updateUser).toHaveBeenCalledWith(1, expect.objectContaining({
          name: 'Jane Doe'
        }));
      });
    });

    test('should handle API error gracefully', async () => {
      // Arrange
      const errorMessage = 'Failed to load user';
      api.getUser.mockRejectedValue(new Error(errorMessage));

      // Act
      render(<UserProfile userId={1} />);

      // Assert
      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    test('should have correct ARIA labels', async () => {
      // Arrange
      render(<UserProfile userId={1} />);

      // Assert
      await waitFor(() => {
        expect(screen.getByRole('img', { name: /profile picture/i })).toBeInTheDocument();
        expect(screen.getByRole('heading', { level: 2 })).toBeInTheDocument();
      });
    });

    test('should be keyboard navigable', async () => {
      // Arrange
      render(<UserProfile userId={1} />);
      await waitFor(() => screen.getByText('John Doe'));

      const editButton = screen.getByRole('button', { name: /edit/i });
      
      // Act
      editButton.focus();
      fireEvent.keyDown(editButton, { key: 'Enter', code: 'Enter' });

      // Assert
      expect(screen.getByLabelText(/name/i)).toHaveFocus();
    });
  });
});
