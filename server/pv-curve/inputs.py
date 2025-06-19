'''
PV Curve Input Collection and Validation Module

This module handles all user input collection and validation for generating Power-Voltage (PV) curves
in power system voltage stability analysis. It provides comprehensive parameter collection with
educational descriptions and robust validation to ensure valid inputs for PV curve generation.

Functions:
    - validate_*_input(): Various validation functions for different input types
    - collect_pv_curve_inputs(): Main function to collect all required PV curve parameters

Author: Matthew Cannavaro, Clemson University
'''

def validate_integer_input(prompt, example, min_val=None, max_val=None):
    """
    Validate integer input with re-prompting until valid input is received
    
    Args:
        prompt (str): Input prompt to display to user
        example (str): Example of valid input to show on error
        min_val (int): Minimum allowed value (optional)
        max_val (int): Maximum allowed value (optional)
        
    Returns:
        int: Validated integer input
    """
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                raise ValueError("Input cannot be empty")
            result = int(value)
            if min_val is not None and result < min_val:
                raise ValueError(f"Value must be >= {min_val}")
            if max_val is not None and result > max_val:
                raise ValueError(f"Value must be <= {max_val}")
            return result
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
            print(f"   Example: {example}")
            print("   Please try again.\n")

def validate_float_input(prompt, example, min_val=None, max_val=None, allow_empty=False, default=None):
    """
    Validate float input with re-prompting until valid input is received
    
    Args:
        prompt (str): Input prompt to display to user
        example (str): Example of valid input to show on error
        min_val (float): Minimum allowed value (optional)
        max_val (float): Maximum allowed value (optional)
        allow_empty (bool): Whether empty input is allowed
        default (float): Default value to use if empty input allowed
        
    Returns:
        float or None: Validated float input or None if empty and allowed
    """
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                if allow_empty and default is not None:
                    return default
                elif allow_empty:
                    return None
                else:
                    raise ValueError("Input cannot be empty")
            result = float(value)
            if min_val is not None and result < min_val:
                raise ValueError(f"Value must be >= {min_val}")
            if max_val is not None and result > max_val:
                raise ValueError(f"Value must be <= {max_val}")
            return result
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
            print(f"   Example: {example}")
            print("   Please try again.\n")

def validate_bus_list_input(prompt, example):
    """
    Validate comma-separated bus numbers for power system analysis
    
    Bus numbers must be non-negative integers representing electrical connection points
    in the power system network.
    
    Args:
        prompt (str): Input prompt to display to user
        example (str): Example of valid input format
        
    Returns:
        list[int]: List of validated bus numbers
    """
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                raise ValueError("Input cannot be empty")
            
            # Parse comma-separated values
            bus_list = []
            for bus_str in value.split(','):
                bus_num = int(bus_str.strip())
                if bus_num < 0:
                    raise ValueError("Bus numbers must be non-negative")
                bus_list.append(bus_num)
            
            if len(bus_list) == 0:
                raise ValueError("Must specify at least one bus")
            
            return bus_list
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
            print(f"   Example: {example}")
            print("   Please try again.\n")

def validate_choice_input(prompt, valid_choices, example, allow_empty=False, default=None):
    """
    Validate input against a predefined list of valid choices
    
    Args:
        prompt (str): Input prompt to display to user
        valid_choices (list[str]): List of acceptable input values
        example (str): Example of valid input
        allow_empty (bool): Whether empty input is allowed
        default (str): Default value to use if empty input allowed
        
    Returns:
        str: Validated choice from valid_choices list
    """
    while True:
        value = input(prompt).strip().lower()
        if not value:
            if allow_empty and default is not None:
                return default
            elif allow_empty:
                return ""
            else:
                print(f"❌ Input cannot be empty")
                print(f"   Valid choices: {', '.join(valid_choices)}")
                print(f"   Example: {example}")
                print("   Please try again.\n")
                continue
        
        if value in valid_choices:
            return value
        else:
            print(f"❌ Invalid choice: '{value}'")
            print(f"   Valid choices: {', '.join(valid_choices)}")
            print(f"   Example: {example}")
            print("   Please try again.\n")

