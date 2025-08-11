
import requests
import json
import pandas as pd
from datetime import datetime
import os

# =============================================================================
# CONFIGURATION - UPDATE THESE VALUES
# =============================================================================

# Get these from https://www.zotero.org/settings/keys
ZOTERO_API_KEY = "YOUR_API_KEY_HERE"  # Your Zotero API key
ZOTERO_USER_ID = "YOUR_USER_ID_HERE"  # Your Zotero User ID (numbers only)

# Optional: Specify a collection ID to limit search to specific folder
# Leave as None to search entire library
COLLECTION_ID = None  # e.g., "ABC123DEF"

# Color mapping - Zotero's internal color codes to human-readable names
COLOR_MAPPING = {
    "#ffd400": "Yellow",
    "#ff6666": "Red", 
    "#5fb236": "Green",
    "#2ea8e5": "Blue",
    "#a28ae5": "Purple",
    "#e56eee": "Magenta",
    "#f19837": "Orange",
    "#aaaaaa": "Gray"
}

# =============================================================================
# SCRIPT CODE
# =============================================================================

class ZoteroAnnotationHarvester:
    def __init__(self, api_key, user_id):
        self.api_key = api_key
        self.user_id = user_id
        self.base_url = f"https://api.zotero.org/users/{user_id}"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
    def get_annotations(self, collection_id=None, limit=100):
        """Fetch annotations from Zotero library"""
        print("Fetching annotations from Zotero...")
        
        url = f"{self.base_url}/items"
        params = {
            'itemType': 'annotation',
            'limit': limit,
            'sort': 'dateModified',
            'direction': 'desc'
        }
        
        if collection_id:
            params['collection'] = collection_id
            
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            annotations = response.json()
            print(f"Found {len(annotations)} annotations")
            return annotations
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching annotations: {e}")
            return []
    
    def get_parent_item_info(self, parent_key):
        """Get information about the parent PDF item"""
        try:
            url = f"{self.base_url}/items/{parent_key}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            item_data = response.json()
            data = item_data.get('data', {})
            
            return {
                'title': data.get('title', 'Unknown Title'),
                'filename': data.get('filename', 'Unknown File')
            }
        except:
            return {'title': 'Unknown Title', 'filename': 'Unknown File'}
    
    def process_annotations(self, annotations):
        """Process and organize annotations by color and type"""
        print("Processing annotations...")
        
        processed_annotations = []
        
        for annotation in annotations:
            data = annotation.get('data', {})
            annotation_type = data.get('annotationType', '')
            
            # Process both highlights and text notes
            if annotation_type == 'highlight':
                text = data.get('annotationText', '').strip()
                if not text:  # Skip empty highlights
                    continue
                    
                color_code = data.get('annotationColor', '#ffd400')  # Default to yellow
                color_name = COLOR_MAPPING.get(color_code, f"Unknown ({color_code})")
                annotation_category = f"{color_name} Highlight"
                
            elif annotation_type == 'note':
                text = data.get('annotationComment', '').strip()
                if not text:  # Skip empty notes
                    continue
                    
                color_code = '#ffffff'  # White for notes
                color_name = 'Note'
                annotation_category = 'Text Note'
                
            else:
                continue  # Skip other annotation types
                
            parent_key = data.get('parentItem')
            page_label = data.get('annotationPageLabel', 'Unknown')
            
            # Get parent PDF information
            parent_info = self.get_parent_item_info(parent_key) if parent_key else {}
            
            processed_annotation = {
                'text': text,
                'annotation_type': annotation_type,
                'color_code': color_code,
                'color_name': color_name,
                'category': annotation_category,
                'page': page_label,
                'pdf_title': parent_info.get('title', 'Unknown'),
                'pdf_filename': parent_info.get('filename', 'Unknown'),
                'date_modified': data.get('dateModified', ''),
                'parent_key': parent_key
            }
            
            processed_annotations.append(processed_annotation)
            
        return processed_annotations
    
    def save_to_files(self, annotations):
        """Save annotations to separate files by color and type"""
        if not annotations:
            print("No annotations to save!")
            return
            
        # Create output directory
        output_dir = f"zotero_annotations_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Group annotations by category (color for highlights, separate for notes)
        by_category = {}
        for ann in annotations:
            category = ann['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(ann)
        
        # Save each category to a separate file
        for category, category_annotations in by_category.items():
            # Clean filename
            safe_category = category.lower().replace(' ', '_').replace('/', '_')
            filename = os.path.join(output_dir, f"{safe_category}.txt")
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"=== {category.upper()} ===\n")
                f.write(f"Total: {len(category_annotations)} annotations\n")
                f.write("=" * 50 + "\n\n")
                
                for i, ann in enumerate(category_annotations, 1):
                    f.write(f"{i}. {ann['pdf_title']}\n")
                    f.write(f"   File: {ann['pdf_filename']}\n")
                    f.write(f"   Page: {ann['page']}\n")
                    f.write(f"   Type: {ann['annotation_type'].title()}\n")
                    f.write(f"   Date: {ann['date_modified']}\n")
                    
                    # Format text differently for notes vs highlights
                    if ann['annotation_type'] == 'note':
                        f.write(f"   Your Note: {ann['text']}\n")
                    else:
                        f.write(f"   Highlighted Text: {ann['text']}\n")
                    
                    f.write("-" * 50 + "\n\n")
        
        # Save summary CSV
        df = pd.DataFrame(annotations)
        csv_filename = os.path.join(output_dir, "all_annotations.csv")
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        # Save separate files for highlights vs notes
        highlights = [ann for ann in annotations if ann['annotation_type'] == 'highlight']
        notes = [ann for ann in annotations if ann['annotation_type'] == 'note']
        
        if highlights:
            highlights_df = pd.DataFrame(highlights)
            highlights_csv = os.path.join(output_dir, "highlights_only.csv")
            highlights_df.to_csv(highlights_csv, index=False, encoding='utf-8')
            
        if notes:
            notes_df = pd.DataFrame(notes)
            notes_csv = os.path.join(output_dir, "text_notes_only.csv")
            notes_df.to_csv(notes_csv, index=False, encoding='utf-8')
        
        # Print summary
        print(f"\nResults saved to: {output_dir}/")
        print(f"Total annotations processed: {len(annotations)}")
        print(f"  Highlights: {len(highlights)}")
        print(f"  Text Notes: {len(notes)}")
        print("\nBreakdown by category:")
        for category, category_annotations in by_category.items():
            print(f"  {category}: {len(category_annotations)} annotations")
        
        return output_dir

def main():
    # Validate configuration
    if ZOTERO_API_KEY == "YOUR_API_KEY_HERE" or ZOTERO_USER_ID == "YOUR_USER_ID_HERE":
        print("ERROR: Please update the configuration section with your Zotero API key and User ID")
        print("Get them from: https://www.zotero.org/settings/keys")
        return
    
    print("Zotero Annotation Harvester by Color")
    print("=" * 40)
    
    # Initialize harvester
    harvester = ZoteroAnnotationHarvester(ZOTERO_API_KEY, ZOTERO_USER_ID)
    
    # Fetch annotations
    annotations = harvester.get_annotations(collection_id=COLLECTION_ID)
    
    if not annotations:
        print("No annotations found. Make sure your API key and User ID are correct.")
        return
    
    # Process annotations
    processed = harvester.process_annotations(annotations)
    
    if not processed:
        print("No highlight or note annotations found in your library.")
        return
    
    # Save results
    output_dir = harvester.save_to_files(processed)
    print(f"\nDone! Check the '{output_dir}' folder for your organized annotations.")

if __name__ == "__main__":
    main()
