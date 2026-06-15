# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
from datetime import datetime
import numpy as np

app = FastAPI(
    title="ShadowMatrix™ Enterprise Security Suite",
    version="3.5.0"
)

class DocumentChunk(BaseModel):
    chunk_id: str
    content: str
    document_source: str

class BufferAuditRequest(BaseModel):
    session_id: str
    retrieved_chunks: List[DocumentChunk]

# Keep our live memory state to show on the web interface
latest_audit_data = {
    "session_id": "No active scans yet",
    "peak_risk": "0.0%",
    "verdict": "AWAITING INGESTION",
    "chunks": []
}

def analyze_chunk_vector(text: str) -> float:
    text_clean = text.lower().strip()
    imperatives = ["forget", "ignore", "nevermind", "disregard", "override", "commanded", "stop acting"]
    targets = ["tokens", "credentials", "password", "session", "database", "admin", "dump", "flag"]
    
    imp_count = sum(1 for w in imperatives if w in text_clean)
    targ_count = sum(1 for w in targets if w in text_clean)
    
    structural_weight = (imp_count * 4.5) + (targ_count * 3.8)
    if structural_weight == 0:
        return 1.1  # Safe baseline floor
        
    probability = (1 / (1 + np.exp(-structural_weight + 4.5))) * 100
    return float(np.round(probability, 2))

@app.post("/audit-buffer")
async def audit_buffer(payload: BufferAuditRequest):
    global latest_audit_data
    try:
        buffer_results = []
        highest_risk_found = 0.0
        system_compromised = False
        
        for chunk in payload.retrieved_chunks:
            risk_pct = analyze_chunk_vector(chunk.content)
            if risk_pct > highest_risk_found:
                highest_risk_found = risk_pct
                
            is_anomaly = risk_pct >= 75.0
            if is_anomaly:
                system_compromised = True
            
            buffer_results.append({
                "chunk_id": chunk.chunk_id,
                "source_file": chunk.document_source,
                "content": chunk.content,
                "risk_index": f"{risk_pct}%",
                "status": "BLOCKED" if is_anomaly else "PASSED"
            })
            
        verdict = "REJECT_BUFFER_STREAM" if system_compromised else "ALLOW_INGESTION"
        
        # Save payload parameters into global memory for the web view
        latest_audit_data = {
            "session_id": payload.session_id,
            "peak_risk": f"{highest_risk_found}%",
            "verdict": verdict,
            "chunks": buffer_results
        }
        
        return {"status": "SUCCESS", "verdict": verdict, "peak_risk": f"{highest_risk_found}%"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🎨 THE INNOVATION: The Visual Auditor Command Center HTML Endpoint
@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    status_color = "#e63946" if latest_audit_data["verdict"] == "REJECT_BUFFER_STREAM" else "#2a9d8f"
    if latest_audit_data["session_id"] == "No active scans yet": status_color = "#4a4e69"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ShadowMatrix™ Auditor Interface</title>
        <meta http-equiv="refresh" content="3"> <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f111a; color: #e2e8f0; margin: 40px; }}
            .container {{ max-width: 1200px; margin: auto; }}
            h1 {{ color: #ffffff; border-bottom: 2px solid #1e293b; padding-bottom: 10px; font-weight: 400; }}
            .header-panel {{ display: flex; gap: 20px; margin-bottom: 30px; }}
            .card {{ background-color: #1a1d29; border: 1px solid #2d3748; padding: 20px; border-radius: 8px; flex: 1; }}
            .verdict-banner {{ background-color: {status_color}; color: white; padding: 25px; border-radius: 8px; font-weight: bold; font-size: 24px; text-align: center; letter-spacing: 2px; margin-bottom: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background-color: #1a1d29; border-radius: 8px; overflow: hidden; }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #2d3748; }}
            th {{ background-color: #1e2230; color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }}
            .badge {{ padding: 5px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
            .badge-passed {{ background-color: #10b98120; color: #10b981; border: 1px solid #10b98140; }}
            .badge-blocked {{ background-color: #ef444420; color: #ef4444; border: 1px solid #ef444440; animation: blink 1.5s infinite; }}
            @keyframes blink {{ 50% {{ opacity: 0.5; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SHADOWMATRIX™ // RAG Context Buffer Interceptor</h1>
            
            <div class="verdict-banner">
                PIPELINE VERDICT: {latest_audit_data["verdict"]}
            </div>

            <div class="header-panel">
                <div class="card">
                    <small style="color: #64748b;">ACTIVE SESSION REF</small>
                    <div style="font-size: 20px; font-weight: bold; margin-top: 5px; color: #38bdf8;">{latest_audit_data["session_id"]}</div>
                </div>
                <div class="card">
                    <small style="color: #64748b;">PEAK BUFFER RISK INDEX</small>
                    <div style="font-size: 20px; font-weight: bold; margin-top: 5px; color: #f43f5e;">{latest_audit_data["peak_risk"]}</div>
                </div>
            </div>

            <h3>CONTEXT STREAM REAL-TIME MAP</h3>
            <table>
                <thead>
                    <tr>
                        <th>Chunk ID</th>
                        <th>Source Document Name</th>
                        <th>Extracted Document Text Fragment</th>
                        <th>Semantic Risk</th>
                        <th>Action Status</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for chunk in latest_audit_data["chunks"]:
        badge_class = "badge-blocked" if chunk["status"] == "BLOCKED" else "badge-passed"
        html_content += f"""
                    <tr>
                        <td style="font-family: monospace; color: #38bdf8;">{chunk["chunk_id"]}</td>
                        <td style="font-weight: bold;">{chunk["source_file"]}</td>
                        <td style="color: #cbd5e1; font-size: 14px;">"{chunk["content"]}"</td>
                        <td style="font-weight: bold; color: #f43f5e;">{chunk["risk_index"]}</td>
                        <td><span class="badge {badge_class}">{chunk["status"]}</span></td>
                    </tr>
        """
        
    html_content += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return html_content