def validate_contingency_input(prompt, example):
    """
    Validate contingency format for transmission line outage analysis
    
    Contingencies represent equipment failures (like transmission line outages) that are
    simulated during PV curve analysis to find critical operating conditions.
    
    Format: "bus1_bus2" where bus1 and bus2 are the endpoints of a transmission line
    
    Args:
        prompt (str): Input prompt to display to user
        example (str): Example of valid contingency format
        
    Returns:
        str or None: Validated contingency string or None if empty (allowed)
    """
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                return None  # Empty is allowed for contingencies
            
            if '_' not in value:
                raise ValueError("Contingency must be in format 'bus1_bus2'")
            
            parts = value.split('_')
            if len(parts) != 2:
                raise ValueError("Contingency must have exactly two bus numbers separated by '_'")
            
            # Validate both parts are integers
            bus1, bus2 = int(parts[0]), int(parts[1])
            if bus1 < 0 or bus2 < 0:
                raise ValueError("Bus numbers must be non-negative")
            if bus1 == bus2:
                raise ValueError("Source and destination buses must be different")
            
            return value
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
            print(f"   Example: {example}")
            print("   Please try again.\n")

def collect_pv_curve_inputs():
    """
    Collect all required inputs for PV curve generation with comprehensive validation
    
    This function guides users through entering all parameters needed for power system
    voltage stability analysis and PV curve generation. Each parameter includes detailed
    explanations to help users understand the engineering significance.
    
    Returns:
        dict: Comprehensive dictionary containing all validated PV curve parameters:
            - system_config: Grid model, base power, frequency
            - transfer_config: Source/sink buses, monitoring location
            - step_config: Power step sizes and limits
            - load_config: Load model characteristics  
            - contingency_config: Equipment failure scenarios
            - generator_config: Generator operating limits
            - tolerance_config: Numerical convergence settings
    """
    print("=== PV Curve Generation - Input Collection ===\n")
    print("This tool will guide you through collecting all parameters needed for")
    print("Power-Voltage (PV) curve generation and voltage stability analysis.\n")
    
    # Required Inputs
    print("REQUIRED INPUTS:")
    
    # Power system model - Defines the electrical grid topology and number of buses (connection points)
    # Common IEEE test systems like IEEE 39-bus represent standard power grid configurations
    # used for research and testing. Larger numbers mean more complex grids.
    print("\n1. Power System Model:")
    print("   The power system model defines the electrical grid topology and complexity.")
    print("   IEEE test systems are standard networks used for research and validation.")
    print("   - IEEE 14: Small transmission system (good for learning)")
    print("   - IEEE 39: New England system (medium complexity)")
    print("   - IEEE 118: Large transmission system (high complexity)")
    print("   - Custom: User-defined simple network")
    while True:
        grid_size = input("   Enter power grid model (e.g., IEEE 39, IEEE 118, Custom): ").strip()
        if grid_size:
            break
        else:
            print("❌ Grid model cannot be empty")
            print("   Example: IEEE 39")
            print("   Please try again.\n")
    
    # Source and sink configuration - Source buses inject power (like generators), sink buses consume it (like loads)
    # The PV curve shows how voltage changes as we transfer more power from sources to sinks
    # Multiple buses can be specified to represent generator groups or load areas
    print("\n2. Power Transfer Configuration:")
    print("   Power transfer analysis simulates increasing power flow from generation")
    print("   areas (source buses) to load areas (sink buses). This creates stress on")
    print("   the transmission system that eventually leads to voltage instability.")
    print("   - Source buses: Where additional power generation is added")
    print("   - Sink buses: Where additional load demand is added")
    print("   - Multiple buses can represent generation/load zones")
    
    # Where you're adding more power generation
    source_buses = validate_bus_list_input(
        "   Enter source bus number(s) (comma-separated if multiple): ",
        "1,2 or 5"
    )
    # Where you're adding more load demand
    sink_buses = validate_bus_list_input(
        "   Enter sink/load bus number(s) (comma-separated if multiple): ",
        "3,4 or 8"
    )
    
    # Monitoring bus - This is the specific location where we track voltage changes
    # As power transfer increases, voltage at this bus will drop, creating the PV curve
    # Usually chosen as a critical load bus or the weakest point in the system
    print("\n3. Voltage Monitoring:")
    print("   The monitoring bus is where voltage changes are tracked during the analysis.")
    print("   This location should be chosen as a critical point in the system, typically:")
    print("   - A major load center")
    print("   - The weakest bus in the network")
    print("   - A bus that represents system-wide voltage behavior")
    
    # Where you're watching voltage changes
    monitor_bus = validate_integer_input(
        "   Enter bus number to monitor voltage: ",
        "6", min_val=0
    )
    
    # Step size parameters - Control how power transfer is gradually increased during analysis
    # Initial step: how much power (MW) to add each iteration
    # Minimum step: smallest increment before stopping (determines accuracy)
    # Reduction factor: how much to reduce step size when convergence fails
    print("\n4. Step Size Configuration:")
    print("   Step size parameters control how power transfer is gradually increased.")
    print("   - Initial step: Starting power increment (larger = faster but less accurate)")
    print("   - Minimum step: Smallest increment before stopping (smaller = more accurate)")
    print("   - Reduction factor: How much to reduce step when power flow fails to converge")
    print("   Recommended: Start with 100 MW, reduce to 10 MW minimum, factor of 2")
    
    initial_step = validate_float_input(
        "   Enter initial step size (MW) [default: 100]: ",
        "100", min_val=0.1, allow_empty=True, default=100.0
    )
    min_step = validate_float_input(
        "   Enter minimum step size (MW) [default: 10]: ",
        "10", min_val=0.01, allow_empty=True, default=10.0
    )
    step_reduction_factor = validate_float_input(
        "   Enter step reduction factor when convergence fails [default: 2]: ",
        "2", min_val=1.1, allow_empty=True, default=2.0
    )
    
    # Transfer limits - Maximum power transfer to prevent analysis from running indefinitely
    # Useful when you know the approximate limit or want to focus on a specific range
    # Leave blank to find the natural voltage collapse point
    print("\n5. Transfer Limits:")
    print("   Maximum transfer limit prevents the analysis from running indefinitely.")
    print("   - Leave blank to find the natural voltage collapse point")
    print("   - Set a limit if you know the approximate stability margin")
    print("   - Useful for focusing analysis on a specific power transfer range")
    
    max_transfer = validate_float_input(
        "   Enter maximum transfer limit (MW) [optional, press Enter to skip]: ",
        "500", min_val=0, allow_empty=True
    )
    
    # Optional Inputs
    print("\nOPTIONAL INPUTS:")
    
    # Load model - Defines how electrical loads (like motors, lights) respond to voltage changes
    # Constant power: load power stays same regardless of voltage (most conservative for stability)
    # Constant current: load current stays same (moderate voltage dependency)
    # Constant impedance: load impedance stays same (highest voltage dependency)
    # Voltage exponent: 0=constant power, 1=constant current, 2=constant impedance
    print("\n6. Load Model Configuration:")
    print("   Load model defines how electrical loads respond to voltage changes:")
    print("   - Constant power: Power consumption stays constant (most conservative)")
    print("   - Constant current: Current consumption stays constant (moderate)")
    print("   - Constant impedance: Load impedance stays constant (least conservative)")
    print("   Most power system studies use constant power loads as the default.")
    
    load_model = validate_choice_input(
        "   Enter load model type (constant_power, constant_current, constant_impedance) [default: constant_power]: ",
        ["constant_power", "constant_current", "constant_impedance"],
        "constant_power", allow_empty=True, default="constant_power"
    )
    voltage_exponent = validate_float_input(
        "   Enter voltage exponent for load model [default: 0]: ",
        "0", min_val=0, max_val=2, allow_empty=True, default=0.0
    )
    
    # Contingency analysis - Simulates equipment failures like transmission line outages
    # Important for finding the most critical operating conditions that could cause voltage collapse
    # Contingencies test "what if" scenarios: what happens if this transmission line fails?
    print("\n7. Contingency Analysis:")
    print("   Contingency analysis simulates equipment failures during PV curve generation.")
    print("   This is critical for finding the most limiting operating conditions:")
    print("   - Tests 'what if' scenarios (e.g., transmission line failures)")
    print("   - Identifies critical equipment for system stability")
    print("   - Format: 'bus1_bus2' for line from bus1 to bus2")
    print("   - Example: '1_2' represents outage of line connecting buses 1 and 2")
    
    include_contingencies = validate_choice_input(
        "   Include contingency analysis? (y/n) [default: n]: ",
        ["y", "yes", "n", "no"],
        "n", allow_empty=True, default="n"
    )
    contingencies = []
    if include_contingencies in ['y', 'yes']:
        print("   Enter contingencies (format: line_from_to, e.g., 1_2 for line from bus 1 to bus 2):")
        print("   Press Enter with no input when finished adding contingencies.")
        while True:
            contingency = validate_contingency_input(
                "   Contingency (press Enter when done): ",
                "1_2"
            )
            if not contingency:
                break
            contingencies.append(contingency)
    
    # Critical scenarios - Determines how many different failure conditions to analyze
    # More scenarios = more comprehensive analysis but longer computation time
    # Base case completion ensures we find the limit even without equipment failures
    print("\n8. Analysis Options:")
    print("   Analysis options control the scope and depth of the stability study:")
    print("   - Critical scenarios: How many different failure conditions to analyze")
    print("   - Base case completion: Ensures voltage collapse point is found without failures")
    print("   - More scenarios = more comprehensive but slower analysis")
    
    # Need to handle this differently since validate_integer_input doesn't support defaults
    while True:
        try:
            temp_input = input("   Number of critical scenarios to find [default: 5]: ").strip()
            if not temp_input:
                critical_scenarios = 5
                break
            critical_scenarios = int(temp_input)
            if critical_scenarios < 1 or critical_scenarios > 20:
                raise ValueError("Number must be between 1 and 20")
            break
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
            print("   Example: 5")
            print("   Please try again.\n")
    
    run_base_to_completion = validate_choice_input(
        "   Run base case to completion? (y/n) [default: y]: ",
        ["y", "yes", "n", "no"],
        "y", allow_empty=True, default="y"
    ) in ['y', 'yes']
    
    # Generator limits - Real generators have limits on how much reactive power they can provide
    # Reactive power is needed to maintain voltage; when generators hit limits, voltage drops faster
    # Including limits makes the analysis more realistic but may reduce the apparent stability margin
    print("\n9. Generator Configuration:")
    print("   Generator configuration determines how realistic generator limits are modeled:")
    print("   - Reactive power limits: Real generators can't provide unlimited reactive power")
    print("   - When limits are reached, voltage support decreases rapidly")
    print("   - Including limits makes analysis more realistic but may reduce stability margins")
    print("   - Recommended: Include limits for realistic analysis")
    
    consider_gen_limits = validate_choice_input(
        "   Consider generator reactive power limits? (y/n) [default: y]: ",
        ["y", "yes", "n", "no"],
        "y", allow_empty=True, default="y"
    ) in ['y', 'yes']
    
    # Tolerance settings - Control the numerical accuracy of power flow calculations
    # MVA tolerance: how close power balance must be (smaller = more accurate)
    # AGC tolerance: automatic generation control precision (prevents generator hunting)
    # Tighter tolerances give more accurate results but may slow down computation
    print("\n10. Tolerance Settings:")
    print("   Tolerance settings control the numerical accuracy of power flow calculations:")
    print("   - MVA tolerance: How close power balance must be (smaller = more accurate)")
    print("   - AGC tolerance: Generator control precision (prevents oscillations)")
    print("   - Tighter tolerances = more accurate but slower computation")
    print("   - Default values are suitable for most analyses")
    
    mva_tolerance = validate_float_input(
        "   MVA convergence tolerance [default: 1.0]: ",
        "1.0", min_val=0.001, max_val=10.0, allow_empty=True, default=1.0
    )
    agc_tolerance = validate_float_input(
        "   Island-based AGC tolerance [default: 5.0]: ",
        "5.0", min_val=0.1, max_val=50.0, allow_empty=True, default=5.0
    )
    
    # System parameters - Basic electrical characteristics of the power system
    # Base MVA: reference power level for per-unit calculations (typically 100 MVA)
    # Nominal frequency: standard operating frequency (60 Hz in North America, 50 Hz elsewhere)
    # These are used for normalizing and scaling the analysis results
    print("\n11. System Parameters:")
    print("   System parameters define basic electrical characteristics:")
    print("   - Base MVA: Reference power level for per-unit calculations")
    print("   - Nominal frequency: Standard operating frequency")
    print("   - North America: 60 Hz, Europe/Asia: 50 Hz")
    print("   - These parameters normalize and scale analysis results")
    
    base_mva = validate_float_input(
        "   System base MVA [default: 100]: ",
        "100", min_val=1.0, max_val=10000.0, allow_empty=True, default=100.0
    )
    nominal_frequency = validate_float_input(
        "   Nominal frequency (Hz) [default: 60]: ",
        "60", min_val=40.0, max_val=100.0, allow_empty=True, default=60.0
    )
    
    # Compile all inputs into structured dictionary
    inputs = {
        'system_config': {
            'grid_model': grid_size,
            'base_mva': base_mva,
            'nominal_frequency': nominal_frequency
        },
        'transfer_config': {
            'source_buses': source_buses,
            'sink_buses': sink_buses,
            'monitor_bus': monitor_bus
        },
        'step_config': {
            'initial_step_mw': initial_step,
            'minimum_step_mw': min_step,
            'step_reduction_factor': step_reduction_factor,
            'max_transfer_mw': max_transfer
        },
        'load_config': {
            'load_model': load_model,
            'voltage_exponent': voltage_exponent
        },
        'contingency_config': {
            'include_contingencies': include_contingencies in ['y', 'yes'],
            'contingencies': contingencies,
            'critical_scenarios': critical_scenarios,
            'run_base_to_completion': run_base_to_completion
        },
        'generator_config': {
            'consider_limits': consider_gen_limits
        },
        'tolerance_config': {
            'mva_convergence_tolerance': mva_tolerance,
            'agc_tolerance': agc_tolerance
        }
    }
    
    print("\n=== Input Collection Complete ===")
    print(f"Collected inputs for {grid_size} system")
    print(f"Transfer from bus(es) {source_buses} to {sink_buses}")
    print(f"Monitoring voltage at bus {monitor_bus}")
    print(f"Step size: {initial_step} MW (min: {min_step} MW)")
    
    return inputs

