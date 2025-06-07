-- Create document_history table for tracking generated documents
CREATE TABLE IF NOT EXISTS document_history (
    id SERIAL PRIMARY KEY,
    bestellnummer VARCHAR(255) NOT NULL,
    document_type VARCHAR(50) NOT NULL CHECK (document_type IN ('lieferschein', 'laufkarte', 'rechnung')),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    generated_by VARCHAR(255),
    document_data JSONB,
    file_path VARCHAR(500),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_document_history_bestellnummer ON document_history(bestellnummer);
CREATE INDEX idx_document_history_generated_at ON document_history(generated_at DESC);
CREATE INDEX idx_document_history_document_type ON document_history(document_type);

-- Add RLS (Row Level Security) policies if needed
ALTER TABLE document_history ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust based on your security needs)
CREATE POLICY "Enable all operations for document_history" ON document_history
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Add comment to table
COMMENT ON TABLE document_history IS 'Tracks all generated documents (Lieferschein, Laufkarte, Rechnung) with their data snapshots';
COMMENT ON COLUMN document_history.bestellnummer IS 'Order number from bestellungen table';
COMMENT ON COLUMN document_history.document_type IS 'Type of document: lieferschein, laufkarte, or rechnung';
COMMENT ON COLUMN document_history.generated_at IS 'Timestamp when the document was generated';
COMMENT ON COLUMN document_history.generated_by IS 'User or system that generated the document';
COMMENT ON COLUMN document_history.document_data IS 'Complete snapshot of order data at generation time';
COMMENT ON COLUMN document_history.file_path IS 'Optional path to stored PDF file';
COMMENT ON COLUMN document_history.metadata IS 'Additional metadata like version, notes, etc.';