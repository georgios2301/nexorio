from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import os
from datetime import datetime
import json
from app.ocr import process_image
import uvicorn
from dotenv import load_dotenv
import shutil
from pathlib import Path
import io
import tempfile

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# Supabase configuration - MUST be set as environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_KEY environment variables must be set!")
    print("Set them using:")
    print("  export SUPABASE_URL='your-supabase-url'")
    print("  export SUPABASE_KEY='your-supabase-key'")
    exit(1)

# Initialize FastAPI app
app = FastAPI(title="DZMetall Lieferschein API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Position(BaseModel):
    id: Optional[int] = None
    bestellnummer: str
    pos_nr: Optional[str] = None
    auftrag: Optional[str] = None
    beschreibung: Optional[str] = None
    vorgang: Optional[str] = None
    preis: Optional[float] = None
    menge: Optional[float] = None
    modellnummer: Optional[str] = None
    fv: Optional[str] = None
    werkstoff: Optional[str] = None
    created_at: Optional[str] = None

class PositionUpdate(BaseModel):
    id: Optional[int] = None
    bestellnummer: Optional[str] = None
    pos_nr: Optional[str] = None
    auftrag: Optional[str] = None
    beschreibung: Optional[str] = None
    vorgang: Optional[str] = None
    preis: Optional[float] = None
    menge: Optional[float] = None
    modellnummer: Optional[str] = None
    fv: Optional[str] = None
    werkstoff: Optional[str] = None

class Order(BaseModel):
    bestellnummer: str
    created_at: Optional[str] = None

class DocumentHistory(BaseModel):
    id: Optional[int] = None
    bestellnummer: str
    document_type: str  # 'lieferschein', 'laufkarte', 'rechnung'
    generated_at: Optional[str] = None
    generated_by: Optional[str] = None
    document_data: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# Headers for Supabase requests
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/orders")
async def get_orders():
    """Get all order numbers from the database"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/bestellungen?select=bestellnummer,created_at&order=created_at.desc",
                headers=headers
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            
            return response.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/positions")
async def get_positions(bestellnummer: str):
    """Get all positions for a specific order"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/positionen?bestellnummer=eq.{bestellnummer}&order=pos_nr.asc&select=*",
                headers=headers
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            
            positions = response.json()
            print(f"Loaded {len(positions)} positions for order {bestellnummer}")
            if positions:
                print(f"First position: {positions[0]}")
                # Check if vorgang field exists
                if 'vorgang' in positions[0]:
                    print(f"Vorgang field exists: {positions[0].get('vorgang')}")
                else:
                    print("WARNING: vorgang field NOT in database response!")
            
            return positions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/positions/batch")
async def update_positions_batch(positions: List[Dict[str, Any]]):
    """Update multiple position records using bestellnummer and pos_nr as composite key"""
    try:
        print(f"Received {len(positions)} positions")  # Debug log
        async with httpx.AsyncClient() as client:
            results = []
            
            for i, position in enumerate(positions):
                try:
                    print(f"Processing position {i+1}: {position}")
                    
                    bestellnummer = position.get('bestellnummer')
                    pos_nr = position.get('pos_nr')
                    
                    if not bestellnummer or pos_nr is None:
                        print(f"Warning: Position missing bestellnummer or pos_nr: {position}")
                        continue
                    
                    # Check if position already exists
                    check_response = await client.get(
                        f"{SUPABASE_URL}/rest/v1/positionen?bestellnummer=eq.{bestellnummer}&pos_nr=eq.{pos_nr}&select=*",
                        headers=headers
                    )
                    
                    if check_response.status_code == 200:
                        existing = check_response.json()
                        if existing and len(existing) > 0:
                            # Position exists - update it using composite key
                            update_data = {k: v for k, v in position.items() if k not in ['id', 'created_at', 'bestellnummer', 'pos_nr']}
                            # Debug: Show what fields we're updating including vorgang
                            print(f"Updating existing position (bestellnummer={bestellnummer}, pos_nr={pos_nr})")
                            print(f"Update data fields: {list(update_data.keys())}")
                            if 'vorgang' in update_data:
                                print(f"Vorgang value: '{update_data['vorgang']}'")
                            else:
                                print("WARNING: vorgang field NOT in update data!")
                            print(f"Full update data: {update_data}")
                            
                            update_response = await client.patch(
                                f"{SUPABASE_URL}/rest/v1/positionen?bestellnummer=eq.{bestellnummer}&pos_nr=eq.{pos_nr}",
                                headers=headers,
                                json=update_data
                            )
                            
                            if update_response.status_code in [200, 204]:
                                results.append({"bestellnummer": bestellnummer, "pos_nr": pos_nr, "status": "updated"})
                                continue
                            else:
                                print(f"Update failed: {update_response.status_code}, {update_response.text}")
                                raise HTTPException(
                                    status_code=update_response.status_code,
                                    detail=f"Failed to update position: {update_response.text}"
                                )
                        else:
                            # Position doesn't exist - create it
                            create_data = {k: v for k, v in position.items() if k not in ['id', 'created_at'] and v is not None}
                            print(f"Creating new position with data: {create_data}")
                            
                            response = await client.post(
                                f"{SUPABASE_URL}/rest/v1/positionen",
                                headers=headers,
                                json=create_data
                            )
                            
                            if response.status_code not in [200, 201]:
                                print(f"Create failed: {response.status_code}, {response.text}")
                                raise HTTPException(
                                    status_code=response.status_code,
                                    detail=f"Failed to create position: {response.text}"
                                )
                            
                            results.append({"bestellnummer": bestellnummer, "pos_nr": pos_nr, "status": "created"})
                        
                except KeyError as e:
                    print(f"KeyError processing position {i+1}: {str(e)}")
                    print(f"Position data: {position}")
                    raise HTTPException(status_code=400, detail=f"Missing required field: {str(e)}")
                except Exception as e:
                    print(f"Error processing position {i+1}: {str(e)}")
                    print(f"Position data: {position}")
                    raise
            
            print(f"Successfully processed {len(results)} positions")
            return {"updated": len(results), "results": results}
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in update_positions_batch: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/extract")
async def extract_from_image(file: UploadFile = File(...)):
    """Extract data from uploaded delivery note image"""
    try:
        # Read file content
        content = await file.read()
        
        print(f"Processing file: {file.filename}, size: {len(content)} bytes")
        
        # Check if GEMINI_API_KEY is set
        if not os.getenv("GEMINI_API_KEY"):
            print("WARNING: GEMINI_API_KEY not set. Using less accurate Tesseract OCR.")
        
        # Process image with OCR
        extracted_data = await process_image(content, file.filename)
        
        if not extracted_data:
            error_detail = {
                "error": "Could not extract data from image",
                "details": "No order number (BL-) or position items (FL-) found in the document",
                "suggestions": [
                    "Ensure the image is a delivery note with BL- order numbers",
                    "Check image quality - text should be clear and readable",
                    "For better accuracy, set GEMINI_API_KEY environment variable"
                ]
            }
            raise HTTPException(status_code=422, detail=error_detail)
        
        # Insert order if bestellnummer exists
        if extracted_data.get("bestellnummer"):
            async with httpx.AsyncClient() as client:
                # Check if order already exists
                check_response = await client.get(
                    f"{SUPABASE_URL}/rest/v1/bestellungen?bestellnummer=eq.{extracted_data['bestellnummer']}",
                    headers=headers
                )
                
                if check_response.status_code == 200 and not check_response.json():
                    # Order doesn't exist, create it
                    order_data = {"bestellnummer": extracted_data["bestellnummer"]}
                    order_response = await client.post(
                        f"{SUPABASE_URL}/rest/v1/bestellungen",
                        headers=headers,
                        json=order_data
                    )
                    
                    if order_response.status_code not in [200, 201]:
                        raise HTTPException(
                            status_code=order_response.status_code,
                            detail=f"Failed to create order: {order_response.text}"
                        )
                
                # Insert positions
                if extracted_data.get("positionen"):
                    positions_data = [
                        {**pos, "bestellnummer": extracted_data["bestellnummer"]}
                        for pos in extracted_data["positionen"]
                    ]
                    
                    # Debug: Print what we're sending
                    print(f"Sending positions to database: {json.dumps(positions_data, indent=2)}")
                    
                    positions_response = await client.post(
                        f"{SUPABASE_URL}/rest/v1/positionen",
                        headers=headers,
                        json=positions_data
                    )
                    
                    if positions_response.status_code not in [200, 201]:
                        raise HTTPException(
                            status_code=positions_response.status_code,
                            detail=f"Failed to create positions: {positions_response.text}"
                        )
        
        return extracted_data
    except HTTPException:
        # Re-raise HTTPException as-is (don't wrap it)
        raise
    except Exception as e:
        # Only wrap non-HTTP exceptions
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/orders/{bestellnummer}")
async def delete_order(bestellnummer: str):
    """Delete an order and all its positions"""
    try:
        async with httpx.AsyncClient() as client:
            # Delete positions first
            positions_response = await client.delete(
                f"{SUPABASE_URL}/rest/v1/positionen?bestellnummer=eq.{bestellnummer}",
                headers=headers
            )
            
            if positions_response.status_code not in [200, 204]:
                raise HTTPException(
                    status_code=positions_response.status_code,
                    detail=f"Failed to delete positions: {positions_response.text}"
                )
            
            # Delete order
            order_response = await client.delete(
                f"{SUPABASE_URL}/rest/v1/bestellungen?bestellnummer=eq.{bestellnummer}",
                headers=headers
            )
            
            if order_response.status_code not in [200, 204]:
                raise HTTPException(
                    status_code=order_response.status_code,
                    detail=f"Failed to delete order: {order_response.text}"
                )
            
            return {"message": f"Order {bestellnummer} and its positions deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/document-history")
async def create_document_history(history: DocumentHistory):
    """Record a new document generation event"""
    try:
        async with httpx.AsyncClient() as client:
            # Prepare data for insertion
            history_data = {
                "bestellnummer": history.bestellnummer,
                "document_type": history.document_type,
                "generated_by": history.generated_by,
                "document_data": history.document_data,
                "file_path": history.file_path,
                "metadata": history.metadata
            }
            
            # Remove None values
            history_data = {k: v for k, v in history_data.items() if v is not None}
            
            response = await client.post(
                f"{SUPABASE_URL}/rest/v1/document_history",
                headers=headers,
                json=history_data
            )
            
            if response.status_code not in [200, 201]:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to create document history: {response.text}"
                )
            
            return response.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/document-history")
async def get_document_history(bestellnummer: Optional[str] = None):
    """Get document history, optionally filtered by order number"""
    try:
        async with httpx.AsyncClient() as client:
            # Build query URL
            url = f"{SUPABASE_URL}/rest/v1/document_history?select=*&order=generated_at.desc"
            if bestellnummer:
                url += f"&bestellnummer=eq.{bestellnummer}"
            
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch document history: {response.text}"
                )
            
            return response.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/document-history/{history_id}")
async def get_document_history_by_id(history_id: int):
    """Get a specific document history record"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/document_history?id=eq.{history_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch document history: {response.text}"
                )
            
            history = response.json()
            if not history:
                raise HTTPException(status_code=404, detail="Document history not found")
            
            return history[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/document-history/{history_id}")
async def delete_document_history(history_id: int):
    """Delete a document history record"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{SUPABASE_URL}/rest/v1/document_history?id=eq.{history_id}",
                headers=headers
            )
            
            if response.status_code not in [200, 204]:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to delete document history: {response.text}"
                )
            
            return {"message": f"Document history {history_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)