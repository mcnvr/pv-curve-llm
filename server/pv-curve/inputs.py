"""
===== PV-CURVE ANALYSIS INPUT PARAMETERS =====
REQUIRED:
- Grid Model
- Base MVA  
- Frequency
- Source Buses
- Sink Buses
- Monitor Bus
- Initial Step
- Min Step
- Step Reduction
OPTIONAL:
- Max Transfer
- Load Model
- Voltage Exponent
- Include Contingencies
- Contingencies
- Critical Scenarios
- Run Base Completion
- Generator Limits
- MVA Tolerance
- AGC Tolerance
"""

def collect_simple_pv_inputs():
    """Simple PV curve input collection - minimal validation"""
    
    print("=== Simple PV Curve Input Collection ===\n")
    print("Required Parameters:\n")
    
    # ===== REQUIRED INPUTS =====
    
    # This specifies the name or identifier of the electrical power system network being analyzed.
    # In PV-curve analysis, the grid model determines the network topology, impedances, and generation/load distribution that affect voltage stability limits.
    grid_model = input("Grid model (e.g., IEEE 39): ")
    
    # This is the reference power value (in MVA) used to normalize all power quantities in the system.
    # For PV-curves, the base MVA ensures consistent per-unit calculations when determining maximum power transfer limits before voltage collapse.
    base_mva = float(input("Base MVA (default 100): ") or "100")
    
    # This is the nominal operating frequency of the electrical power system in Hertz.
    # In PV-curve analysis, frequency affects line impedances and reactive power characteristics that influence the voltage stability margin.
    frequency = float(input("Frequency Hz (default 60): ") or "60")
    
    # These are the bus numbers where generators will increase their power output during the analysis.
    # In PV-curves, source buses represent the origin points of increasing power transfer that drives the system toward voltage instability.
    source_buses = [int(x.strip()) for x in input("Source bus numbers (comma-separated): ").split(',')]
    
    # These are the bus numbers where load will be increased to absorb the additional power being transferred.
    # For PV-curve construction, sink buses represent the destination points that create the power transfer stress leading to voltage collapse.
    sink_buses = [int(x.strip()) for x in input("Sink bus numbers (comma-separated): ").split(',')]
    
    # This is the specific bus number where voltage magnitude will be monitored and plotted.
    # In PV-curves, the monitor bus voltage is plotted against power transfer to identify the critical point where voltage collapse occurs.
    monitor_bus = int(input("Monitor bus number: "))
    
    # This is the initial increment of power (in MW) added at each step of the analysis.
    # For PV-curve generation, the initial step size determines how quickly the analysis progresses toward the voltage stability limit.
    initial_step = float(input("Initial step size MW (default 100): ") or "100")
    
    # This is the smallest allowable power increment (in MW) that can be used in the final steps.
    # In PV-curves, the minimum step ensures precise detection of the exact power level where voltage collapse occurs.
    min_step = float(input("Minimum step size MW (default 10): ") or "10")
    
    # This is the factor by which the step size is reduced when approaching convergence difficulties.
    # For PV-curve analysis, step reduction allows accurate identification of the nose point where voltage stability is lost.
    step_reduction = float(input("Step reduction factor (default 2): ") or "2")
    
    print("\nOptional Parameters:\n")
    
    # ===== OPTIONAL INPUTS =====
    
    # This sets an upper bound on the total power transfer (in MW) that will be attempted.
    # In PV-curves, max transfer prevents excessive computation time and can represent known thermal or stability constraints.
    max_transfer = input("Max transfer MW (optional): ")
    max_transfer = float(max_transfer) if max_transfer else None
    
    # This defines how electrical loads change their power consumption in response to voltage variations.
    # For PV-curves, the load model significantly affects the shape and critical point since different load types respond differently to voltage drops.
    load_model = input("Load model (constant_power/constant_current/constant_impedance, default constant_power): ") or "constant_power"
    
    # This is the mathematical exponent that quantifies how much load power varies with voltage changes.
    # In PV-curve analysis, voltage exponent determines load sensitivity and directly impacts the voltage stability margin and collapse point.
    voltage_exp = float(input("Voltage exponent (default 0): ") or "0")
    
    # This enables the simulation of equipment failures or outages during the voltage stability analysis.
    # For PV-curves, contingency analysis reveals how transmission line or generator outages can reduce voltage stability margins.
    include_cont = input("Include contingencies? (y/n, default n): ").lower() or "n"
    
    # These are specific equipment outages (lines, transformers, generators) to simulate during analysis.
    # In PV-curves, each contingency creates a separate curve showing how equipment failures affect maximum power transfer capability.
    contingencies = []
    if include_cont in ['y', 'yes']:
        cont_input = input("Contingencies (format: bus1_bus2, comma-separated): ")
        if cont_input:
            contingencies = [x.strip() for x in cont_input.split(',')]
    
    # This specifies how many of the most severe contingency scenarios should be analyzed in detail.
    # For PV-curve studies, critical scenarios focus computational resources on the outages most likely to cause voltage collapse.
    critical_scenarios = int(input("Critical scenarios (default 5): ") or "5")
    
    # This determines whether the normal operating case should be fully analyzed before studying contingencies.
    # In PV-curves, completing the base case establishes the benchmark voltage stability margin for comparison with contingency cases.
    run_base = input("Run base case to completion? (y/n, default y): ").lower() or "y"
    
    # This includes the physical reactive power output limits of generators in the analysis.
    # For PV-curves, generator limits are critical because reactive power shortage is often the primary cause of voltage instability.
    gen_limits = input("Consider generator limits? (y/n, default y): ").lower() or "y"
    
    # This sets the numerical tolerance for power flow convergence during each step of the analysis.
    # In PV-curve generation, tighter MVA tolerance ensures accurate solutions but may slow computation near the stability limit.
    mva_tol = float(input("MVA tolerance (default 1.0): ") or "1.0")
    
    # This defines the tolerance for automatic generation control that maintains system frequency and power balance.
    # For PV-curves, AGC tolerance affects how generators respond to increasing power transfer and can influence the stability margin.
    agc_tol = float(input("AGC tolerance (default 5.0): ") or "5.0")
    
    # Compile inputs
    inputs = {
        'grid_model': grid_model,
        'base_mva': base_mva,
        'frequency': frequency,
        'source_buses': source_buses,
        'sink_buses': sink_buses,
        'monitor_bus': monitor_bus,
        'initial_step': initial_step,
        'min_step': min_step,
        'step_reduction': step_reduction,
        'max_transfer': max_transfer,
        'load_model': load_model,
        'voltage_exponent': voltage_exp,
        'include_contingencies': include_cont in ['y', 'yes'],
        'contingencies': contingencies,
        'critical_scenarios': critical_scenarios,
        'run_base_completion': run_base in ['y', 'yes'],
        'generator_limits': gen_limits in ['y', 'yes'],
        'mva_tolerance': mva_tol,
        'agc_tolerance': agc_tol
    }
    
    return inputs

def print_inputs(inputs):
    """Print all collected inputs"""
    print("\n=== ALL COLLECTED INPUTS ===")
    for key, value in inputs.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    inputs = collect_simple_pv_inputs()
    print_inputs(inputs)
