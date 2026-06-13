# shield.py
import os
from datetime import datetime

def calculate_risk_score(text_content):
    """
    Evaluates text and calculates an objective risk score from 0 to 100
    based on threat indicators.
    """
    score = 0
    text_clean = text_content.lower()
    
    # 1. High-Severity Triggers (Direct Hijacking attempts)
    critical_triggers = ["ignore previous instructions", "nevermind", "system override", "override your safety"]
    # 2. Medium-Severity Triggers (Phishing behavioral signals)
    medium_triggers = ["update your credentials", "input your password", "session tokens", "login before proceeding"]
    
    # Check for Critical Threats (Max out the score immediately)
    for trigger in critical_triggers:
        if trigger in text_clean:
            score += 100
            return min(score, 100), f"CRITICAL: Found system override trigger '{trigger}'"
            
    # Check for Medium/Phishing Threats (Accumulate risk)
    found_mediums = []
    for trigger in medium_triggers:
        if trigger in text_clean:
            score += 35
            found_mediums.append(trigger)
            
    if score >= 70:
        return min(score, 100), f"HIGH RISK: Multiple phishing indicators found {found_mediums}"
    elif score > 0:
        return score, f"MEDIUM RISK: Singular phishing indicator found {found_mediums}"
        
    return 0, "LOW RISK: No threat patterns identified."

# --- RAG Execution Suite ---
print("==================================================")
print("🛡️  AI-Security-Lab: Risk Scoring Engine v1.0    🛡️")
print("==================================================\n")

file_path = os.path.join("knowledge_base", "invoice_policy.txt")
print(f"📥 Fetching database chunk: '{file_path}'...")

if os.path.exists(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        document_content = f.read()
        
    # Run the scoring engine
    risk_score, assessment = calculate_risk_score(document_content)
    
    print(f"\n📊 --- SECURITY AUDIT MATRIX ---")
    print(f"🔢 Calculated Risk Score: {risk_score} / 100")
    print(f"📝 Assessment Verdict:   {assessment}")
    print(f"---------------------------------")
    
    # Dynamic decision boundary based on the score
    if risk_score >= 70:
        print("🛑 [BLOCK]: Transaction dropped. Risk threshold exceeded standard tolerance.")
    elif risk_score >= 35:
        print("⚠️ [WARN]: Transaction passed with sanitized clearance. Alert logged to CISO.")
    else:
        print("✅ [PASS]: Document within acceptable baseline parameters.")
    print()
else:
    print("❌ Error: Missing 'knowledge_base/invoice_policy.txt'.")