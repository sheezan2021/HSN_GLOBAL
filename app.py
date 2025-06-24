from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json
from pathlib import Path
import re

import os

# Initialize Flask app
app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'),
            static_url_path='',
            template_folder='templates')

# Enable CORS
CORS(app)

# Ensure the static folder exists
os.makedirs(app.static_folder, exist_ok=True)

# Add cache control headers
@app.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'public, max-age=300'  # 5 minutes cache
    return response

@app.route("/")
def index():
    return render_template("index.html")

def load_json_file(filepath):
    """Helper function to load a JSON file and handle errors"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"Warning: JSON decode error in {filepath}: {e}")
        return None

def load_country_data(country_code):
    """Load HSN data for a specific country"""
    country_code = country_code.upper()
    hsn_data = {}
    
    # Map country codes to their directory names
    country_dirs = {
        'IN': 'HSN_India',
        'TR': 'HSN_Turkey',
        # Add more countries as needed
    }
    
    data_dir = Path(f'static/{country_dirs.get(country_code, "HSN_India")}')
    
    if not data_dir.exists():
        print(f"Error: Directory not found for {country_code}: {data_dir}")
        return {}
    
    for file_path in data_dir.glob('*.json'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)
                # Extract chapter number from filename (e.g., 'India_04_chapter_hsn_codes.json' -> '04')
                # Handle different filename formats
                filename_parts = file_path.stem.split('_')
                chapter = None
                
                # Try different patterns to extract chapter number
                for part in filename_parts:
                    if part.isdigit():
                        chapter = part.zfill(2)
                        break
                
                if not chapter:
                    print(f"Warning: Could not extract chapter number from {file_path}")
                    continue
                
                # Get the chapter description from the data
                chapter_info = chapter_data.get(chapter, {})
                hsn_data[chapter] = {
                    'description': chapter_info.get('description', f'Chapter {chapter}'),
                    'categories': chapter_info.get('categories', {})
                }
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    # Sort chapters numerically
    hsn_data = dict(sorted(hsn_data.items()))
    return hsn_data

# Available countries with their display names and directory names
AVAILABLE_COUNTRIES = {
    'IN': {
        'name': 'India',
        'dir': 'HSN_India'
    },
    'TR': {
        'name': 'Turkey',
        'dir': 'HSN_Turkey'
    },
    'MY': {
        'name': 'Malaysia',
        'dir': 'HSN_Malaysia'
    },
    'SA': {
        'name': 'Saudi Arabia',
        'dir': 'HSN_Saudi_Arabia'
    },
    'AE': {
        'name': 'United Arab Emirates',
        'dir': 'HSN_UAE'
    }
}

# Global dictionary to store data for all countries
COUNTRY_DATA = {}
HSN_DATA = {}

# Available countries with their names and directories
AVAILABLE_COUNTRIES = {
    'IN': {'name': 'India', 'dir': 'HSN_India'},
    'TR': {'name': 'Turkey', 'dir': 'HSN_Turkey'},
    'MY': {'name': 'Malaysia', 'dir': 'HSN_Malaysia'},
    'SA': {'name': 'Saudi_Arabia', 'dir': 'HSN_Saudi_Arabia'},
    'AE': {'name': 'UAE', 'dir': 'HSN_UAE'}
}

def load_hsn_data(country_code='IN'):
    """Load HSN data for a specific country"""
    global HSN_DATA
    
    if country_code not in AVAILABLE_COUNTRIES:
        print(f"Error: Country code {country_code} not in AVAILABLE_COUNTRIES")
        return False
        
    country_dir = os.path.join('static', AVAILABLE_COUNTRIES[country_code]['dir'])
    if not os.path.exists(country_dir):
        print(f"Warning: Directory not found: {country_dir}")
        return False
        
    # Clear existing data for this country
    HSN_DATA = {}
    loaded_files = 0
    
    # Find all JSON files for this country
    for root, _, files in os.walk(country_dir):
        for file in files:
            if file.lower().endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        print(f"Loading file: {file_path}")  # Debug log
                        data = json.load(f)
                        # Check if this is a single-chapter file (like Turkey's)
                        if isinstance(data, dict) and 'description' in next(iter(data.values()), {}):
                            # This is a single-chapter file (like Turkey's)
                            for chapter, chapter_data in data.items():
                                if chapter not in HSN_DATA:
                                    HSN_DATA[chapter] = chapter_data
                                else:
                                    # If chapter exists, merge categories
                                    if 'categories' in chapter_data and 'categories' in HSN_DATA[chapter]:
                                        HSN_DATA[chapter]['categories'].update(chapter_data.get('categories', {}))
                            loaded_files += 1
                        else:
                            # This is a multi-chapter file (like India's)
                            for chapter, chapter_data in data.items():
                                if chapter not in HSN_DATA:
                                    HSN_DATA[chapter] = chapter_data
                                else:
                                    # If chapter exists, merge categories
                                    if 'categories' in chapter_data and 'categories' in HSN_DATA[chapter]:
                                        HSN_DATA[chapter]['categories'].update(chapter_data.get('categories', {}))
                            loaded_files += 1
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
                    import traceback
                    traceback.print_exc()
    
    print(f"Loaded {loaded_files} files for {country_code}")
    print(f"Chapters loaded: {list(HSN_DATA.keys())}")  # Debug log
    return loaded_files > 0

def get_country_data(country_code):
    """Get HSN data for a country, loading it if not already loaded"""
    country_code = country_code.upper()
    if country_code not in COUNTRY_DATA:
        COUNTRY_DATA[country_code] = load_country_data(country_code)
    return COUNTRY_DATA[country_code]

def search_hsn_code(code, country_code='IN'):
    """Search for an HSN code in the loaded data"""
    global HSN_DATA
    
    if not code or not code.strip():
        return None
        
    code = code.strip()
    # Allow 2-10 digit codes to support classified products
    if not re.match(r'^\d{2,10}$', code):
        return None
    
    # Load data for the specified country
    if not load_hsn_data(country_code):
        print(f"Failed to load data for country: {country_code}")
        return None
        
    chapter = code[:2]
    if chapter not in HSN_DATA:
        print(f"Chapter {chapter} not found in HSN_DATA")
        print(f"Available chapters: {list(HSN_DATA.keys())}")
        return None
        
    chapter_data = HSN_DATA[chapter]
    
    # Handle different data structures
    chapter_description = chapter_data.get('chapter_description', '')
    if not chapter_description and 'description' in chapter_data:
        chapter_description = chapter_data['description']
    
    result = {
        'chapter': chapter,
        'chapter_description': chapter_description,
        'found': False
    }
    
    # Search in categories if they exist
    categories = chapter_data.get('categories', {})
    if not categories and 'products' in chapter_data:
        # Handle case where products are directly under chapter (Turkey's structure)
        categories = {'00': {'description': 'All Categories', 'products': chapter_data.get('products', {})}}
    
    for cat_code, category in categories.items():
        if code.startswith(cat_code) or cat_code == '00':  # '00' is a special case for Turkey
            result['category'] = {
                'code': cat_code,
                'description': category.get('description', '')
            }
            
            # Search in products
            products = category.get('products', {})
            # Handle case where products might be in 'classified-products' (Turkey's structure)
            if not products and 'classified-products' in category:
                products = {}
                for prod_code, prod_desc in category.get('classified-products', {}).items():
                    # Extract the main product code (first 6 digits)
                    main_code = prod_code[:6]
                    if main_code not in products:
                        products[main_code] = {
                            'description': prod_desc.split('—')[0].strip() if '—' in prod_desc else prod_desc,
                            'classified-products': {}
                        }
                    products[main_code]['classified-products'][prod_code] = prod_desc
            
            # Search through products
            for prod_code, product in products.items():
                if code.startswith(prod_code):
                    product_result = {
                        'code': prod_code,
                        'description': product.get('description', '')
                    }
                    # Add classified products if they exist
                    if 'classified-products' in product:
                        product_result['classified_products'] = product['classified-products']
                    
                    result['product'] = product_result
                    
                    # Check if we have an exact match with a classified product
                    if 'classified_products' in product_result:
                        # Check for exact match in classified products
                        for cls_code, cls_desc in product_result['classified_products'].items():
                            # For 8-digit codes, check direct match with cls_code (which is the full 8 digits)
                            if len(code) == 8 and code == cls_code:
                                result['classified_product'] = {
                                    'code': cls_code,
                                    'description': cls_desc
                                }
                                result['found'] = True
                                return result
                            # For backward compatibility with old format
                            full_cls_code = prod_code + cls_code
                            if code == full_cls_code:
                                result['classified_product'] = {
                                    'code': full_cls_code,
                                    'description': cls_desc
                                }
                                result['found'] = True
                                return result
                    
                    # If we have an exact product match or a partial match
                    if code == prod_code or code.startswith(prod_code):
                        result['found'] = True
                        # If we have classified products, include them in the result
                        if 'classified_products' in product_result:
                            result['product']['classified_products'] = product_result['classified_products']
                        return result
        
        if result.get('found'):
            break
    
    return result if result.get('found') or 'category' in result else None

def find_suggestions(hsn_code, country_code='IN', max_suggestions=10):
    """Find all matching HSN codes that start with the given code for a specific country"""
    suggestions = []
    hsn_data = get_country_data(country_code)
    added_codes = set()  # To avoid duplicates
    
    # If code is too short, suggest matching chapters
    if len(hsn_code) <= 2:
        chapter = hsn_code.zfill(2)
        # Find all chapters that start with the input
        for chap, chapter_data in hsn_data.items():
            if chap.startswith(chapter) and chapter not in added_codes:
                suggestions.append({
                    'code': chap,
                    'type': 'Chapter',
                    'description': chapter_data.get('description', f'Chapter {chap}')
                })
                added_codes.add(chap)
    
    # If code is 4 digits or more, suggest matching categories
    if len(hsn_code) >= 4:
        chapter = hsn_code[:2].zfill(2)
        if chapter in hsn_data:
            category_prefix = hsn_code[2:4].zfill(2)
            for cat_code, category in hsn_data[chapter].get('categories', {}).items():
                if cat_code.startswith(category_prefix):
                    full_code = f"{chapter}{cat_code}"
                    if full_code not in added_codes:
                        suggestions.append({
                            'code': full_code,
                            'type': 'Category',
                            'description': category.get('description', f'Category {cat_code}')
                        })
                        added_codes.add(full_code)
                    
                    # If code is 6 digits or more, suggest matching products
                    if len(hsn_code) >= 6:
                        product_prefix = hsn_code[4:6].zfill(2)
                        for prod_code, product in category.get('products', {}).items():
                            if prod_code.startswith(product_prefix):
                                full_code = f"{chapter}{cat_code}{prod_code}"
                                if full_code not in added_codes:
                                    suggestions.append({
                                        'code': full_code,
                                        'type': 'Product',
                                        'description': product.get('description', f'Product {prod_code}')
                                    })
                                    added_codes.add(full_code)
                                
                                # If code is 6 or more digits, suggest matching classified products
                                if len(hsn_code) >= 6 and 'classified-products' in product:
                                    # If we have a full 6-digit product code, show all its classified products
                                    if len(hsn_code) == 6 and hsn_code == full_code:
                                        for cls_code, desc in product['classified-products'].items():
                                            full_cls_code = f"{full_code}{cls_code}"
                                            if full_cls_code not in added_codes:
                                                suggestions.append({
                                                    'code': full_cls_code,
                                                    'type': 'Classified Product',
                                                    'description': desc
                                                })
                                                added_codes.add(full_cls_code)
                                    # If we're searching within a specific product's classified codes
                                    elif len(hsn_code) > 6 and hsn_code.startswith(full_code):
                                        cls_prefix = hsn_code[6:]
                                        for cls_code, desc in product['classified-products'].items():
                                            if cls_code.startswith(cls_prefix):
                                                full_cls_code = f"{full_code}{cls_code}"
                                                if full_cls_code not in added_codes:
                                                    suggestions.append({
                                                        'code': full_cls_code,
                                                        'type': 'Classified Product',
                                                        'description': desc
                                                    })
                                                    added_codes.add(full_cls_code)
    
    # Sort suggestions by code length and then by code
    suggestions.sort(key=lambda x: (len(x['code']), x['code']))
    
    # Limit the number of suggestions and ensure they're unique
    unique_suggestions = []
    seen = set()
    
    for s in suggestions:
        if s['code'] not in seen:
            seen.add(s['code'])
            unique_suggestions.append(s)
            if len(unique_suggestions) >= max_suggestions:
                break
                
    return unique_suggestions

@app.route('/search_hsn')
def search_hsn():
    hsn_code = request.args.get('code', '').strip()
    country_code = request.args.get('country', 'IN').upper()
    suggestions_only = request.args.get('suggestions', 'false').lower() == 'true'
    
    if not hsn_code or not hsn_code.isdigit() or len(hsn_code) < 2 or len(hsn_code) > 10:
        if suggestions_only:
            return jsonify({'suggestions': []})
        return jsonify({
            'found': False,
            'error': 'Please provide a valid HSN code (2-10 digits)'
        }), 400
    
    # If suggestions are requested
    if suggestions_only:
        suggestions = find_suggestions(hsn_code, country_code)
        return jsonify({'suggestions': suggestions})
    
    # First try to find an exact match
    result = search_hsn_code(hsn_code, country_code)
    
    if result and result.get('found'):
        # If we have a classified product match, make sure it's included in the response
        if len(hsn_code) >= 10 and 'product' in result and 'classified_products' in result['product']:
            classified_code = hsn_code[6:]
            for cls_code, cls_desc in result['product']['classified_products'].items():
                if hsn_code == (result['product']['code'] + cls_code):
                    result['classified_product'] = {
                        'code': result['product']['code'] + cls_code,
                        'description': cls_desc
                    }
                    break
        
        result['exact_match'] = True
        return jsonify(result)
    
    # If no exact match, try to find partial matches
    chapter = hsn_code[:2].zfill(2)
    if chapter not in HSN_DATA:
        return jsonify({
            'found': False,
            'error': f'No matching HSN code found for: {hsn_code}'
        }), 404
    
    # Return chapter-level match
    chapter_data = HSN_DATA[chapter]
    result = {
        'found': True,
        'exact_match': False,
        'chapter': chapter,
        'chapter_description': chapter_data.get('description', f'Chapter {chapter}'),
        'category': None,
        'product': None,
        'classified_product': None
    }
    
    # Try to find the best partial match
    if len(hsn_code) >= 4:  # Try to match category
        category_code = hsn_code[2:4].zfill(2)
        for cat_code, category in chapter_data.get('categories', {}).items():
            if cat_code.startswith(category_code):
                result['category'] = {
                    'code': cat_code,
                    'description': category.get('description', f'Category {cat_code}')
                }
                
                # Try to match product
                if len(hsn_code) >= 6:
                    product_code = hsn_code[4:6].zfill(2)
                    for prod_code, product in category.get('products', {}).items():
                        if prod_code.startswith(product_code):
                            result['product'] = {
                                'code': prod_code,
                                'description': product.get('description', f'Product {prod_code}')
                            }
                            
                            # Try to match classified product
                            if len(hsn_code) == 8:
                                classified_code = hsn_code[6:8]
                                for cls_code, desc in product.get('classified-products', {}).items():
                                    if cls_code.startswith(classified_code):
                                        result['classified_product'] = {
                                            'code': cls_code,
                                            'description': desc
                                        }
                                        result['exact_match'] = True
                                        break
                            break
                break
    
    return jsonify(result)

@app.route('/get_countries')
def get_countries():
    # Return list of available countries with their display names
    countries = [
        {'code': code, 'name': info['name']} 
        for code, info in AVAILABLE_COUNTRIES.items()
    ]
    return jsonify(countries)

@app.route('/get_hsn')
def get_hsn():
    country_code = request.args.get('country', 'IN').upper()
    
    # Check if country is valid
    if country_code not in AVAILABLE_COUNTRIES:
        return jsonify({"error": "Invalid country code"}), 400
    
    # Load the data for the country
    data = get_country_data(country_code)
    
    if data:
        return jsonify(data)
    else:
        return jsonify({"error": "Data not found"}), 404

@app.route('/get_hsn_attributes')
def get_hsn_attributes():
    hsn_code = request.args.get('hsn_code')
    country_code = request.args.get('country', 'IN').upper()
    
    print(f"\n=== Debug: HSN Attributes Request ===")
    print(f"HSN Code: {hsn_code}, Country: {country_code}")
    
    if not hsn_code:
        return jsonify({"error": "HSN code is required"}), 400
    
    # Get country directory from available countries
    country_info = AVAILABLE_COUNTRIES.get(country_code, {})
    if not country_info:
        print(f"Error: Unknown country code: {country_code}")
        return jsonify({"error": f"Unsupported country code: {country_code}"}), 400
    
    country_dir = country_info.get('dir', 'HSN_India')
    
    # Determine the attributes filename based on country
    # Handle case-insensitive filename for India
    if country_code.upper() == 'IN':
        attributes_filename = "India_hsn_attributes.json"
    else:
        attributes_filename = f"{country_code.lower()}_hsn_attributes.json"
        
    attributes_path = os.path.join('static', country_dir, attributes_filename)
    print(f"Looking for attributes in: {os.path.abspath(attributes_path)}")
    
    print(f"Debug: Looking for attributes in {attributes_path}")
    
    try:
        if not os.path.exists(attributes_path):
            print(f"Error: Attributes file not found at {os.path.abspath(attributes_path)}")
            return jsonify({"error": f"Attributes file not found for country {country_code}"}), 404
        
        print(f"Loading attributes from: {os.path.abspath(attributes_path)}")
        with open(attributes_path, 'r', encoding='utf-8') as f:
            all_attributes = json.load(f)
            
        # If it's a single object, convert it to a list with one item
        if not isinstance(all_attributes, list):
            print("Converting single attribute object to list")
            all_attributes = [all_attributes]
        
        print(f"Successfully loaded {len(all_attributes)} attribute entries")
        
        # Find matching HSN code (handle different formats)
        found = False
        for idx, attr in enumerate(all_attributes, 1):
            if not isinstance(attr, dict):
                print(f"Warning: Entry {idx} is not a dictionary: {attr}")
                continue
                
            if 'hsn_code' not in attr:
                print(f"Warning: Entry {idx} is missing hsn_code")
                continue
            
            # Get the HSN code from attributes and clean it
            attr_code = str(attr['hsn_code']).strip()
            search_code = str(hsn_code).strip()
            
            print(f"Checking entry {idx}: HSN {attr_code} (type: {type(attr['hsn_code']).__name__}) "
                  f"against search code {search_code}")
            
            # Try exact match first
            if attr_code == search_code:
                print(f"✓ Found exact match for HSN code: {search_code}")
                print(f"Variant types: {attr.get('variant_types', 'N/A')}")
                return jsonify(attr)
                
            # If no exact match, try removing any non-digit characters and compare
            clean_attr_code = ''.join(c for c in attr_code if c.isdigit())
            clean_search_code = ''.join(c for c in search_code if c.isdigit())
            
            if clean_attr_code and clean_search_code and clean_attr_code == clean_search_code:
                print(f"✓ Found match after cleaning for HSN code: {search_code}")
                print(f"Variant types: {attr.get('variant_types', 'N/A')}")
                return jsonify(attr)
            
            # If still no match, check if one is a prefix of the other
            if (clean_attr_code.startswith(clean_search_code) or 
                clean_search_code.startswith(clean_attr_code)):
                print(f"✓ Found prefix match for HSN code: {search_code}")
                print(f"Variant types: {attr.get('variant_types', 'N/A')}")
                return jsonify(attr)
        
        print(f"No matching HSN code found in {len(all_attributes)} entries")
        
        print(f"Debug: No matching HSN code found in {attributes_path}")
        return jsonify({"error": f"Attributes not found for HSN code: {hsn_code}"}), 404
        
    except json.JSONDecodeError as je:
        print(f"JSON Decode Error in {attributes_path}: {je}")
        return jsonify({"error": f"Invalid JSON in attributes file: {je}"}), 500
    except Exception as e:
        print(f"Error loading HSN attributes from {attributes_path}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error loading attributes: {str(e)}"}), 500

if __name__ == "__main__":
    app.secret_key = 'your-secret-key-here'
    app.run(debug=True)