# Documentation for PV Curve Parameter Meanings
PV_CURVE_PARAMETER_GUIDE = """
=== PV CURVE PARAMETER GUIDE ===

This guide explains what each parameter means for PV curve generation:

SYSTEM CONFIGURATION:
- grid_model: Defines the power system network topology and complexity
- base_mva: Reference power level for per-unit system calculations  
- nominal_frequency: Standard operating frequency of the power system

TRANSFER CONFIGURATION:
- source_buses: Locations where additional generation is added during analysis
- sink_buses: Locations where additional load is added during analysis
- monitor_bus: Critical bus where voltage changes are tracked

STEP CONFIGURATION:
- initial_step_mw: Starting power increment for each iteration
- minimum_step_mw: Smallest power increment before stopping analysis
- step_reduction_factor: Factor to reduce step size when convergence fails
- max_transfer_mw: Maximum power transfer limit (optional)

LOAD CONFIGURATION:
- load_model: How loads respond to voltage changes (power/current/impedance)
- voltage_exponent: Mathematical representation of load voltage dependency

CONTINGENCY CONFIGURATION:
- include_contingencies: Whether to simulate equipment failures
- contingencies: List of transmission line outages to simulate
- critical_scenarios: Number of critical failure conditions to analyze
- run_base_to_completion: Whether to find base case voltage collapse point

GENERATOR CONFIGURATION:
- consider_limits: Whether to include realistic generator reactive power limits

TOLERANCE CONFIGURATION:
- mva_convergence_tolerance: Power flow numerical convergence criteria
- agc_tolerance: Automatic generation control precision settings

WHAT IS A PV CURVE?
A PV (Power-Voltage) curve shows the relationship between power transfer and 
voltage magnitude at a critical bus in the power system. As power transfer 
increases, voltage initially decreases slowly, then more rapidly approaching 
the "nose point" - the maximum transferable power before voltage collapse.

The curve has two operating points for each power level (except at the nose):
- Upper portion: Stable operating region (normal operation)
- Lower portion: Unstable operating region (voltage collapse risk)

PV curves are essential for:
- Determining voltage stability margins
- Identifying critical operating conditions  
- Planning reactive power support
- Setting operating limits for system security
"""

if __name__ == "__main__":
    # Demo of input collection
    print("PV Curve Input Collection Demo")
    print("=" * 50)
    
    # Collect inputs
    inputs = collect_pv_curve_inputs()
    
    # Display parameter guide
    print(PV_CURVE_PARAMETER_GUIDE)
    
    # Show collected inputs summary
    print("\n=== COLLECTED INPUTS SUMMARY ===")
    for category, params in inputs.items():
        print(f"\n{category.upper()}:")
        for param, value in params.items():
            print(f"  {param}: {value}")