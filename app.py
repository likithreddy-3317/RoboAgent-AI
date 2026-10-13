import json, os
import streamlit as st
from roboagent.cli import run_order

st.set_page_config(page_title="RoboAgent AI", page_icon="🤖", layout="wide")
st.title("🤖 RoboAgent AI")
st.caption("Multi-agent warehouse management and simulated robotic task execution")
st.warning("Simulation only. This app does not control physical robot hardware.")
request = st.text_area("Warehouse order", "Process high-priority order 1042: pick 2 wireless mice, 1 keyboard, and 1 USB-C hub.")
inject = st.checkbox("Inject a simulated R1 failure to demonstrate re-planning")
if st.button("Process order", type="primary"):
    os.environ["ROBOAGENT_INJECT_FAILURE"] = "1" if inject else "0"
    with st.spinner("Agents are processing the order..."):
        try:
            report, path = run_order(request)
            a,b,c = st.columns(3)
            a.metric("Tasks completed", f'{report["completed_tasks"]}/{report["total_tasks"]}')
            b.metric("Inventory available", "Yes" if report["inventory_available"] else "No")
            c.metric("Replanned", "Yes" if report["replanned"] else "No")
            st.subheader("Agent decisions")
            st.json({"order":report["order"], "inventory_checks":report["inventory_checks"], "robot_assignments":report["robot_assignments"], "routes":report["routes"], "issues":report["issues"]})
            st.subheader("Execution log")
            for line in report["execution_log"]: st.write("•", line)
            st.download_button("Download JSON report", json.dumps(report, indent=2), file_name=path.name, mime="application/json")
        except Exception as e: st.error(f"{type(e).__name__}: {e}")
