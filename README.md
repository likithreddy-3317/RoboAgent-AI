# RoboAgent AI — Main Project

**Goal:** Build an AI-powered multi-agent warehouse system that understands orders, inspects inventory, plans tasks, allocates simulated robots, executes simulated picking, monitors execution, detects failures, and re-plans incomplete work.

> Safety boundary: this is a software simulation, not a physical robot controller or an industrially validated system.

## Agents
1. **Order Agent:** local Ollama LLM + Pydantic structured output.
2. **Inventory Agent:** checks stock and storage location.
3. **Planning Agent:** decomposes the order into picking tasks.
4. **Robot Allocation Agent:** assigns robots with battery >= 30%.
5. **Route Agent:** uses Dijkstra shortest-path routing.
6. **Execution Agent:** simulates travel, picking and delivery.
7. **Monitoring Agent:** detects incomplete tasks.
8. **Replanning Agent:** reallocates incomplete tasks after a simulated failure.
9. **Report Agent:** writes an auditable JSON report.

LangGraph coordinates the workflow using a shared state. Inventory, robots and routes are deterministic demo data.

## macOS setup
Run commands from the extracted `roboagent_ai` project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
ollama pull qwen2.5:3b
```

Ensure the Ollama app is running. If needed, use a separate terminal with `ollama serve`.

## Run CLI
```bash
python -m roboagent.cli
```
Example:
```text
Process high-priority order 1042: pick 2 wireless mice, 1 keyboard, and 1 USB-C hub.
```
Reports are written to `outputs/`.

## Run dashboard
```bash
streamlit run app.py
```
Use the failure checkbox to inject one simulated R1 failure and demonstrate the re-planning path.

## Failure injection from CLI
```bash
export ROBOAGENT_INJECT_FAILURE=1
python -m roboagent.cli
```
Reset it with `unset ROBOAGENT_INJECT_FAILURE`.

## Demo products
wireless mouse, keyboard, usb-c hub, camera, tripod. Edit `roboagent/warehouse.py` to change inventory, robots, and the warehouse graph.

## Evaluation scenarios
- Normal order with available items.
- Request more stock than inventory contains.
- Unknown product.
- Failure injection with re-planning.

## Current limitations
The first version uses static in-memory demo inventory, a small route graph, and simulated actions. It does not include persistent database updates, live sensor data, ROS 2, or physical robot control. These are suitable future extensions.
