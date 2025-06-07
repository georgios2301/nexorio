import os
import io
import re
import json
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from PIL import Image
import pytesseract
import pdf2image
import tempfile
from difflib import SequenceMatcher
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../.env'))

# Configure Gemini API if available - NEVER hardcode API keys!
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print(f"Gemini API configured successfully (key ends with ...{GEMINI_API_KEY[-4:]})")
else:
    print("WARNING: GEMINI_API_KEY not set. Using fallback OCR method.")

# Vorgang options and patterns
VORGANG_OPTIONS = [
    "trennen/pendeln/putzen",
    "geschweißte Stellen putzen",
    "Pendeln/putzen",
    "Putzen",
    "Reparatur fehler ausschl.",
    "Pendeln"
]

# Keywords that trigger "trennen/pendeln/putzen" (including variations)
TRENNEN_PENDELN_PUTZEN_KEYWORDS = [
    "entrichtern", 
    "enttrichtern",  # mit doppeltem 't'
    "entgraten",
    "entgrat",
    "trennen"
]

def determine_vorgang(text: str) -> Optional[str]:
    """Determine the vorgang based on text content and rules"""
    if not text:
        return None
    
    text_lower = text.lower()
    print(f"DEBUG determine_vorgang: Input text: '{text}'")
    
    # Rule 1: Check for keywords that trigger "trennen/pendeln/putzen"
    for keyword in TRENNEN_PENDELN_PUTZEN_KEYWORDS:
        if keyword in text_lower:
            print(f"DEBUG determine_vorgang: Found keyword '{keyword}' -> returning 'trennen/pendeln/putzen'")
            return "trennen/pendeln/putzen"
    
    # Rule 1.5: Special check for "pendeln" AND "putzen" together
    if "pendeln" in text_lower and "putzen" in text_lower:
        print(f"DEBUG determine_vorgang: Found 'pendeln' AND 'putzen' -> returning 'trennen/pendeln/putzen'")
        return "trennen/pendeln/putzen"
    
    # Rule 2: Find best match from options
    best_match = None
    best_score = 0.0
    
    print(f"DEBUG determine_vorgang: Checking against options...")
    
    for option in VORGANG_OPTIONS:
        option_lower = option.lower()
        
        # Check for exact substring match first
        if option_lower in text_lower:
            print(f"DEBUG determine_vorgang: Exact match found for '{option}'")
            return option
        
        # Check individual words from the option
        option_words = [w.strip() for w in option_lower.replace('/', ' ').split() if len(w.strip()) > 2]
        words_found = 0
        
        for word in option_words:
            if word in text_lower:
                words_found += 1
                print(f"DEBUG determine_vorgang: Found word '{word}' from option '{option}'")
        
        # Calculate match score based on words found
        if option_words:
            word_score = words_found / len(option_words)
            if word_score > best_score:
                best_score = word_score
                best_match = option
                print(f"DEBUG determine_vorgang: New best match '{option}' with score {word_score}")
    
    # Only return match if score is high enough
    if best_score >= 0.5:  # At least 50% of words must match
        print(f"DEBUG determine_vorgang: Returning best match '{best_match}' with score {best_score}")
        return best_match
    
    print(f"DEBUG determine_vorgang: No good match found (best score: {best_score})")
    return None

async def process_image(content: bytes, filename: str) -> Optional[Dict[str, Any]]:
    """Process image content and extract structured data"""
    try:
        # Try Gemini AI first if API key is available
        if GEMINI_API_KEY:
            result = await process_with_gemini(content, filename)
            if result:
                return result
        
        # Fallback to local OCR
        return await process_with_tesseract(content, filename)
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None

async def process_with_gemini(content: bytes, filename: str) -> Optional[Dict[str, Any]]:
    """Process image using Google Gemini AI"""
    try:
        # Convert content to PIL Image
        if filename.lower().endswith('.pdf'):
            # Convert PDF to images
            images = pdf2image.convert_from_bytes(content)
            if images:
                image = images[0]  # Use first page
            else:
                return None
        else:
            image = Image.open(io.BytesIO(content))
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Prepare prompt for extraction
        prompt = """
        Analysiere dieses Lieferschein-Dokument und extrahiere die folgenden Informationen im JSON-Format:
        
        {
            "bestellnummer": "Die Bestellnummer (meist mit BL- Präfix)",
            "datum": "Das Datum des Lieferscheins",
            "kunde": "Kundenname",
            "positionen": [
                {
                    "pos_nr": "Positionsnummer",
                    "auftrag": "Auftragsnummer (oft mit FL- Präfix)",
                    "beschreibung": "Artikelbeschreibung - WICHTIG: Extrahiere den VOLLSTÄNDIGEN Text inklusive Wörter wie Entrichtern, Entgraten, etc.",
                    "vorgang": "Vorgang/Prozess - kann leer sein, wird später automatisch bestimmt",
                    "menge": "Menge als Zahl",
                    "preis": "Preis als Zahl",
                    "modellnummer": "Modellnummer falls vorhanden",
                    "werkstoff": "Material/Werkstoff falls vorhanden",
                    "fv": "F/V/P Code falls vorhanden"
                }
            ]
        }
        
        Wichtig:
        - Extrahiere NUR die tatsächlich vorhandenen Daten
        - Bei der Beschreibung: Nimm den KOMPLETTEN Text inklusive aller Prozesswörter
        - Konvertiere Mengen und Preise in Zahlen
        - Bei deutschen Zahlen: Ersetze Komma durch Punkt
        - Gib NULL zurück für nicht vorhandene Felder
        - Bestellnummern haben oft das Format BL-XXXXX
        - Auftragsnummern haben oft das Format FL-XXXXX
        """
        
        # Generate content
        response = model.generate_content([prompt, image])
        
        # Extract JSON from response
        text = response.text
        
        # Try to find JSON in response
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            # Clean up data
            if 'positionen' in data:
                for pos in data['positionen']:
                    # Convert German decimal format to standard
                    if 'menge' in pos and isinstance(pos['menge'], str):
                        pos['menge'] = float(pos['menge'].replace(',', '.'))
                    if 'preis' in pos and isinstance(pos['preis'], str):
                        pos['preis'] = float(pos['preis'].replace(',', '.'))
                    
                    # Determine vorgang based on beschreibung and existing vorgang
                    beschreibung = pos.get('beschreibung', '')
                    existing_vorgang = pos.get('vorgang', '')
                    combined_text = f"{beschreibung} {existing_vorgang}".strip()
                    
                    if combined_text:
                        determined_vorgang = determine_vorgang(combined_text)
                        pos['vorgang'] = determined_vorgang
                        print(f"DEBUG OCR: Position {pos.get('pos_nr')} - Beschreibung: '{beschreibung}' -> Vorgang: '{determined_vorgang}'")
                    else:
                        print(f"DEBUG OCR: Position {pos.get('pos_nr')} - No text for vorgang determination")
            
            print(f"DEBUG OCR: Final data with vorgang: {json.dumps(data, indent=2)}")
            return data
        
        return None
    except Exception as e:
        print(f"Gemini processing error: {str(e)}")
        return None

