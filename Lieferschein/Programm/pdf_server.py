from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import tempfile
from datetime import datetime
import requests
import json

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Try to import from different locations depending on deployment
try:
    # Production (Render) - files are in root directory
    from lieferschein_generator import generate_lieferschein, generate_laufkarte, generate_rechnung
except ImportError:
    # Development - files are in Vorlagen directory
    from Vorlagen.lieferschein_generator import generate_lieferschein, generate_laufkarte, generate_rechnung

app = Flask(__name__)
CORS(app)

# Backend API URL
BACKEND_API_URL = os.environ.get('BACKEND_API_URL', 'http://localhost:8001')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "pdf-server-python"})

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """Generate PDF based on document type"""
    try:
        data = request.json
        doc_type = data.get('docType')
        doc_data = data.get('data', {})
        
        if not doc_type:
            return jsonify({"error": "docType is required"}), 400
        
        # Generate PDF based on type and get document number
        document_number = None
        if doc_type == 'lieferschein':
            pdf_path = generate_lieferschein(doc_data)
            # Get the generated Lieferschein number from the counter
            try:
                from lieferschein_counter import get_current_number
            except ImportError:
                from Vorlagen.lieferschein_counter import get_current_number
            document_number = f"DZ{datetime.now().year}-{get_current_number():04d}"
        elif doc_type == 'laufkarte':
            pdf_path = generate_laufkarte(doc_data)
            # Laufkarte uses the order number
            document_number = doc_data.get('bestellnummer', '')
        elif doc_type == 'rechnung':
            pdf_path = generate_rechnung(doc_data)
            # Rechnung uses RE- prefix
            document_number = f"RE-{doc_data.get('bestellnummer', '')}"
        else:
            return jsonify({"error": f"Unknown docType: {doc_type}"}), 400
        
        # Record document generation in history
        try:
            history_data = {
                "bestellnummer": doc_data.get("bestellnummer", ""),
                "document_type": doc_type,
                "generated_by": "pdf_server",
                "document_data": doc_data,
                "metadata": {
                    "pdf_path": pdf_path,
                    "timestamp": datetime.now().isoformat(),
                    "document_number": document_number
                }
            }
            
            # Send to backend API
            response = requests.post(
                f"{BACKEND_API_URL}/api/document-history",
                json=history_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code not in [200, 201]:
                print(f"Warning: Failed to record document history: {response.text}")
        except Exception as e:
            print(f"Warning: Error recording document history: {str(e)}")
        
        # Send the PDF file
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{doc_type}_{doc_data.get("bestellnummer", "unknown")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 4000))
    app.run(host='0.0.0.0', port=port, debug=True)