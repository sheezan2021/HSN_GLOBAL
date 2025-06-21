import json
import re
from collections import defaultdict
from pathlib import Path

def count_hsn_codes(data):
    # Dictionary to store counts for each digit length
    counts = defaultdict(int)
    
    def _count_codes(node):
        if isinstance(node, dict):
            for key, value in node.items():
                # Check if key is a numeric code
                if isinstance(key, str) and key.replace(' ', '').isdigit():
                    # Count the digit length (removing any spaces)
                    length = len(key.replace(' ', ''))
                    if length % 2 == 0:  # Only count even-digit lengths
                        counts[length] += 1
                # Recursively check values
                _count_codes(value)
        elif isinstance(node, list):
            for item in node:
                _count_codes(item)
    
    _count_codes(data)
    return dict(sorted(counts.items()))

if __name__ == "__main__":
    # Path to the JSON file
    json_path = r"C:\Users\User\Desktop\HSN\HSN_GLOBAL\static\HSN_India\India_08_chapter_hsn_codes.json"
    
    try:
        # Load the JSON data
        with open(json_path, 'r', encoding='utf-8') as f:
            hsn_data = json.load(f)
        
        print(f"Analyzing HSN codes in: {json_path}")
        print("-" * 50)
        
        # Get counts
        digit_counts = count_hsn_codes(hsn_data)
        
        # Print results
        print("HSN Code Length Counts:")
        print("-" * 30)
        
        # Define all possible even-digit lengths we want to check (2 to 16)
        all_lengths = range(2, 17, 2)
        
        # Print counts for all lengths, including those with zero counts
        for length in all_lengths:
            count = digit_counts.get(length, 0)
            print(f"{length:2d}-digit HSN codes: {count:4d}")
        
        total = sum(digit_counts.values())
        print("-" * 30)
        print(f"Total HSN codes:    {total:4d}")
        
    except FileNotFoundError:
        print(f"Error: File not found at {json_path}")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in the file")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
