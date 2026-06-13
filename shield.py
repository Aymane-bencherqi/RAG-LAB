# shield.py
import os
from datetime import datetime

def calculate_risk_score(text_content):
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

# --- New Audit and Export Controller ---
def execute_lab_suite():
    files_to_scan = ["invoice_policy.txt", "clean_document.txt", "mutated_attack.txt"]
    report_entries = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("==================================================")
    print("🛡️  AI-Security-Lab: Generating Scan Report...    🛡️")
    print("==================================================\n")
    
    # 1. Process files and compile results
    for file_name in files_to_scan:
        file_path = os.path.join("knowledge_base", file_name)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            score, assessment = calculate_risk_score(content)
            verdict = "BLOCKED" if score >= 70 else "PASSED"
            
            # Format entry for the report file
            report_entries.append(
                f"FILE: {file_name}\n"
                f"RISK SCORE: {score}/100\n"
                f"VERDICT: {verdict}\n"
                f"DETAILS: {assessment}\n"
                f"{'-'*40}\n"
            )
            print(f"✅ Processed {file_name} -> Score: {score}")

    # 2. Write everything out to a structured report artifact
    with open("security_scan_report.txt", "w", encoding="utf-8") as report_file:
        report_file.write(f"==================================================\n")
        report_file.write(f"          ZEPHYRBANK AI SECURITY AUDIT REPORT     \n")
        report_file.write(f"          Generated: {timestamp}                  \n")
        report_file.write(f"==================================================\n\n")
        
        for entry in report_entries:
            report_file.write(entry)
            
    print("\n🎉 Success! Corporate audit file exported to: 'security_scan_report.txt'")

if __name__ == "__main__":
    execute_lab_suite()