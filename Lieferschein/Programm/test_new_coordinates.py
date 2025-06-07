#!/usr/bin/env python3
"""
Test script to generate a Lieferschein with the new coordinates
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Vorlagen'))

from lieferschein_generator import generate_lieferschein

# Test data with multiple positions to test pagination
test_data = {
    'bestellnummer': 'BL252115',
    'datum': '06.01.2025',
    'kunde': {
        'name': 'Musterfirma GmbH',
        'adresse': 'Industriestraße 123',
        'plz': '12345',
        'ort': 'Musterstadt'
    },
    'positionen': []
}

# Add many positions to test multi-page support
for i in range(1, 25):  # 24 positions to ensure multi-page
    test_data['positionen'].append({
        'pos_nr': i,
        'auftrag': f'FL25095{i}',
        'beschreibung': f'Testposition {i} - Bearbeitung und Montage',
        'menge': 10.0,
        'preis': 25.50,
        'modellnummer': f'TCR-{i:03d}',
        'fv': 'F',
        'werkstoff': 'ES 1.4317.261'
    })

if __name__ == "__main__":
    try:
        print("Generating test Lieferschein with new coordinates...")
        output_path = generate_lieferschein(test_data)
        print(f"✓ Lieferschein created: {output_path}")
        
        # Open the PDF
        if sys.platform == "darwin":  # macOS
            os.system(f"open '{output_path}'")
        elif sys.platform == "win32":  # Windows
            os.startfile(output_path)
        else:  # Linux
            os.system(f"xdg-open '{output_path}'")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()