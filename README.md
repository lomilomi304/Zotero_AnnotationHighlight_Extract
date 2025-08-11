# Zotero Annotation Harvester by Color

A Python script that extracts highlighted text annotations from your Zotero PDF library and organizes them by highlight color. Perfect for researchers who want to quickly gather all their color-coded highlights for analysis, note-taking, or writing.

## Quick Start

### 1. Install Requirements

```bash
pip install requests pandas
```

### 2. Get Your Zotero Credentials

1. Visit https://www.zotero.org/settings/keys
2. Click "Create new private key"
3. Give it a name (e.g., "Annotation Harvester")
4. Check "Allow library access" (read permissions)
5. Click "Save Key"
6. Copy your API key and User ID (the 6-7 digit number shown)

### 3. Configure the Script

Open the script and update these lines:

```python
ZOTERO_API_KEY = "your_actual_api_key_here"
ZOTERO_USER_ID = "1234567"  # Your user ID numbers
```

### 4. Run the Script

```bash
python zotero_harvester.py
```

## Output Structure

The script creates a timestamped folder (e.g., `zotero_annotations_20241211_143022/`) containing:

```
zotero_annotations_20241211_143022/
├── yellow_highlights.txt
├── red_highlights.txt
├── green_highlights.txt
├── blue_highlights.txt
├── purple_highlights.txt
└── all_annotations.csv
```

### Text File Format
Each color file contains formatted annotations:

```
=== YELLOW HIGHLIGHTS ===
Total: 15 annotations
==================================================

1. The Impact of Climate Change on Biodiversity
   File: climate_biodiversity_2023.pdf
   Page: 23
   Date: 2024-12-10T15:30:45Z
   Text: Species migration patterns have shifted significantly over the past decade...
--------------------------------------------------

2. Another Paper Title
   File: another_paper.pdf
   Page: 45
   Date: 2024-12-09T10:15:30Z
   Text: The methodology employed in this study...
--------------------------------------------------
```

## Configuration Options

### Basic Settings

```python
# Your Zotero credentials
ZOTERO_API_KEY = "your_key_here"
ZOTERO_USER_ID = "your_id_here"

# Optional: Limit to specific collection
COLLECTION_ID = None  # Set to collection ID to filter
```

### Advanced Customization

#### Custom Output Directory

To change the output directory, modify the `save_to_files` method:

```python
# Change this line in the save_to_files method:
output_dir = "my_custom_folder"  # Instead of auto-generated name
```

Or set a custom base directory:

```python
# Add this at the top of save_to_files method:
base_dir = "/path/to/your/desired/location"
output_dir = os.path.join(base_dir, f"zotero_annotations_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
```

#### Color Customization

Add or modify colors in the `COLOR_MAPPING` dictionary:

```python
COLOR_MAPPING = {
    "#ffd400": "Yellow",
    "#ff6666": "Red", 
    "#5fb236": "Green",
    "#2ea8e5": "Blue",
    "#a28ae5": "Purple",
    "#e56eee": "Magenta",
    "#f19837": "Orange",
    "#aaaaaa": "Gray",
    "#your_color": "Custom Name"  # Add custom colors
}
```

#### Fetch More Annotations

By default, the script fetches the 100 most recent annotations. To get more:

```python
# In the main() function, change:
annotations = harvester.get_annotations(collection_id=COLLECTION_ID, limit=500)
```

Note: Zotero API has rate limits. For very large libraries, consider pagination.

#### Filter by Date Range

Add date filtering to the `get_annotations` method:

```python
# Add to params in get_annotations method:
params['since'] = '2024-01-01'  # ISO date format
```

## Collection-Specific Harvesting

To harvest from a specific Zotero folder:

1. In Zotero, right-click on the collection → "Show Collection Key"
2. Set the `COLLECTION_ID` in the script:

```python
COLLECTION_ID = "ABC123DEF"  # Your collection key
```

## Troubleshooting

### Common Issues

**"No annotations found"**
- Verify your API key and User ID are correct
- Make sure you have highlighted PDFs in your Zotero library
- Check if `COLLECTION_ID` is set correctly (if using)

**"Error fetching annotations"**
- Check your internet connection
- Verify API key has proper permissions
- Ensure User ID is just numbers (no letters)

**Empty text files**
- The script only extracts highlight annotations (not notes or images)
- Make sure your highlights have actual text content
- Check if you're using supported highlight colors

### API Rate Limits

Zotero's API allows:
- 1000 requests per hour for personal libraries
- 10 requests per second

For large libraries, the script automatically handles basic rate limiting.

## File Formats

### CSV Output
The `all_annotations.csv` file contains columns:
- `text` - The highlighted text
- `color_code` - Hex color code
- `color_name` - Human-readable color name
- `page` - Page number
- `pdf_title` - PDF document title
- `pdf_filename` - PDF file name
- `date_modified` - Last modification date
- `parent_key` - Zotero item key

### Text Output
Organized by color for easy reading and copying into notes or papers.

## Advanced Usage

### Batch Processing Multiple Collections

To process multiple collections in one run:

```python
collections = ["ABC123", "DEF456", "GHI789"]
all_annotations = []

for collection_id in collections:
    annotations = harvester.get_annotations(collection_id=collection_id)
    processed = harvester.process_annotations(annotations)
    all_annotations.extend(processed)

harvester.save_to_files(all_annotations)
```

### Integration with Other Tools

The CSV output is perfect for:
- **Excel/Google Sheets** - For analysis and visualization
- **Obsidian/Notion** - Import as database
- **R/Python data analysis** - Further processing with pandas
- **Qualitative analysis software** - Import for coding

## License

This script is provided as-is for educational and research purposes. Respect Zotero's API terms of service and rate limits.

## Contributing

Found a bug or have a feature request? Feel free to modify the script for your needs! Common enhancements:
- Export to other formats (Markdown, JSON, etc.)
- GUI interface
- Automatic synchronization
- Advanced filtering options

## Support

For Zotero API documentation: https://www.zotero.org/support/dev/web_api/v3/start

For Python help: The script uses standard libraries (`requests`, `pandas`) with extensive documentation available online.
