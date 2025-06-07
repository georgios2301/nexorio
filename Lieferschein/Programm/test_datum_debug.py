#!/usr/bin/env python3
"""
Debug script to check what's being printed in the PDF
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Vorlagen'))

from lieferschein_generator import generate_lieferschein

# Test data with explicit date
test_data = {
    'bestellnummer': 'BL252115',
    'datum': '06.01.2025',  # Explicit date without time
    'positionen': [{
        'pos_nr': 1,
        'auftrag': 'FL250958',
        'beschreibung': 'Test Position',
        'menge': 1,
        'preis': 10.00
    }]
}

print(f"Sending date to PDF generator: '{test_data['datum']}'")

if __name__ == "__main__":
    try:
        output_path = generate_lieferschein(test_data)
        print(f"✓ Lieferschein created: {output_path}")
        
        # Open the PDF
        if sys.platform == "darwin":  # macOS
            os.system(f"open '{output_path}'")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()