async def process_with_tesseract(content: bytes, filename: str) -> Optional[Dict[str, Any]]:
    """Process image using Tesseract OCR"""
    try:
        # Convert content to PIL Image
        if filename.lower().endswith('.pdf'):
            # Convert PDF to images
            images = pdf2image.convert_from_bytes(content)
            if images:
                image = images[0]  # Use first page
            else:
                return None
        else:
            image = Image.open(io.BytesIO(content))
        
        # Perform OCR
        text = pytesseract.image_to_string(image, lang='deu')
        
        # Extract structured data using regex patterns
        data = {
            "bestellnummer": None,
            "datum": None,
            "kunde": None,
            "positionen": []
        }
        
        # Extract order number (BL-XXXXX pattern)
        bl_match = re.search(r'BL-\d+', text)
        if bl_match:
            data["bestellnummer"] = bl_match.group(0)
        
        # Extract date (various German date formats)
        date_patterns = [
            r'\d{1,2}\.\d{1,2}\.\d{4}',
            r'\d{1,2}\.\d{1,2}\.\d{2}',
            r'\d{1,2}\s+\w+\s+\d{4}'
        ]
        for pattern in date_patterns:
            date_match = re.search(pattern, text)
            if date_match:
                data["datum"] = date_match.group(0)
                break
        
        # Extract positions (FL-XXXXX pattern and related data)
        lines = text.split('\n')
        current_position = None
        
        for i, line in enumerate(lines):
            # Look for FL- pattern
            fl_match = re.search(r'FL-\d+', line)
            if fl_match:
                if current_position:
                    data["positionen"].append(current_position)
                
                current_position = {
                    "auftrag": fl_match.group(0),
                    "pos_nr": None,
                    "beschreibung": None,
                    "menge": None,
                    "preis": None,
                    "werkstoff": None,
                    "modellnummer": None,
                    "vorgang": None,
                    "fv": None
                }
                
                # Extract position number
                pos_match = re.search(r'^\d+', line)
                if pos_match:
                    current_position["pos_nr"] = pos_match.group(0)
                
                # Look for quantity and price in same or next lines
                for j in range(i, min(i + 3, len(lines))):
                    # German number format (1.234,56 or 1234,56)
                    number_pattern = r'\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?'
                    numbers = re.findall(number_pattern, lines[j])
                    
                    for num in numbers:
                        # Convert German format to float
                        num_float = float(num.replace('.', '').replace(',', '.'))
                        
                        # Heuristic: smaller numbers are quantities, larger are prices
                        if num_float < 100 and current_position["menge"] is None:
                            current_position["menge"] = num_float
                        elif num_float >= 100 and current_position["preis"] is None:
                            current_position["preis"] = num_float
                
                # Extract material/werkstoff
                material_patterns = [
                    r'St\s*\d+',  # Steel grades
                    r'S\s*\d+\s*\w*',
                    r'Alu(?:minium)?',
                    r'Edelstahl',
                    r'\d+\s*mm'  # Dimensions
                ]
                for pattern in material_patterns:
                    material_match = re.search(pattern, line, re.IGNORECASE)
                    if material_match:
                        current_position["werkstoff"] = material_match.group(0)
                        break
                
                # Extract F/V/P code
                fv_match = re.search(r'\b[FVP]\b', line)
                if fv_match:
                    current_position["fv"] = fv_match.group(0)
                
                # Try to extract beschreibung from the line
                if fl_match:
                    # Remove the FL number and position number to get description
                    desc_text = line
                    desc_text = re.sub(r'FL-\d+', '', desc_text)
                    desc_text = re.sub(r'^\d+\s*', '', desc_text)
                    desc_text = desc_text.strip()
                    if desc_text:
                        current_position["beschreibung"] = desc_text
        
        # Add last position if exists
        if current_position:
            data["positionen"].append(current_position)
        
        # Apply vorgang determination to all positions
        for pos in data["positionen"]:
            beschreibung = pos.get('beschreibung', '')
            if beschreibung:
                pos['vorgang'] = determine_vorgang(beschreibung)
        
        # Return data only if we found meaningful content
        if data["bestellnummer"] or data["positionen"]:
            return data
        
        return None
    except Exception as e:
        print(f"Tesseract processing error: {str(e)}")
        return None