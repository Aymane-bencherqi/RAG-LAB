# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

# Initialize the web application
app = FastAPI(
    title="AI-Security-Gateway API",
    description="Production-ready heuristic layer for intercepting Indirect Prompt Injections.",
    version="1.0.0"
)

# Define what the incoming request payload data must look like
class ScanRequest(BaseModel):
    document_content: str
    source_identifier: str = "unknown_source"

# Define the security scoring logic directly inside the API loop
def evaluate_text_risk(text_content: str):
    score = 0
    text_clean = text_content.lower()
    found_indicators = []
    
    critical_indicators = ["ignore previous", "nevermind", "system override", "override your safety"]
    mutated_indicators = ["disregard", "forget your prior", "commanded to", "unrestricted", "ignore structural"]
    phishing_indicators = ["update your credentials", "tokens", "login before proceeding"]

    for indicator in critical_indicators:
        if indicator in text_clean:
            return 100, f"CRITICAL: Direct override trigger found -> '{indicator}'"

    for indicator in mutated_indicators:
        if indicator in text_clean:
            score += 40
            found_indicators.append(indicator)
            
    for indicator in phishing_indicators:
        if indicator in text_clean:
            score += 30
            found_indicators.append(indicator)

    final_score = min(score, 100)
    
    if final_score >= 70:
        return final_score, f"HIGH RISK: Detected combined adversarial signature pattern: {found_indicators}"
    elif final_score >= 35:
        return final_score, f"MEDIUM RISK: Suspicious linguistic anomalies detected: {found_indicators}"
        
    return 0, "LOW RISK: No threat patterns identified."


# --- THE WEB ROUTE (API ENDPOINT) ---
@app.post("/scan")
async def scan_document(payload: ScanRequest):
    """
    Receives text context over HTTP POST, evaluates malicious density, 
    and returns a structured security verdict.
    """
    try:
        # Run the text from the HTTP request through the engine
        risk_score, assessment = evaluate_text_risk(payload.document_content)
        verdict = "BLOCKED" if risk_score >= 70 else "PASSED"
        
        # Build a highly detailed structured response
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "target_source": payload.source_identifier,
            "metrics": {
                "risk_score": risk_score,
                "max_threshold": 100,
                "danger_level": "CRITICAL" if risk_score == 100 else ("HIGH" if risk_score >= 70 else ("MEDIUM" if risk_score >= 35 else "LOW"))
            },
            "verdict": verdict,
            "remediation_details": assessment
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Gateway Processing Error: {str(e)}")

# Add a simple health check route
@app.get("/")
def read_root():
    return {"status": "ONLINE", "engine": "AI-Security-Gateway-v1"}