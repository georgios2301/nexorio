#!/usr/bin/env python3
import sys
sys.path.append('Lieferschein/Vorlagen')

from laufkarte_pdf_generator import generate_laufkarte_direct
import subprocess
import os

# Test data
test_data = {
    'datum': '06.01.2025',
    'positionen': [
        {
            'auftrag': 'FL-12345',
            'beschreibung': 'Stahlplatte 10mm',
            'vorgang': 'trennen/pendeln/putzen',
            'menge': 5,
            'fv': 'F',
            'werkstoff': 'St 37',
            'modellnummer': 'MOD-001'
        },
        {
            'auftrag': 'FL-12346',
            'beschreibung': 'Aluminiumblech 3mm entgraten und bohren',
            'vorgang': 'Pendeln/putzen',
            'menge': 10,
            'fv': 'V',
            'werkstoff': 'AlMg3',
            'modellnummer': 'MOD-002'
        }
    ]
}

# Generate PDF
pdf_path = generate_laufkarte_direct(test_data)
print(f"PDF generated: {pdf_path}")

# Open PDF
if sys.platform == "darwin":  # macOS
    subprocess.run(["open", pdf_path])
elif sys.platform == "win32":  # Windows
    os.startfile(pdf_path)
else:  # Linux
    subprocess.run(["xdg-open", pdf_path])