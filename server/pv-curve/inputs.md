# PV-Curve Analysis Input Parameters

This document outlines all necessary input types and associated information required for Power-Voltage (PV) curve analysis in power systems using pandapower and our custom implementation.

## Overview

PV-curve analysis is a critical tool for voltage stability assessment in power systems. It plots the voltage magnitude at a specific bus against the total system load (active power), revealing the **nose point** where voltage collapse occurs.

---

## 1. Network Selection Inputs

### 1.1 IEEE Test Case Networks
**Description:** Standard test networks for power system analysis
**Required:** Yes
**Type:** String (enumerated)

**Available Options:**
- `case14` - IEEE 14-bus system (14 buses, good for quick analysis)
- `case30` - IEEE 30-bus system (30 buses, medium-sized)
- `case39` - IEEE 39-bus system (39 buses, New England system, commonly used for stability studies)
- `case118` - IEEE 118-bus system (118 buses, large system for comprehensive analysis)

**Source:** [Pandapower Networks Documentation](https://pandapower.readthedocs.io/en/develop/about/units.html)

**Default:** `case39`

**Selection Criteria:**
- **Small networks (case14):** Fast computation, educational purposes
- **Medium networks (case30, case39):** Balanced analysis time and complexity
- **Large networks (case118):** Comprehensive analysis, slower computation

---

## 2. Bus Selection Inputs

### 2.1 Monitored Bus Index
**Description:** The specific bus where voltage magnitude is monitored during load scaling
**Required:** Yes
**Type:** Integer
**Range:** 0 to (number_of_buses - 1)

**Selection Guidelines:**
- **Load buses:** Typically most vulnerable to voltage instability
- **Critical buses:** Buses serving important loads
- **Weak buses:** Electrically distant from generation sources
- **Transmission/distribution interface buses**

**Validation:** Must be within the valid bus range for the selected network

**Examples:**
- IEEE 39-bus: Valid range 0-38 (commonly analyze bus 10, 15, 20)
- IEEE 118-bus: Valid range 0-117 (commonly analyze bus 50, 75, 100)

---

## 3. Load Scaling Parameters

### 3.1 Maximum Load Scaling Factor
**Description:** Maximum multiplier for base case loads before terminating analysis
**Required:** Yes
**Type:** Float
**Range:** 1.0 to 5.0 (typical range 1.5 to 2.5)
**Unit:** Per unit (1.0 = 100% of base load)

**Default:** 2.0 (200% of base load)

**Considerations:**
- **Conservative analysis:** 1.5-1.8 (realistic load growth scenarios)
- **Stress testing:** 2.0-2.5 (extreme loading conditions)
- **Academic studies:** Up to 3.0+ (theoretical limits)

### 3.2 Number of Analysis Points
**Description:** Number of load scaling steps between base case and maximum scaling
**Required:** Yes
**Type:** Integer
**Range:** 10 to 100
**Default:** 41

**Trade-offs:**
- **Fewer points (10-20):** Faster analysis, may miss critical details near nose point
- **More points (50-100):** Higher accuracy, slower computation, better nose point resolution

**Recommended Values:**
- Quick analysis: 21 points
- Standard analysis: 41 points
- Detailed analysis: 61-81 points

---

## 4. Analysis Configuration

### 4.1 Plot Generation
**Description:** Whether to generate and return base64-encoded plot
**Required:** No
**Type:** Boolean
**Default:** True

**Options:**
- `True`: Generate plot for visualization (recommended for web applications)
- `False`: Skip plot generation for faster computation (API endpoints)

### 4.2 Load Scaling Distribution
**Description:** How load increases are distributed across the system
**Type:** String (implicit in our implementation)
**Options:**
- `uniform`: All loads scaled by same factor (our current implementation)
- `proportional`: Loads scaled proportionally to base values
- `specific_bus`: Only specific buses scaled (advanced)

---

## 5. Power Flow Solver Parameters

Based on [Pandapower Power Flow Documentation](https://pandapower.readthedocs.io/en/latest/powerflow/ac.html):

### 5.1 Algorithm Selection
**Description:** Power flow solution algorithm
**Type:** String
**Default:** 'nr' (Newton-Raphson)

**Available Algorithms:**
- `nr`: Newton-Raphson (recommended for PV analysis)
- `bfsw`: Backward/Forward Sweep (for radial networks)
- `gs`: Gauss-Seidel (slower convergence)
- `fdbx/fdxb`: Fast-decoupled methods

### 5.2 Convergence Tolerance
**Description:** Power flow convergence criteria
**Type:** Float
**Default:** 1e-8 MVA
**Range:** 1e-6 to 1e-10

### 5.3 Maximum Iterations
**Description:** Maximum power flow iterations before non-convergence
**Type:** Integer
**Default:** 10 (for Newton-Raphson)

---

## 6. Network Configuration Inputs

### 6.1 Base System Parameters
**Description:** Fundamental system parameters from selected IEEE case
**Source:** Automatically loaded from pandapower networks

**Includes:**
- **Bus data:** Voltage levels, bus types
- **Load data:** Active/reactive power demands
- **Generator data:** Generation limits and settings
- **Line data:** Impedances, thermal limits
- **Transformer data:** Ratios, impedances

### 6.2 System Frequency
**Description:** System operating frequency
**Type:** Float
**Default:** 50 Hz (pandapower standard)
**Units:** Hertz

**Note:** Pandapower standard types are designed for 50 Hz systems. For 60 Hz systems, line reactance values may need adjustment.

---

## 7. Output Configuration

### 7.1 Results Format
**Description:** Structure of analysis results
**Type:** Dictionary

**Returned Data:**
- `P_list`: Total system power at each analysis point [MW]
- `V_list`: Monitored bus voltage at each point [p.u.]
- `base_case`: Base case operating point data
- `nose_point`: Voltage collapse point data
- `voltage_margin`: Safety margin calculations
- `plot_base64`: Visualization (if requested)

### 7.2 Error Handling
**Description:** Analysis validation and error reporting
**Includes:**
- Bus index validation
- Network connectivity verification
- Power flow convergence monitoring
- Load scaling feasibility

---

## 8. Advanced Parameters (Optional)

### 8.1 Temperature Considerations
**Description:** Line temperature effects on impedance
**Type:** Boolean
**Default:** False
**Reference:** [TDPF Documentation](https://pandapower.readthedocs.io/en/latest/powerflow/ac.html)

### 8.2 Voltage-Dependent Loads
**Description:** Load characteristics under voltage variations
**Type:** Boolean
**Default:** True
**Impact:** Affects curve shape and collapse point

### 8.3 Generator Reactive Power Limits
**Description:** Enforce generator Q limits during analysis
**Type:** Boolean
**Default:** False
**Impact:** More realistic but may cause earlier convergence failure

---

## 9. Practical Input Guidelines

### 9.1 For Educational/Learning Use
```python
network_case = "case14"
bus_idx = 5
max_scale = 1.8
num_points = 21
```

### 9.2 For Research Analysis
```python
network_case = "case39"
bus_idx = 10
max_scale = 2.0
num_points = 41
```

### 9.3 For Comprehensive Studies
```python
network_case = "case118"
bus_idx = 50
max_scale = 1.6
num_points = 61
```

---

## 10. Input Validation Requirements

### 10.1 Mandatory Checks
1. **Network case exists** in pandapower networks
2. **Bus index is valid** for selected network
3. **Load scaling parameters** are positive and reasonable
4. **Analysis points** sufficient for accurate curve generation

### 10.2 Recommended Checks
1. **Base case power flow** converges successfully
2. **Load data exists** in selected network
3. **Monitored bus** has meaningful voltage variations
4. **System is connected** and properly formed

---

## 11. Performance Considerations

### 11.1 Computation Time Factors
- **Network size:** Larger networks require more time
- **Number of points:** Linear impact on computation time
- **Convergence criteria:** Tighter tolerance increases time
- **Plot generation:** Minimal impact on overall time

### 11.2 Memory Requirements
- **Network storage:** IEEE cases are lightweight
- **Results storage:** Proportional to number of analysis points
- **Plot generation:** Base64 encoding requires additional memory

---

## References

1. [Pandapower Unit System and Conventions](https://pandapower.readthedocs.io/en/develop/about/units.html)
2. [Pandapower Balanced AC Power Flow](https://pandapower.readthedocs.io/en/latest/powerflow/ac.html)
3. [Pandapower Standard Types](https://pandapower.readthedocs.io/en/latest/std_types/basic.html)
4. [Working with Markdown in Python](https://www.honeybadger.io/blog/python-markdown/)
5. Frank et al., "Temperature-dependent power flow", IEEE Transactions on Power Systems, 2013
6. Ngoko et al., "Temperature Dependent Power Flow Model", IEEE Conference, 2019

---

**Last Updated:** January 2025  
**Version:** 1.0  
**Compatible with:** pandapower 3.0+, Python 3.8+ 