#!/usr/bin/env python3
import sys
sys.path.append('../Vorlagen')

from lieferschein_generator import generate_lieferschein

# Test with minimal data
data = {
    "bestellnummer": "TEST-123",
    "datum": "06.06.2025"
}

try:
    pdf_path = generate_lieferschein(data)
    print(f"PDF generated: {pdf_path}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()