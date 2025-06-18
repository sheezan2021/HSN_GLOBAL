from flask import Flask, render_template, jsonify, request
import json

app = Flask(__name__)

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

@app.route("/get_hsn")
def get_hsn():
    country = request.args.get('country', 'IN').upper()
    
    # List of JSON files to load (you can modify this list as needed)
    json_files = [
        'static/HSN_India/India_06_chapter_hsn_codes.json',
        'static/HSN_India/India_07_chapter_hsn_codes.json',
        'static/HSN_India/India_08_chapter_hsn_codes.json',
        'static/HSN_India/India_09_chapter_hsn_codes.json'
    ]
    
    merged_data = {}
    
    for filepath in json_files:
        data = load_json_file(filepath)
        if data:
            # Merge the data (this assumes each JSON has unique top-level keys)
            for key, value in data.items():
                if key in merged_data:
                    # If key exists, merge the categories
                    if 'categories' in value and 'categories' in merged_data[key]:
                        merged_data[key]['categories'].update(value['categories'])
                    # Add other merge logic here if needed for different structures
                else:
                    merged_data[key] = value
    
    if not merged_data:
        return jsonify({"error": "No valid JSON data could be loaded"}), 500
        
    return jsonify(merged_data)

if __name__ == "__main__":
    app.secret_key = 'your-secret-key-here'
    app.run(debug=True)
