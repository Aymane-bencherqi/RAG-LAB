# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
from datetime import datetime
import numpy as np

app = FastAPI(
    title="ShadowMatrix™ Active Decoy Suite",
    version="4.0.0"
)

class DocumentChunk(BaseModel):
    chunk_id: str
    content: str
    document_source: str

class BufferAuditRequest(BaseModel):
    session_id: str
    retrieved_chunks: List[DocumentChunk]
    # Simulate the text that the AI generated as an output response
    simulated_ai_response: str = ""

# Secret marker key to trace data leaks
HONEY_TOKEN_SECRET = "DECOY_KEY_ENSAM_2026"

latest_audit_data = {
    "session_id": "No active scans yet",
    "peak_risk": "0.0%",
    "verdict": "AWAITING INGESTION",
    "honey_token_compromised": False,
    "chunks": []
}

def analyze_chunk_vector(text: str) -> float:
    text_clean = text.lower().strip()
    imperatives = ["forget", "ignore", "nevermind", "disregard", "override", "commanded"]
    targets = ["tokens", "credentials", "password", "session", "database", "key"]
    
    imp_count = sum(1 for w in imperatives if w in text_clean)
    targ_count = sum(1 for w in targets if w in text_clean)
    
    structural_weight = (imp_count * 4.5) + (targ_count * 3.8)
    if structural_weight == 0: return 1.1
    return float(np.round((1 / (1 + np.exp(-structural_weight + 4.5))) * 100, 2))

@app.post("/audit-buffer")
async def audit_buffer(payload: BufferAuditRequest):
    global latest_audit_data
    try:
        buffer_results = []
        highest_risk_found = 0.0
        system_compromised = False
        
        # Check if the AI's response leaked our hidden honey token secret!
        honey_leaked = HONEY_TOKEN_SECRET in payload.simulated_ai_response
        if honey_leaked:
            system_compromised = True
            highest_risk_found = 100.0
            
        for chunk in payload.retrieved_chunks:
            # Structurally insert our secret honey token into every text chunk behind the scenes
            poison_aware_content = f"{chunk.content} [SYSTEM_METADATA_REF: {HONEY_TOKEN_SECRET}]"
            
            risk_pct = analyze_chunk_vector(chunk.content)
            if risk_pct > highest_risk_found:
                highest_risk_found = risk_pct
                
            is_anomaly = risk_pct >= 75.0 or honey_leaked
            if is_anomaly:
                system_compromised = True
            
            buffer_results.append({
                "chunk_id": chunk.chunk_id,
                "source_file": chunk.document_source,
                "content": poison_aware_content, # The chunk now carries the active decoy trap!
                "risk_index": "100.0%" if honey_leaked and is_anomaly else f"{risk_pct}%",
                "status": "TRIPPED / BLOCKED" if is_anomaly else "PASSED"
            })
            
        verdict = "REJECT_BUFFER_STREAM" if system_compromised else "ALLOW_INGESTION"
        
        latest_audit_data = {
            "session_id": payload.session_id,
            "peak_risk": f"{highest_risk_found}%",
            "verdict": verdict,
            "honey_token_compromised": honey_leaked,
            "chunks": buffer_results
        }
        
        return {"status": "SUCCESS", "verdict": verdict, "honey_token_leaked": honey_leaked}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    status_color = "#e63946" if latest_audit_data["verdict"] == "REJECT_BUFFER_STREAM" else "#2a9d8f"
    if latest_audit_data["session_id"] == "No active scans yet": status_color = "#4a4e69"
    
    decoy_alert_style = "display: block; background-color: #7209b7; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; text-align: center; color: #fff;" if latest_audit_data["honey_token_compromised"] else "display: none;"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ShadowMatrix™ Active Command Console</title>
        <meta http-equiv="refresh" content="2">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d0e15; color: #e2e8f0; margin: 40px; }}
            .container {{ max-width: 1200px; margin: auto; }}
            h1 {{ color: #ffffff; border-bottom: 2px solid #1e293b; padding-bottom: 10px; font-weight: 400; }}
            .card {{ background-color: #161923; border: 1px solid #2d3748; padding: 20px; border-radius: 8px; flex: 1; }}
            .verdict-banner {{ background-color: {status_color}; color: white; padding: 20px; border-radius: 8px; font-weight: bold; font-size: 24px; text-align: center; letter-spacing: 2px; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; background-color: #161923; border-radius: 8px; overflow: hidden; }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #2d3748; }}
            th {{ background-color: #1e2330; color: #94a3b8; font-size: 11px; text-transform: uppercase; }}
            .badge-passed {{ background-color: #10b98120; color: #10b981; border: 1px solid #10b98140; padding: 5px 10px; border-radius: 4px; font-size: 12px; }}
            .badge-blocked {{ background-color: #ef444420; color: #ef4444; border: 1px solid #ef444440; padding: 5px 10px; border-radius: 4px; font-size: 12px; font-weight:bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SHADOWMATRIX™ // Active Decoy Engine</h1>
            
            <div id="decoyAlert" style="{decoy_alert_style}">
                🪤 [HONEY-TOKEN TRIPPED]: The LLM actively attempted to exfiltrate decoy keys!
            </div>

            <div class="verdict-banner">PIPELINE VERDICT: {latest_audit_data["verdict"]}</div>

            <div style="display: flex; gap: 20px; margin-bottom: 30px;">
                <div class="card">
                    <small style="color: #64748b;">ACTIVE SESSION REF</small>
                    <div style="font-size: 20px; font-weight: bold; margin-top: 5px; color: #38bdf8;">{latest_audit_data["session_id"]}</div>
                </div>
                <div class="card">
                    <small style="color: #64748b;">PEAK RISK PROFILE</small>
                    <div style="font-size: 20px; font-weight: bold; margin-top: 5px; color: #f43f5e;">{latest_audit_data["peak_risk"]}</div>
                </div>
            </div>

            <h3>ACTIVE PIPELINE MEMORY EXTRAPOLATION</h3>
            <table>
                <thead>
                    <tr><th>Chunk ID</th><th>Source Document</th><th>Decoy Injected Text Content</th><th>Threat Weight</th><th>Status</th></tr>
                </thead>
                <tbody>
    """
    for chunk in latest_audit_data["chunks"]:
        badge = "badge-blocked" if chunk["status"] == "TRIPPED / BLOCKED" else "badge-passed"
        html_content += f"""
                    <tr>
                        <td style="font-family: monospace; color: #38bdf8;">{chunk["chunk_id"]}</td>
                        <td><b>{chunk["source_file"]}</b></td>
                        <td style="color: #cbd5e1; font-size: 13px;">{chunk["content"]}</td>
                        <td style="color: #f43f5e; font-weight: bold;">{chunk["risk_index"]}</td>
                        <td><span class="{badge}">{chunk["status"]}</span></td>
                    </tr>
        """
    html_content += "</tbody></table></div></body></html>"
    return html_content