import json
from pathlib import Path
from datetime import datetime
from .graph import build_graph
from .agents import MODEL

def run_order(request):
    result = build_graph().invoke({"raw_order": request, "issues": [], "execution_log": [], "replanned": False})
    report = result["final_report"]
    out = Path("outputs")
    out.mkdir(exist_ok=True)
    path = out / f"warehouse_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report, path

def main():
    print("="*65 + "\nROBOAGENT AI — MULTI-AGENT WAREHOUSE SIMULATION")
    print(f"Local LLM: {MODEL}\nType an order in plain English; type 'exit' to quit.")
    while True:
        request = input("\nWarehouse order> ").strip()
        if request.lower() in {"exit", "quit"}: break
        if not request: continue
        try:
            report, path = run_order(request)
            print("\nORDER SUMMARY")
            print(json.dumps({k: report[k] for k in ["order","inventory_available","tasks","robot_assignments","issues","replanned","completed_tasks","total_tasks"]}, indent=2))
            print("\nEXECUTION LOG")
            for line in report["execution_log"]: print(" •", line)
            print(f"\nJSON report saved: {path}")
        except Exception as e:
            print(f"Request failed: {type(e).__name__}: {e}")
            print("Check Ollama is running and the model is installed.")
if __name__ == "__main__": main()
