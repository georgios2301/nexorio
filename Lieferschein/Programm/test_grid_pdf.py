#!/usr/bin/env python3
"""
Test script to generate a PDF with grid overlay on ls_vorlage.pdf
This helps identify exact coordinates for placing text on the template
"""

import os
import sys
import tempfile
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import red, blue, lightgrey, black, grey
from reportlab.lib.units import mm

def create_grid_overlay():
    """Create a grid overlay PDF with coordinates"""
    overlay_path = tempfile.mktemp(suffix='_grid.pdf')
    c = canvas.Canvas(overlay_path, pagesize=A4)
    width, height = A4
    
    # Draw fine grid lines every 25 points
    c.setStrokeColor(lightgrey)
    c.setLineWidth(0.3)
    
    # Fine vertical lines
    for x in range(0, int(width) + 1, 25):
        c.line(x, 0, x, height)
    
    # Fine horizontal lines
    for y in range(0, int(height) + 1, 25):
        c.line(0, y, width, y)
    
    # Draw medium grid lines every 50 points
    c.setStrokeColor(grey)
    c.setLineWidth(0.5)
    
    for x in range(0, int(width) + 1, 50):
        c.line(x, 0, x, height)
        # Add coordinate labels
        if x % 100 != 0:  # Skip 100s labels (they'll be in black)
            c.setFont("Helvetica", 7)
            c.setFillColor(grey)
            # Top
            c.drawString(x - 10, height - 10, f"{int(x)}")
            # Bottom
            c.drawString(x - 10, 5, f"{int(x)}")
    
    for y in range(0, int(height) + 1, 50):
        c.line(0, y, width, y)
        # Add coordinate labels
        if y % 100 != 0:  # Skip 100s labels
            c.setFont("Helvetica", 7)
            c.setFillColor(grey)
            # Left
            c.drawString(5, y - 2, f"{int(y)}")
            # Right
            c.drawString(width - 30, y - 2, f"{int(y)}")
    
    # Draw major grid lines every 100 points
    c.setStrokeColor(black)
    c.setLineWidth(1)
    
    for x in range(0, int(width) + 1, 100):
        c.line(x, 0, x, height)
        # Add major coordinate labels
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(black)
        # Top
        c.drawString(x - 15, height - 10, f"{int(x)}")
        # Bottom  
        c.drawString(x - 15, 5, f"{int(x)}")
    
    for y in range(0, int(height) + 1, 100):
        c.line(0, y, width, y)
        # Add major coordinate labels
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(black)
        # Left
        c.drawString(5, y - 2, f"{int(y)}")
        # Right
        c.drawString(width - 35, y - 2, f"{int(y)}")
    
    # Add coordinate reference points
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(red)
    
    # Test points for common field positions
    test_points = [
        (100, 750, "Kunde/Adresse"),
        (420, 750, "Bestellnummer"),
        (420, 710, "Datum"),
        (80, 550, "Tabelle Start"),
        (80, 500, "Position 1"),
        (80, 480, "Position 2"),
        (80, 460, "Position 3"),
        (500, 100, "Summe/Total"),
    ]
    
    for x, y, label in test_points:
        c.circle(x, y, 3, fill=1)
        c.drawString(x + 10, y, f"{label} ({int(x)}, {int(y)})")
    
    # Add instructions and coordinate info
    c.setFont("Helvetica", 12)
    c.setFillColor(blue)
    c.drawCentredString(width/2, height - 30, "GRID OVERLAY - Koordinaten in Punkten")
    c.drawCentredString(width/2, height - 50, "Schwarze Linien = 100 Punkte | Graue = 50 Punkte | Hellgrau = 25 Punkte")
    
    # Add coordinate system info
    c.setFont("Helvetica", 10)
    c.setFillColor(red)
    c.drawString(10, height - 70, "Koordinatensystem: X = horizontal (0-595), Y = vertikal (0-842)")
    c.drawString(10, height - 85, "Ursprung (0,0) = unten links | A4 = 210 x 297 mm = 595 x 842 Punkte")
    
    c.save()
    return overlay_path

def merge_with_template():
    """Merge grid overlay with ls_vorlage.pdf"""
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(os.path.dirname(script_dir), 'Vorlagen', 'ls_vorlage.pdf')
    output_path = os.path.join(script_dir, 'lieferschein_mit_grid.pdf')
    
    # Check if template exists
    if not os.path.exists(template_path):
        print(f"ERROR: Template not found at {template_path}")
        return None
    
    # Create grid overlay
    overlay_path = create_grid_overlay()
    
    try:
        # Read PDFs
        template_pdf = PdfReader(template_path)
        overlay_pdf = PdfReader(overlay_path)
        output_pdf = PdfWriter()
        
        # Merge first page
        template_page = template_pdf.pages[0]
        overlay_page = overlay_pdf.pages[0]
        template_page.merge_page(overlay_page)
        output_pdf.add_page(template_page)
        
        # Write output
        with open(output_path, 'wb') as f:
            output_pdf.write(f)
        
        print(f"✓ Grid PDF created: {output_path}")
        print("\nÖffnen Sie diese Datei und teilen Sie mir mit, wo die folgenden Informationen platziert werden sollen:")
        print("- Bestellnummer")
        print("- Datum")
        print("- Kundenname und Adresse")
        print("- Positionstabelle (Start Y-Koordinate)")
        print("- Spalten der Tabelle (X-Koordinaten für: Pos, Auftrag, Beschreibung, Menge, Preis, etc.)")
        
        return output_path
        
    finally:
        # Clean up
        if os.path.exists(overlay_path):
            os.remove(overlay_path)

if __name__ == "__main__":
    result = merge_with_template()
    if result:
        print(f"\nDie Datei wurde erstellt: {result}")
        
        # Try to open the PDF automatically
        if sys.platform == "darwin":  # macOS
            os.system(f"open '{result}'")
        elif sys.platform == "win32":  # Windows
            os.startfile(result)
        else:  # Linux
            os.system(f"xdg-open '{result}'")