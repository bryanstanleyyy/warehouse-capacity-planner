/**
 * Tests for FileUploadZone component
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '../utils/test-utils';
import { FileUploadZone } from '../../components/inventory/FileUploadZone';

describe('FileUploadZone', () => {
  it('renders upload zone', () => {
    render(<FileUploadZone onFileSelect={vi.fn()} />);

    expect(screen.getByText(/drag.*drop.*excel file/i)).toBeInTheDocument();
  });

  it('calls onFileSelect with valid file', async () => {
    const handleFileSelect = vi.fn();
    render(<FileUploadZone onFileSelect={handleFileSelect} />);

    const file = new File(['test'], 'test.xlsx', {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    });

    const input = document.querySelector('#file-upload-input') as HTMLInputElement;

    // Simulate file selection by setting files property and triggering change
    Object.defineProperty(input, 'files', {
      value: [file],
      writable: false,
    });

    // Trigger change event
    const event = new Event('change', { bubbles: true });
    input.dispatchEvent(event);

    // Should call onFileSelect with the file
    expect(handleFileSelect).toHaveBeenCalledWith(file);
  });

  it('shows error for invalid file type', () => {
    const handleFileSelect = vi.fn();
    render(<FileUploadZone onFileSelect={handleFileSelect} accept=".xlsx,.xls" />);

    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });

    const input = document.querySelector('#file-upload-input') as HTMLInputElement;

    // Simulate file selection
    Object.defineProperty(input, 'files', {
      value: [file],
      writable: false,
    });

    const event = new Event('change', { bubbles: true });
    input.dispatchEvent(event);

    // Should show error and not call onFileSelect
    expect(screen.getByText(/invalid file type/i)).toBeInTheDocument();
    expect(handleFileSelect).not.toHaveBeenCalled();
  });

  it('shows error for file exceeding size limit', () => {
    const handleFileSelect = vi.fn();
    render(<FileUploadZone onFileSelect={handleFileSelect} maxSize={1} />);

    // Create a 2MB file (exceeds 1MB limit)
    const largeContent = 'a'.repeat(2 * 1024 * 1024);
    const file = new File([largeContent], 'large.xlsx', {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    });

    const input = document.querySelector('#file-upload-input') as HTMLInputElement;

    // Simulate file selection
    Object.defineProperty(input, 'files', {
      value: [file],
      writable: false,
    });

    const event = new Event('change', { bubbles: true });
    input.dispatchEvent(event);

    // Should show error
    expect(screen.getByText(/file size exceeds/i)).toBeInTheDocument();
    expect(handleFileSelect).not.toHaveBeenCalled();
  });

  it('disables interaction when disabled prop is true', () => {
    render(<FileUploadZone onFileSelect={vi.fn()} disabled={true} />);

    const input = document.querySelector('#file-upload-input') as HTMLInputElement;
    expect(input).toBeDisabled();
  });

  it('shows progress indicator when uploading', () => {
    render(<FileUploadZone onFileSelect={vi.fn()} uploading={true} />);

    // Should show progress or uploading state
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });
});
