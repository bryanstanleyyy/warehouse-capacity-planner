# Warehouse Capacity Planner - Excel Template Examples

This directory contains comprehensive Excel template files for uploading inventory data to the Warehouse Capacity Planner. These examples serve as references, starting points, and testing resources.

## Quick Start

**First time user?** Start with [templates/quick_start_template.xlsx](templates/quick_start_template.xlsx)

This template includes:
- 5 pre-filled example items
- Comments explaining each column
- Data validation dropdowns
- Empty rows for you to add your items

## Directory Structure

```
examples/
├── templates/          # User-facing templates (5-15 items)
├── datasets/           # Realistic pre-populated datasets (40-200 items)
└── edge_cases/         # Testing scenarios (20-500 items)
```

## Templates Directory

Templates are designed for users to fill in with their own inventory data. They include instructional features and examples.

### [quick_start_template.xlsx](templates/quick_start_template.xlsx) (5 items)
**Best for:** First-time users, learning the system

**Features:**
- 5 diverse example items (General, Equipment, Medical, Hazmat)
- Cell comments explaining each column
- Dropdown menus for categories and service branches
- Example formulas for auto-calculations
- Empty rows ready for your data

**Use this when:** You're uploading inventory for the first time and want guidance

---

### [basic_inventory_template.xlsx](templates/basic_inventory_template.xlsx) (10 items)
**Best for:** Standard warehouse operations

**Features:**
- 10 items covering common warehouse categories
- Mix of simple and moderate complexity items
- Examples with and without climate control requirements
- Realistic weights, dimensions, and quantities

**Use this when:** You need a straightforward template without instructional features

---

### [comprehensive_inventory_template.xlsx](templates/comprehensive_inventory_template.xlsx) (15 items)
**Best for:** Advanced users exploring all features

**Features:**
- 15 items showcasing ALL system capabilities
- Alternative column name formats (nomenclature, qty, wt, etc.)
- All boolean value formats (yes/no, true/false, 1/0, x/blank)
- Extreme cases (very tall items 20+ ft, heavy PSF 300+)
- Priority ordering examples
- All 8 categories represented

**Use this when:** You want to see all features or use non-standard column names

## Datasets Directory

Pre-populated datasets with realistic inventory for different warehouse scenarios. Use these to test the system or as reference examples.

### [warehouse_standard_50_items.xlsx](datasets/warehouse_standard_50_items.xlsx) (50 items)
**Scenario:** Standard mixed-use warehouse

**Distribution:**
- General (30%), Equipment (24%), Furniture (16%), Components (20%), Medical (10%)
- 8 climate-controlled items (16%)
- 3 special handling items (6%)
- Service branches: Logistics, Operations, Admin, Medical

**Use this when:** Testing with a realistic standard warehouse inventory

---

### [warehouse_mixed_100_items.xlsx](datasets/warehouse_mixed_100_items.xlsx) (100 items)
**Scenario:** Large mixed-use warehouse with challenging items

**Distribution:**
- All 8 categories represented
- 12 tall items (18-22 ft requiring high bay storage)
- 8 heavy items (250+ PSF requiring high floor strength)
- 15-20 climate-controlled items
- 8-10 special handling items

**Use this when:** Testing allocation with challenging constraints (height, weight, climate)

---

### [cold_storage_inventory.xlsx](datasets/cold_storage_inventory.xlsx) (60 items)
**Scenario:** Refrigerated/freezer warehouse

**Distribution:**
- **100% climate-controlled** (all items require temperature control)
- Medical (33%), Containers (25%), General (25%), Hazmat (17%)
- 20% also require special handling (refrigerated hazmat)
- Temperature-sensitive: pharmaceuticals, vaccines, frozen goods

**Use this when:** Planning cold storage or refrigerated warehouse capacity

---

### [warehouse_large_200_items.xlsx](datasets/warehouse_large_200_items.xlsx) (200 items)
**Scenario:** Large-scale warehouse capacity testing

**Size Distribution:**
- 40% small items (<100 sq ft)
- 35% medium items (100-300 sq ft)
- 20% large items (300-1,000 sq ft)
- 5% oversized items (1,000+ sq ft)

