import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Vorlagen.lieferschein_generator import generate_lieferschein, generate_laufkarte, generate_rechnung
import subprocess
import platform

# Test data
test_data = {
    "bestellnummer": "BL-12345",
    "datum": "06.01.2025",
    "kunde": {
        "name": "Musterfirma GmbH",
        "adresse": "Musterstraße 123",
        "plz": "12345",
        "ort": "Musterstadt"
    },
    "positionen": [
        {
            "pos_nr": "1",
            "auftrag": "FL-10001",
            "beschreibung": "Stahlplatte 10mm sehr lange Beschreibung die über mehrere Zeilen geht und den Platz reduziert",
            "vorgang": "Zuschnitt nach Maß",
            "menge": 5.0,
            "preis": 125.50,
            "modellnummer": "SP-10-500",
            "fv": "F",
            "werkstoff": "S235JR"
        },
        {
            "pos_nr": "2",
            "auftrag": "FL-10002",
            "beschreibung": "Winkelstahl 50x50x5",
            "vorgang": "Bohren",
            "menge": 10.0,
            "preis": 45.80,
            "modellnummer": "WS-50-5",
            "fv": "V",
            "werkstoff": "S275JR"
        },
        {
            "pos_nr": "3",
            "auftrag": "FL-10003",
            "beschreibung": "Rundstahl Ø20mm",
            "vorgang": "Ablängen",
            "menge": 8.0,
            "preis": 22.30,
            "modellnummer": "RS-20",
            "fv": "P",
            "werkstoff": "S355J2"
        },
        {
            "pos_nr": "4",
            "auftrag": "FL-10004",
            "beschreibung": "Flachstahl 40x10mm",
            "vorgang": "Fräsen",
            "menge": 12.0,
            "preis": 18.50,
            "modellnummer": "FS-40-10",
            "fv": "F",
            "werkstoff": "S235JR"
        },
        {
            "pos_nr": "5",
            "auftrag": "FL-10005",
            "beschreibung": "U-Profil 80x40x4",
            "vorgang": "Schweißen",
            "menge": 6.0,
            "preis": 65.20,
            "modellnummer": "UP-80-40",
            "fv": "V",
            "werkstoff": "S275JR"
        },
        {
            "pos_nr": "6",
            "auftrag": "FL-10006",
            "beschreibung": "Vierkantrohr 60x60x3",
            "vorgang": "Lackieren",
            "menge": 4.0,
            "preis": 89.90,
            "modellnummer": "VKR-60-3",
            "fv": "P",
            "werkstoff": "S355J2"
        },
        {
            "pos_nr": "7",
            "auftrag": "FL-10007",
            "beschreibung": "T-Profil 100x100x10",
            "vorgang": "Galvanisieren",
            "menge": 3.0,
            "preis": 112.30,
            "modellnummer": "TP-100-10",
            "fv": "F",
            "werkstoff": "S235JR"
        },
        {
            "pos_nr": "8",
            "auftrag": "FL-10008",
            "beschreibung": "Sechskantstahl SW 25",
            "vorgang": "Drehen",
            "menge": 15.0,
            "preis": 28.40,
            "modellnummer": "SKS-25",
            "fv": "V",
            "werkstoff": "S275JR"
        }
    ]
}

def test_pdf_generation():
    """Test PDF generation for all document types"""
    print("Testing PDF generation...")
    
    # Test Lieferschein
    print("\n1. Generating Lieferschein...")
    try:
        pdf_path = generate_lieferschein(test_data)
        print(f"   ✓ Lieferschein created: {pdf_path}")
        open_pdf(pdf_path)
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test Laufkarte
    print("\n2. Generating Laufkarte...")
    try:
        pdf_path = generate_laufkarte(test_data)
        print(f"   ✓ Laufkarte created: {pdf_path}")
        open_pdf(pdf_path)
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test Rechnung
    print("\n3. Generating Rechnung...")
    try:
        pdf_path = generate_rechnung(test_data)
        print(f"   ✓ Rechnung created: {pdf_path}")
        open_pdf(pdf_path)
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n✅ Test completed!")

def open_pdf(path):
    """Open PDF in default viewer"""
    try:
        if platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', path])
        elif platform.system() == 'Windows':
            subprocess.run(['start', '', path], shell=True)
        else:  # Linux
            subprocess.run(['xdg-open', path])
    except:
        print(f"   ℹ Could not open PDF automatically. File saved at: {path}")

if __name__ == "__main__":
    test_pdf_generation()