# shield.py
import os
from datetime import datetime

def calculate_risk_score(text_content):
    """Evaluates text and calculates an objective risk score from 0 to 100."""
    score = 0
    text_clean = text_content.lower()
    
    critical_triggers = ["ignore previous instructions", "nevermind", "system override", "override your safety"]
    medium_triggers = ["update your credentials", "input your password", "session tokens", "login before proceeding"]
    
    for trigger in critical_triggers:
        if trigger in text_clean:
            score += 100
            return min(score, 100), f"CRITICAL: Found system override trigger '{trigger}'"
            
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

def run_audit(file_name):
    """Helper function to load a file and process its security score."""
    file_path = os.path.join("knowledge_base", file_name)
    print(f"📥 Fetching database chunk: '{file_path}'...")
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        risk_score, assessment = calculate_risk_score(content)
        
        print(f"📊 --- SECURITY AUDIT MATRIX FOR {file_name} ---")
        print(f"🔢 Calculated Risk Score: {risk_score} / 100")
        print(f"¼ Verdict Assessment:    {assessment}")
        
        if risk_score >= 70:
            print("🛑 [BLOCK]: Transaction dropped. Critical risk detected.")
        else:
            print("✅ [PASS]: Document cleared. Within normal operating metrics.")
        print("-" * 60)
    else:
        print(f"❌ Error: Missing file '{file_path}'")

# --- Run the Multi-File Matrix Test ---
print("==================================================")
print("🛡️  AI-Security-Lab: Multi-File Testing Matrix   🛡️")
print("==================================================\n")

# Test the poisoned file
run_audit("invoice_policy.txt")

# Test the clean file
run_audit("clean_document.txt")