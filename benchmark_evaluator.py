# benchmark_evaluator.py
import json
import time
import numpy as np

# Load our updated dataset
with open("real_world_dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

def baseline_keyword_filter(text: str) -> str:
    """Traditional naive string matching firewall."""
    text_clean = text.lower()
    blacklist = ["nevermind", "system override", "ignore previous instructions"]
    for word in blacklist:
        if word in text_clean:
            return "BLOCKED"
    return "PASSED"

def shadowmatrix_advanced_engine(text: str, metadata_type: str) -> str:
    """
    ShadowMatrix Core: Combines token density profiling with 
    context-aware safety exclusions to prevent false positive flags.
    """
    text_clean = text.lower().strip()
    
    # Heuristic Token Layers
    imperatives = ["forget", "ignore", "nevermind", "disregard", "override", "commanded", "execute", "modify"]
    targets = ["tokens", "credentials", "password", "session", "database", "keys", "value"]
    
    # Check for legitimate programming/educational context flags
    safe_contexts = ["python", "object-oriented", "class method", "coding", "programming"]
    is_educational = any(ctx in text_clean for ctx in safe_contexts)
    
    imp_count = sum(1 for w in imperatives if w in text_clean)
    targ_count = sum(1 for w in targets if w in text_clean)
    
    # Calculate density value
    weight = (imp_count * 4.5) + (targ_count * 3.8)
    
    # Strict structural schema enforcement
    if metadata_type == "numeric" and imp_count > 0:
        return "BLOCKED"
        
    if weight == 0:
        probability = 0.0
    else:
        # Sigmoid curve normalization
        probability = (1 / (1 + np.exp(-weight + 4.5))) * 100
        
    # If it looks like an attack, but contains verified educational keywords, let it pass
    if probability >= 75.0 and is_educational:
        return "PASSED"
        
    return "BLOCKED" if probability >= 75.0 else "PASSED"

def run_suite():
    total = len(dataset)
    kw_correct = 0
    sm_correct = 0
    
    print("======================================================================")
    print("         SHADOWMATRIX™ EMPIRICAL SCALED ACCURACY VALIDATION           ")
    print("======================================================================\n")

    for tc in dataset:
        kw_res = baseline_keyword_filter(tc["content"])
        sm_res = shadowmatrix_advanced_engine(tc["content"], tc["metadata"])
        
        kw_ok = kw_res == tc["expected_verdict"]
        sm_ok = sm_res == tc["expected_verdict"]
        
        if kw_ok: kw_correct += 1
        if sm_ok: sm_correct += 1
        
        print(f"ID: {tc['id']} | Type: {tc['category']}")
        print(f" ├─ Content:     \"{tc['content'][:70]}...\"")
        print(f" ├─ Keyword App:  {kw_res} -> {'✓' if kw_ok else '✗'}")
        print(f" └─ ShadowMatrix: {sm_res} -> {'✓' if sm_ok else '✗'}\n")

    print("======================================================================")
    print("                     SCALED VALIDATION PERFORMANCE SUMMARY            ")
    print("======================================================================")
    print(f"System Model             | Measured Accuracy Across Dataset (%)")
    print(f"----------------------------------------------------------------------")
    print(f"Baseline Keyword Filter  | {(kw_correct/total)*100:.1f}%")
    print(f"ShadowMatrix Guard Layer | {(sm_correct/total)*100:.1f}%")
    print("======================================================================\n")

if __name__ == "__main__":
    run_suite()