"""Report generation service for allocation results."""
import io
import csv
from datetime import datetime
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.extensions import db
from app.models import AllocationResult, SavedReport


class ReportService:
    """Service for generating and managing allocation reports."""

    @staticmethod
    def generate_html_report(result_id: int) -> str:
        """
        Generate HTML report for an allocation result.

        Args:
            result_id: AllocationResult ID

        Returns:
            HTML string

        Raises:
            ValueError: If result not found
        """
        result = AllocationResult.query.get(result_id)
        if not result:
            raise ValueError(f"Allocation result {result_id} not found")

        # Setup Jinja2 environment
        import os
        template_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'templates'
        )
        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

        # Load template
        template = env.get_template('allocation_report.html')

        # Prepare data for template
        allocation_data = result.allocation_data
        summary = allocation_data.get('summary', {})
        zone_allocations = allocation_data.get('zone_allocations', [])
        failures = allocation_data.get('failures', [])

        # Render template
        html = template.render(
            result=result,
            summary=summary,
            zone_allocations=zone_allocations,
            failures=failures,
            generated_at=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            warehouse_name=result.warehouse.name if result.warehouse else 'Unknown',
            upload_name=result.upload.upload_name if result.upload else 'Unknown'
        )

        return html

    @staticmethod
    def generate_pdf_report(result_id: int) -> bytes:
        """
        Generate PDF report for an allocation result.

        Args:
            result_id: AllocationResult ID

        Returns:
            PDF binary data

        Raises:
            ValueError: If result not found
            RuntimeError: If WeasyPrint is not available
        """
        # Lazy import WeasyPrint (requires GTK libraries on Windows)
        try:
            from weasyprint import HTML
        except (ImportError, OSError) as e:
            raise RuntimeError(
                "WeasyPrint not available. PDF export requires GTK libraries. "
                "See: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation"
            ) from e

        # Generate HTML first
        html_content = ReportService.generate_html_report(result_id)

        # Convert HTML to PDF using WeasyPrint
        pdf_file = HTML(string=html_content).write_pdf()

        return pdf_file

    @staticmethod
    def generate_csv_export(result_id: int) -> str:
        """
        Generate CSV export of allocation items.

        Args:
            result_id: AllocationResult ID

        Returns:
            CSV string

        Raises:
            ValueError: If result not found
        """
        result = AllocationResult.query.get(result_id)
        if not result:
            raise ValueError(f"Allocation result {result_id} not found")

        allocation_data = result.allocation_data
        zone_allocations = allocation_data.get('zone_allocations', [])

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Zone Name',
            'Item Name',
            'Category',
            'Quantity',
            'Height (ft)',
            'Area (sq ft)',
            'Weight (lbs)',
            'PSF',
            'Service Branch',
            'Priority Order',
            'Requires Climate Control',
            'Requires Special Handling'
        ])

        # Write allocated items
        for zone_alloc in zone_allocations:
            zone_name = zone_alloc.get('zone_info', {}).get('name', 'Unknown')
            for item in zone_alloc.get('allocated_items', []):
                writer.writerow([
                    zone_name,
                    item.get('name', ''),
                    item.get('category', ''),
                    item.get('quantity', 0),
                    item.get('height', 0),
                    item.get('area', 0),
                    item.get('weight', 0),
                    item.get('psf', 0),
                    item.get('service_branch', ''),
                    item.get('priority_order', 999),
                    item.get('requires_climate_control', False),
                    item.get('requires_special_handling', False)
                ])

        # Add failures section
        failures = allocation_data.get('failures', [])
        if failures:
            writer.writerow([])  # Empty row
            writer.writerow(['FAILED ALLOCATIONS'])
            writer.writerow([
                'Item Name',
                'Category',
                'Quantity',
                'Height (ft)',
                'Area (sq ft)',
                'Weight (lbs)',
                'PSF',
                'Failure Reason'
            ])

            for failure in failures:
                writer.writerow([
                    failure.get('name', ''),
                    failure.get('category', ''),
                    failure.get('quantity', 0),
                    failure.get('height', 0),
                    failure.get('area', 0),
                    failure.get('weight', 0),
                    failure.get('psf', 0),
                    failure.get('failure_reason', '')
                ])

        return output.getvalue()

    @staticmethod
    def save_report(allocation_id: int,
                   report_type: str,
                   file_path: str = None,
                   report_data: Dict[str, Any] = None) -> SavedReport:
        """
        Save a report record to the database.

        Args:
            allocation_id: AllocationResult ID
            report_type: Type of report (HTML, PDF, CSV)
            file_path: Optional path to saved file
            report_data: Optional additional report metadata

        Returns:
            SavedReport object

        Raises:
            ValueError: If allocation result not found or invalid type
        """
        # Validate allocation exists
        allocation = AllocationResult.query.get(allocation_id)
        if not allocation:
            raise ValueError(f"Allocation result {allocation_id} not found")

        # Validate report type
        valid_types = ['HTML', 'PDF', 'CSV', 'Excel']
        if report_type not in valid_types:
            raise ValueError(f"Report type must be one of: {', '.join(valid_types)}")

        # Create report record
        report = SavedReport(
            allocation_id=allocation_id,
            report_name=f"{allocation.result_name or 'Allocation'}_{report_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            report_type=report_type,
            file_path=file_path,
            report_data=report_data or {}
        )

        db.session.add(report)
        db.session.commit()

        return report

    @staticmethod
    def get_reports_for_allocation(allocation_id: int) -> list:
        """
        Get all saved reports for an allocation result.

        Args:
            allocation_id: AllocationResult ID

        Returns:
            List of SavedReport objects
        """
        return SavedReport.query.filter_by(allocation_id=allocation_id).order_by(
            SavedReport.created_at.desc()
        ).all()
