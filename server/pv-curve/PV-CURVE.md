# Power–Voltage (PV) Curve Analysis for AC Power-System Voltage Stability  

## 1. What is a PV Curve?
A Power–Voltage (PV) curve plots the steady-state bus-voltage magnitude (V) versus the total system active-power demand (P).  
The characteristic "nose" of the curve indicates the **voltage-collapse (saddle-node bifurcation) point**, beyond which the power flow equations have no feasible solution.  PV curves are therefore a primary tool for:

* Identifying the maximum loadability of a power system.
* Quantifying voltage-stability (voltage-security) margins.
* Studying the influence of distributed generation (e.g., rooftop PV) and reactive-power compensation on feeder voltage profiles.  

_Practical classroom example:_ The University of Washington's distribution-feeder laboratory exercise shows how rooftop PV can cause over-voltages and rapid voltage fluctuations along radial feeders when the local generation exceeds the load [UW-CEI2020](https://www.cei.washington.edu/lesson-plans-resources/simulating-the-impact-of-pv-generation-on-power-system-voltage/).

---
## 2. Mathematical Background
For an n-bus AC system the power-flow equations are

\[\begin{aligned}
P_i &= V_i\sum_{k=1}^n V_k\left(G_{ik}\cos\theta_{ik} + B_{ik}\sin\theta_{ik}\right)\\[2pt]
Q_i &= V_i\sum_{k=1}^n V_k\left(G_{ik}\sin\theta_{ik} - B_{ik}\cos\theta_{ik}\right)
\end{aligned}\]

where \(G_{ik}+jB_{ik}\) is the admittance matrix and \(\theta_{ik}=\delta_i-\delta_k\).  A PV curve is obtained by _continuation_ of these nonlinear equations as load is **uniformly increased** by a scalar factor \(\lambda\):

\[P_{\text{load}}(\lambda)=\lambda P_{\text{base}},\qquad Q_{\text{load}}(\lambda)=\lambda Q_{\text{base}}\]

The system is solved repeatedly (e.g., Newton–Raphson) while gradually increasing \(\lambda\) until the Jacobian becomes singular (\(\det J =0\)).  The corresponding voltage at the monitored bus is the collapse point.  **Continuation-power-flow (CPF)** with a predictor–corrector scheme is preferred to simple incremental load flow because it can track the curve past turning points.

---
## 3. Typical Workflow
1. **Load an IEEE or user-supplied test network** (e.g., IEEE-39-bus New England system).  
2. **Select a monitored bus** (usually a weak PQ bus).  
3. **Define load-scaling parameters** (max scale, step size or number of points).  
4. **Run CPF / repeated AC power-flow** until convergence fails or the chosen maximum scale is reached.  
5. **Store \(\lambda\) vs. \(V\)** pairs and plot the graph.  
6. Optionally compute voltage-stability margin (distance from operating point to nose).

Packages such as `pandapower`, `PYPOWER`, or commercial tools (PSS®E, PowerWorld) provide CPF utilities.  The lightweight routine in `server/pv-curve/llm-pv_curve.py` uses `pandapower` and writes the resulting PNG to `server/pv-curve/generated-graphs/`.

---
## 4. Input Parameters
| Category | Parameter | Type / Unit | Recommended Range | Notes |
|----------|-----------|------------|-------------------|-------|
| **Network** | `network_case` | string | `case14`, `case30`, `case39`, `case118`, … | IEEE test cases shipped with `pandapower` |
|  | *or* `custom_net` | `pandapowerNet` object | – | Pass an already-built network |
| **Monitored Bus** | `bus_idx` | int | 0 – N-1 | Choose a PQ bus prone to instability |
| **Load Scaling** | `max_scale` | float (p.u.) | 1.1 – 4.0 | 1.0 = base load |
|  | `num_points` | int | 20 – 200 | Uniform steps: `step = (max_scale-1)/(num_points-1)` |
| **Solver Options** | `algorithm` | str | `nr`, `bfsw`, `fdbx`, … | Newton–Raphson (nr) recommended |
|  | `tolerance_mva` | float | 1e-6 – 1e-10 | Power-mismatch tolerance |
|  | `max_iterations` | int | 10 – 30 | Per AC power-flow solve |
| **Physical Models** | `voltage_depend_loads` | bool | True/False | ZIP-load modelling |
|  | `enforce_q_lims` | bool | True/False | Respect generator Q limits |
| **Output** | `return_plot` | bool | True/False | Return base64 plot string |
|  | `run_directory` | str | path | Where to save PNG (default auto-timestamp in `generated-graphs`) |

### Minimal Example
```python
from pv_curve import create_pv_curve

result = create_pv_curve(
    network_case="case39",   # 39-bus New England system
    bus_idx=15,
    max_scale=2.0,
    num_points=41
)
print(result["nose_point"])
```
The call generates `.../generated-graphs/run_YYYYMMDD_HHMMSS/pv_curve.png`.

---
## 5. Practical Guidelines
* **Step size**: Use finer steps (≥ 60 points) near the expected nose to capture the sharp voltage drop.
* **Reactive-power limits**: When a generator hits its Q-limit the PV curve can exhibit a kink _before_ the saddle-node bifurcation – treat this as a separate stability limit.
* **Distributed PV**: High rooftop-PV penetration can shift the curve left (lower loading capability) or even introduce over-voltage problems under light load [UW-CEI2020](https://www.cei.washington.edu/lesson-plans-resources/simulating-the-impact-of-pv-generation-on-power-system-voltage/).
* **Temporal Studies**: Combine PV curves with 15-minute PV-output / load data sets to evaluate diurnal voltage-stability margins [NREL-Forum](https://sam.nrel.gov/forum/forum-general/3795-modeling-graphing-load-data-vs-pv-output-data-on-15-min-intervals.html).

---
## 6. References
1. Kundur, P. _Power System Stability and Control_, McGraw-Hill, 1994.  
2. Van Cutsem, T., & Vournas, C. _Voltage Stability of Electric Power Systems_, Kluwer, 1998.  
3. Milano, F. "Continuation Power Flow," IEEE PES GM Tutorial, 2013.  
4. **University of Washington CEI**. "Simulating the Impact of PV Generation on Power System Voltage," 2020. [Online](https://www.cei.washington.edu/lesson-plans-resources/simulating-the-impact-of-pv-generation-on-power-system-voltage/).  
5. **NREL SAM Forum**. "Modeling / Graphing Load Data vs PV Output Data on 15 min Intervals," 2024. [Online](https://sam.nrel.gov/forum/forum-general/3795-modeling-graphing-load-data-vs-pv-output-data-on-15-min-intervals.html).  
6. pandapower documentation: https://pandapower.readthedocs.io  

_Last updated: June 2025_