**Special Requirements:**
- 35 climate-controlled items
- 18 special handling items
- 15 very tall items (20+ ft)
- 10 very heavy items (300+ PSF)
- 100 items with priority ordering

**Use this when:** Testing large-scale warehouse capacity or performance

---

### [outdoor_yard_inventory.xlsx](datasets/outdoor_yard_inventory.xlsx) (40 items)
**Scenario:** Outdoor storage yard (no climate control)

**Distribution:**
- **0% climate-controlled** (all weather-resistant items)
- Equipment (38%), Vehicles (25%), Containers (25%), Machinery (12%)
- Large footprints (50-400 sq ft per item)
- Heavy items (high PSF tolerance needed)
- Tall items (8-25 ft)

**Use this when:** Planning outdoor yard storage or non-climate-controlled areas

## Edge Cases Directory

Testing files for validating system robustness and handling edge cases.

### [column_variations.xlsx](edge_cases/column_variations.xlsx) (20 items)
**Purpose:** Test all supported column name variations

**Structure:**
- 4 sections with different column naming conventions
- Section 1: Standard names (Name, Quantity, Category, etc.)
- Section 2: Short aliases (item_name, qty, type, wt, len, w, h)
- Section 3: Long aliases (nomenclature, count, class, weight_lbs)
- Section 4: Mixed column names

**Use this when:** Validating the system accepts various column name formats

---

### [edge_cases_all.xlsx](edge_cases/edge_cases_all.xlsx) (30 items)
**Purpose:** Comprehensive edge case scenarios

**Scenarios:**
- Missing data (minimal fields, only name)
- Auto-calculations (Area from L×W, PSF from Weight/Area)
- Extreme dimensions (1×1×1 ft to 30×20×30 ft)
- Extreme weights (10 lbs to 100,000 lbs)
- Extreme PSF (0.5 to 600 PSF)
- All boolean variations (yes/no/true/false/1/0/x/blank)
- Default values (quantity=1, priority=999)
- Special characters in names
- Very long item names (100+ characters)
- Empty optional fields

**Use this when:** Testing system robustness and error handling

---

### [stress_test_500_items.xlsx](edge_cases/stress_test_500_items.xlsx) (500 items)
**Purpose:** Performance and scalability testing

**Distribution:**
- 500 diverse items across all categories
- Climate control: 25% (125 items)
- Special handling: 15% (75 items)
- Evenly distributed across categories
- Normal distribution for dimensions

**Use this when:** Testing performance with large file uploads

## Column Reference

### Required Columns
- **Name** (required) - Unique item name or description
  - Aliases: `name`, `item_name`, `description`, `nomenclature`

### Optional Columns (Recommended)

**Quantity:**
- Default: 1 if not provided
- Aliases: `quantity`, `qty`, `count`

**Category:**
- Valid options: General, Equipment, Machinery, Medical, Hazmat, Electronics, Containers, Components, Furniture
- Aliases: `category`, `type`, `item_type`, `class`

**Dimensions:**
- **Weight (lbs):** `weight`, `weight_lbs`, `wt`
- **Length (ft):** `length`, `len`, `l`
- **Width (ft):** `width`, `w`
- **Height (ft):** `height`, `h`, `ht`
- **Area (sq ft):** `area`, `sq_ft`, `sqft`, `square_feet`
  - Auto-calculated from Length × Width if not provided

**PSF (Pounds per Square Foot):**
- Auto-calculated from Weight / Area
- Used to match items with floor strength constraints

**Service Branch:**
- Valid options: Navy, Army, Marine Corps, Air Force, Logistics, Operations, Medical, Safety, Engineering, Manufacturing, Transportation, Admin, IT
- Aliases: `service`, `branch`, `department`, `dept`, `division`

**Special Requirements:**
- **Climate Control:** `climate_control`, `requires_climate`, `climate`, `climate_controlled`
- **Special Handling:** `special_handling`, `special`, `hazmat`, `fragile`, `requires_special`
- Accepts: Yes, No, True, False, 1, 0, X, blank (case-insensitive)

**Priority Order:**
- Lower numbers = higher priority
- Default: 999 if not provided
- Aliases: `priority`, `priority_order`, `order`

## Upload Guidelines

### Creating Your Own File

