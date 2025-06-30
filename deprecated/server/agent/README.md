# AI Agent

AI Agent which creates PV curves or answers Voltage Stability related requests using LLMs and RAG.

## TODO

- [ ] Improve `/agent` documentation
- [ ] Improve prompts in `prompts.json`
- [ ] Review and improve PV Curve inputs in `inputs.json`
- [ ] Create function to generate PV Curves using inputs from `inputs.json`
- [ ] Add documentation/graph for agentic workflow
- [ ] Add LangGraph node to generate PV curve
- [ ] Add LangGraph node to review PV curve and process user feedback
- [ ] Research/review legality of the data stored in `/data` in Open-Source repo. More info in `/data/README.md` 

## Installation & Run

Run Agent locally:

```bash
cd /server/ai
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```