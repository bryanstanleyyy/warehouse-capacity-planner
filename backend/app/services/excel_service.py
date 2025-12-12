"""Excel file parsing service."""
import pandas as pd
from typing import List, Dict, Any, Optional


class ExcelParsingError(Exception):
    """Custom exception for Excel parsing errors."""
    pass


class ExcelService:
    """Service for parsing Excel files and extracting inventory data."""

    @staticmethod
    def parse_inventory_file(file_path: str) -> Dict[str, Any]:
        """Parse an Excel file and extract inventory data.

        Args:
            file_path: Path to the Excel file

        Returns:
            Dictionary containing parsed inventory data

        Raises:
            ExcelParsingError: If file cannot be parsed
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path)

            # Validate that we have data
            if df.empty:
                raise ExcelParsingError("Excel file is empty")

            # Clean column names (strip whitespace, lowercase)
            df.columns = df.columns.str.strip().str.lower()

            # Extract metadata
            metadata = {
                'total_rows': len(df),
                'columns': list(df.columns),
                'file_path': file_path
            }

            # Convert DataFrame to list of dictionaries
            items = df.to_dict('records')

            return {
                'items': items,
                'metadata': metadata
            }

        except FileNotFoundError:
            raise ExcelParsingError(f"File not found: {file_path}")
        except Exception as e:
            raise ExcelParsingError(f"Error parsing Excel file: {str(e)}")

    @staticmethod
    def extract_inventory_items(items: List[Dict[str, Any]],
                                site: Optional[str] = None,
                                site2: Optional[str] = None) -> List[Dict[str, Any]]:
        """Extract and normalize inventory items from parsed Excel data.

        Args:
            items: List of raw item dictionaries from Excel
            site: Primary site filter
            site2: Secondary site filter

        Returns:
            List of normalized inventory items
        """
        normalized_items = []

        for item in items:
            try:
                normalized = ExcelService._normalize_item(item, site, site2)
                if normalized:
                    normalized_items.append(normalized)
            except Exception as e:
                # Log error but continue processing other items
                print(f"Error processing item: {str(e)}")
                continue

        return normalized_items

    @staticmethod
    def _normalize_item(item: Dict[str, Any],
                       site: Optional[str] = None,
                       site2: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Normalize a single inventory item.

        Args:
            item: Raw item dictionary
            site: Primary site
            site2: Secondary site

        Returns:
            Normalized item dictionary or None if item should be skipped
        """
        # Common column name mappings (flexible to handle different Excel formats)
        name_fields = ['name', 'item_name', 'description', 'nomenclature']
        category_fields = ['category', 'type', 'item_type', 'class']
        quantity_fields = ['quantity', 'qty', 'count']
        weight_fields = ['weight', 'weight_lbs', 'wt']
        length_fields = ['length', 'len', 'l']
        width_fields = ['width', 'w']
        height_fields = ['height', 'h', 'ht']
        area_fields = ['area', 'sq_ft', 'sqft', 'square_feet']
        service_fields = ['service', 'branch', 'department', 'dept', 'division']

        # Extract values using flexible field matching
        normalized = {
            'name': ExcelService._get_first_value(item, name_fields),
            'category': ExcelService._get_first_value(item, category_fields),
            'quantity': ExcelService._get_numeric_value(item, quantity_fields, default=1),
            'weight': ExcelService._get_numeric_value(item, weight_fields),
            'length': ExcelService._get_numeric_value(item, length_fields),
            'width': ExcelService._get_numeric_value(item, width_fields),
            'height': ExcelService._get_numeric_value(item, height_fields),
            'area': ExcelService._get_numeric_value(item, area_fields),
            'service_branch': ExcelService._get_first_value(item, service_fields),
            'description': item.get('description') or item.get('desc'),
        }

        # Calculate area if not provided but length/width are available
        if not normalized['area'] and normalized['length'] and normalized['width']:
            normalized['area'] = normalized['length'] * normalized['width']

        # Calculate PSF (pounds per square foot) if we have weight and area
        if normalized['weight'] and normalized['area'] and normalized['area'] > 0:
            normalized['psf'] = normalized['weight'] / normalized['area']
        else:
            normalized['psf'] = None

        # Store original data for reference
        normalized['item_data'] = item

        # Skip items without a name
        if not normalized['name']:
            return None

        return normalized

    @staticmethod
    def _get_first_value(item: Dict[str, Any], field_names: List[str]) -> Optional[Any]:
        """Get the first non-null value from a list of possible field names.

        Args:
            item: Item dictionary
            field_names: List of possible field names

        Returns:
            First non-null value found or None
        """
        for field in field_names:
            value = item.get(field)
            if value is not None and str(value).strip():
                return str(value).strip()
        return None

    @staticmethod
    def _get_numeric_value(item: Dict[str, Any],
                          field_names: List[str],
                          default: Optional[float] = None) -> Optional[float]:
        """Get a numeric value from possible field names.

        Args:
            item: Item dictionary
            field_names: List of possible field names
            default: Default value if not found

        Returns:
            Numeric value or default
        """
        for field in field_names:
            value = item.get(field)
            if value is not None:
                try:
                    # Handle pandas NaN
                    if pd.isna(value):
                        continue
                    return float(value)
                except (ValueError, TypeError):
                    continue
        return default

    @staticmethod
    def calculate_summary_stats(items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics for inventory items.

        Args:
            items: List of normalized inventory items

        Returns:
            Dictionary of summary statistics
        """
        total_items = sum(item.get('quantity', 0) for item in items)
        total_entries = len(items)
        total_weight = sum(
            (item.get('weight', 0) or 0) * item.get('quantity', 1)
            for item in items
        )
        total_area = sum(
            (item.get('area', 0) or 0) * item.get('quantity', 1)
            for item in items
        )

        # Category breakdown
        categories = {}
        for item in items:
            cat = item.get('category', 'Uncategorized')
            categories[cat] = categories.get(cat, 0) + item.get('quantity', 1)

        return {
            'total_items': total_items,
            'total_entries': total_entries,
            'total_weight': round(total_weight, 2),
            'total_area': round(total_area, 2),
            'categories': categories
        }