1. **Start with a template** - Copy quick_start_template.xlsx or basic_inventory_template.xlsx
2. **Keep the header row** - First row must contain column names (any supported alias)
3. **Fill in your data** - Add rows below the header with your inventory items
4. **Required: Name column** - Every item must have a name
5. **Optional but recommended** - Include dimensions (L, W, H) and weight for accurate allocation

### Boolean Values

The system flexibly handles various boolean formats:
- **Yes values:** yes, YES, y, Y, true, TRUE, True, 1, x, X
- **No values:** no, NO, n, N, false, FALSE, False, 0, (blank)

### Auto-Calculations

- **Area:** If you provide Length and Width but not Area, the system calculates: Area = Length × Width
- **PSF:** If you provide Weight and Area, the system calculates: PSF = Weight / Area
- You can also provide Area or PSF explicitly to override auto-calculation

### File Size and Format

- **Format:** .xlsx or .xls files
- **Max size:** 10MB (typically supports 10,000+ items)
- **No row limit:** Upload as many items as needed

### Common Issues

**Issue:** Upload rejected - "No items found"
- **Solution:** Ensure the first row has at least a "Name" column (or alias like "item_name")

**Issue:** Some items are missing after upload
- **Solution:** Check that all items have a name. Items without names are skipped.

**Issue:** Area or PSF values seem wrong
- **Solution:** Double-check Length, Width, and Weight values. PSF = Weight / Area.

**Issue:** Boolean values not recognized
- **Solution:** Use simple Yes/No values. Avoid typos or unusual formats.

**Issue:** Category or Service Branch shows as "Uncategorized" or "Unassigned"
- **Solution:** Use exact spellings from the valid options list above (case-insensitive is OK)

## Tips and Best Practices

### For Accurate Allocation

1. **Provide dimensions** - Length, Width, Height help the system allocate items to appropriate zones
2. **Specify weight** - Required for calculating PSF (floor strength requirements)
3. **Mark special requirements** - Climate control and special handling flags ensure items go to proper zones
4. **Use priority ordering** - Lower priority numbers (1-10) for critical items that must be allocated first

### For Large Uploads

1. **Break into logical groups** - Consider separate uploads for different locations or categories
2. **Use consistent naming** - Helps identify items later
3. **Include descriptions** - Makes it easier to understand allocation results

### For Testing

1. **Start small** - Try quick_start_template.xlsx first
2. **Test edge cases** - Use edge_cases_all.xlsx to validate your warehouse configuration
3. **Scale up gradually** - Move from 50-item to 100-item to 200-item datasets

## Categories Explained

- **General:** Standard supplies, pallets, boxes, miscellaneous items
- **Equipment:** Industrial tools, forklifts, racks, material handling equipment
- **Machinery:** Heavy manufacturing equipment, presses, CNC machines, industrial machinery
- **Medical:** Healthcare supplies, pharmaceuticals, medical equipment (often requires climate control)
- **Hazmat:** Hazardous materials, chemicals, flammable liquids (requires special handling)
- **Electronics:** IT equipment, servers, electronics (often requires climate control)
- **Containers:** Shipping containers, large storage units, ISO containers
- **Components:** Parts, assemblies, replacement components, spare parts
- **Furniture:** Office furniture, desks, chairs, cabinets

## PSF (Pounds per Square Foot) Guidelines

Floor strength is measured in PSF. Typical warehouse floor strengths:

- **Light duty:** 150 PSF (office areas, light storage)
- **Standard:** 200-250 PSF (general warehouse storage)
- **Heavy duty:** 300-400 PSF (equipment, machinery)
- **Extra heavy:** 500+ PSF (industrial presses, very heavy machinery)

**Example PSF calculations:**
- 1,000 lb pallet on 16 sq ft = 62.5 PSF ✓ (light/standard floor)
- 10,000 lb machine on 100 sq ft = 100 PSF ✓ (standard floor)
- 50,000 lb press on 100 sq ft = 500 PSF ⚠ (requires heavy-duty floor)

## Need Help?

- Check the [main project README](../README.md) for application usage
- Review the example templates for reference
- Start with small test files before uploading production data

## License

These example files are provided as part of the Warehouse Capacity Planner project.
