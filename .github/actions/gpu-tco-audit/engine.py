import os
import json
from datetime import datetime

def calculate_audit():
    gpu = os.getenv('INPUT_GPU_MODEL', 'H100')
    nodes = int(os.getenv('INPUT_NODE_COUNT', 1))
    
    efficiency_map = {"H100": 0.85, "B200": 0.98, "A100": 0.70}
    perf = efficiency_map.get(gpu, 0.50)
    
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "gpu_model": gpu,
        "node_count": nodes,
        "efficiency_score": f"{perf * 100}%",
        "status": "Strategic Analysis Complete"
    }

    # Veriyi kaydet
    os.makedirs('reports', exist_ok=True)
    with open('reports/latest_audit.json', 'w') as f:
        json.dump(report_data, f, indent=4)
    
    print(f"Report generated and saved to reports/latest_audit.json")

if __name__ == "__main__":
    calculate_audit()
