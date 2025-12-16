/**
 * Export utilities for downloading allocation reports
 */

import { allocationApi } from '../api/allocation';

/**
 * Trigger browser download for a blob
 */
export function downloadFile(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

/**
 * Export allocation result as HTML
 */
export async function exportToHTML(resultId: number, resultName?: string): Promise<void> {
  try {
    const blob = await allocationApi.exportHTML(resultId);
    const filename = `${resultName || `allocation_${resultId}`}.html`;
    downloadFile(blob, filename);
  } catch (error) {
    console.error('Error exporting HTML:', error);
    throw new Error('Failed to export HTML report');
  }
}

/**
 * View allocation result as HTML in a new tab
 */
export async function viewHTMLReport(resultId: number): Promise<void> {
  try {
    const blob = await allocationApi.exportHTML(resultId);
    const url = window.URL.createObjectURL(blob);
    const newWindow = window.open(url, '_blank');

    // Clean up the object URL after the window loads
    if (newWindow) {
      newWindow.onload = () => {
        window.URL.revokeObjectURL(url);
      };
    } else {
      // If popup was blocked, clean up immediately
      window.URL.revokeObjectURL(url);
      throw new Error('Failed to open report. Please allow popups for this site.');
    }
  } catch (error) {
    console.error('Error viewing HTML report:', error);
    throw new Error('Failed to view HTML report');
  }
}

/**
 * Export allocation result as CSV
 */
export async function exportToCSV(resultId: number, resultName?: string): Promise<void> {
  try {
    const blob = await allocationApi.exportCSV(resultId);
    const filename = `${resultName || `allocation_${resultId}`}.csv`;
    downloadFile(blob, filename);
  } catch (error) {
    console.error('Error exporting CSV:', error);
    throw new Error('Failed to export CSV file');
  }
}
