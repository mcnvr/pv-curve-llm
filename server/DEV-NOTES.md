# Temporary Notes File

While in the earliest development stages, this is temporary for me to keep track of what I need to add to the README.md soon to stay more organized

PV-Curve functionality might not work well. At this time, I have no Power Systems experience and am still learning/reseraching basics.

## Overview

manual-pv_curve.py - run this file locally to test PV Curve generation

llm-pv_curve.py - Similar to manual-pv_curve.py but designed for LLM use and outside function calls

## TODO

[_] Create README.md
[_] Create virtual environment or Docker container
[_] Set up Deepseek model locally

## Helpful resources

- https://www.youtube.com/watch?v=L0TGm3C5Snw
- https://www.ecsp.ch/

## Necessary Dependencies

### Core Power Systems Analysis
- **pandapower** (>=3.0.0) - Power system analysis library for electrical networks
  - `pandapower.networks` - IEEE test case networks (case14, case30, case39, case118)
  - Used for power flow calculations and voltage stability analysis

### Scientific Computing & Data Processing  
- **numpy** (>=1.20.0) - Numerical computing library
  - Array operations for power/voltage data
  - Linear algebra for scaling operations
  - Mathematical functions (sqrt, linspace, etc.)

### Visualization & Plotting
- **matplotlib** (>=3.5.0) - Plotting library for PV curves
  - `matplotlib.pyplot` - Main plotting interface
  - Generates PV curves, current vs power plots
  - Saves graphs as PNG files with annotations

### Data Handling & Encoding
- **io** (built-in) - Input/output operations
  - BytesIO for in-memory plot storage
  - Base64 encoding for web applications
- **base64** (built-in) - Binary to text encoding
  - Converts plots to base64 for web display

### File System & Organization  
- **os** (built-in) - Operating system interface
  - Directory creation and file path management
  - Cross-platform path handling
- **shutil** (built-in) - High-level file operations
  - Used in clear_generated_graphs() for directory removal

### Date & Time Management
- **datetime** (built-in) - Date and time operations
  - Timestamp generation for run directories
  - Analysis metadata with execution times

### Type Hints & Code Quality
- **typing** (built-in) - Type hints for better code documentation
  - `Tuple, List, Optional, Dict, Any` - Function signatures
  - Improves code readability and IDE support

### Web Framework (for llm-pv_curve.py)
- **flask** - Web framework for API endpoints
  - HTTP request/response handling
  - JSON data serialization

### Python Version Requirements
- **Python >= 3.8** - Required for type hints and modern syntax
- Compatible with pandapower 3.0+ requirements

## Potential tools for RAG:

- Langchain
- llamaindex
    - https://github.com/run-llama/llama_index

## MCP

- TODO