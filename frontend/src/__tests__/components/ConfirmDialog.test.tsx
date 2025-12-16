/**
 * Tests for ConfirmDialog component
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '../utils/test-utils';
import { ConfirmDialog } from '../../components/common/ConfirmDialog';
import userEvent from '@testing-library/user-event';

describe('ConfirmDialog', () => {
  it('renders dialog when open', () => {
    render(
      <ConfirmDialog
        open={true}
        title="Test Title"
        message="Test message"
        onConfirm={vi.fn()}
        onCancel={vi.fn()}
      />
    );

    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Test message')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(
      <ConfirmDialog
        open={false}
        title="Test Title"
        message="Test message"
        onConfirm={vi.fn()}
        onCancel={vi.fn()}
      />
    );

    expect(screen.queryByText('Test Title')).not.toBeInTheDocument();
  });

  it('calls onConfirm when confirm button is clicked', async () => {
    const user = userEvent.setup();
    const handleConfirm = vi.fn();

    render(
      <ConfirmDialog
        open={true}
        title="Test Title"
        message="Test message"
        onConfirm={handleConfirm}
        onCancel={vi.fn()}
      />
    );

    const confirmButton = screen.getByRole('button', { name: /confirm/i });
    await user.click(confirmButton);

    expect(handleConfirm).toHaveBeenCalledTimes(1);
  });

  it('calls onCancel when cancel button is clicked', async () => {
    const user = userEvent.setup();
    const handleCancel = vi.fn();

    render(
      <ConfirmDialog
        open={true}
        title="Test Title"
        message="Test message"
        onConfirm={vi.fn()}
        onCancel={handleCancel}
      />
    );

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await user.click(cancelButton);

    expect(handleCancel).toHaveBeenCalledTimes(1);
  });

  it('displays custom button text', () => {
    render(
      <ConfirmDialog
        open={true}
        title="Test Title"
        message="Test message"
        onConfirm={vi.fn()}
        onCancel={vi.fn()}
        confirmText="Delete"
        cancelText="Keep"
      />
    );

    expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /keep/i })).toBeInTheDocument();
  });

  it('uses default button text when not provided', () => {
    render(
      <ConfirmDialog
        open={true}
        title="Test Title"
        message="Test message"
        onConfirm={vi.fn()}
        onCancel={vi.fn()}
      />
    );

    expect(screen.getByRole('button', { name: /confirm/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
  });
});
