'''
Get values to generate PV curve for power system voltage stability analysis
'''

def collect_pv_curve_inputs():
    print("=== PV Curve Generation - Input Collection ===\n")
    
    # Required Inputs
    print("REQUIRED INPUTS:")
    
    # Power system model - Defines the electrical grid topology and number of buses (connection points)
    # Common IEEE test systems like IEEE 39-bus represent standard power grid configurations
    # used for research and testing. Larger numbers mean more complex grids.
    print("\n1. Power System Model:")
    grid_size = input("   Enter power grid model (e.g., IEEE 39, IEEE 118, Custom): ").strip()
    
    # Source and sink configuration - Source buses inject power (like generators), sink buses consume it (like loads)
    # The PV curve shows how voltage changes as we transfer more power from sources to sinks
    # Multiple buses can be specified to represent generator groups or load areas
    print("\n2. Power Transfer Configuration:")
    # Where you're adding more power generation
    source_bus = input("   Enter source bus number(s) (comma-separated if multiple): ").strip()
    # Where you're adding more load demand
    sink_bus = input("   Enter sink/load bus number(s) (comma-separated if multiple): ").strip()
    
    # Monitoring bus - This is the specific location where we track voltage changes
    # As power transfer increases, voltage at this bus will drop, creating the PV curve
    # Usually chosen as a critical load bus or the weakest point in the system
    print("\n3. Voltage Monitoring:")
    # Where you're watching voltage changes
    monitor_bus = input("   Enter bus number to monitor voltage: ").strip()
    
    # Step size parameters - Control how power transfer is gradually increased during analysis
    # Initial step: how much power (MW) to add each iteration
    # Minimum step: smallest increment before stopping (determines accuracy)
    # Reduction factor: how much to reduce step size when convergence fails
    print("\n4. Step Size Configuration:")
    initial_step = float(input("   Enter initial step size (MW) [default: 100]: ") or "100")
    min_step = float(input("   Enter minimum step size (MW) [default: 10]: ") or "10")
    step_reduction_factor = float(input("   Enter step reduction factor when convergence fails [default: 2]: ") or "2")
    
    # Transfer limits - Maximum power transfer to prevent analysis from running indefinitely
    # Useful when you know the approximate limit or want to focus on a specific range
    # Leave blank to find the natural voltage collapse point
    print("\n5. Transfer Limits:")
    max_transfer = input("   Enter maximum transfer limit (MW) [optional, press Enter to skip]: ").strip()
    max_transfer = float(max_transfer) if max_transfer else None
    
    # Optional Inputs
    print("\nOPTIONAL INPUTS:")
    
    # Load model - Defines how electrical loads (like motors, lights) respond to voltage changes
    # Constant power: load power stays same regardless of voltage (most conservative for stability)
    # Constant current: load current stays same (moderate voltage dependency)
    # Constant impedance: load impedance stays same (highest voltage dependency)
    # Voltage exponent: 0=constant power, 1=constant current, 2=constant impedance
    print("\n6. Load Model Configuration:")
    load_model = input("   Enter load model type (constant_power, constant_current, constant_impedance) [default: constant_power]: ").strip() or "constant_power"
    voltage_exponent = float(input("   Enter voltage exponent for load model [default: 0]: ") or "0")
    
    # Contingency analysis - Simulates equipment failures like transmission line outages
    # Important for finding the most critical operating conditions that could cause voltage collapse
    # Contingencies test "what if" scenarios: what happens if this transmission line fails?
    print("\n7. Contingency Analysis:")
    include_contingencies = input("   Include contingency analysis? (y/n) [default: n]: ").strip().lower()
    contingencies = []
    if include_contingencies in ['y', 'yes']:
        print("   Enter contingencies (format: line_from_to, e.g., 1_2 for line from bus 1 to bus 2):")
        while True:
            contingency = input("   Contingency (press Enter when done): ").strip()
            if not contingency:
                break
            contingencies.append(contingency)
    
    # Critical scenarios - Determines how many different failure conditions to analyze
    # More scenarios = more comprehensive analysis but longer computation time
    # Base case completion ensures we find the limit even without equipment failures
    print("\n8. Analysis Options:")
    critical_scenarios = int(input("   Number of critical scenarios to find [default: 5]: ") or "5")
    run_base_to_completion = input("   Run base case to completion? (y/n) [default: y]: ").strip().lower() != 'n'
    
    # Generator limits - Real generators have limits on how much reactive power they can provide
    # Reactive power is needed to maintain voltage; when generators hit limits, voltage drops faster
    # Including limits makes the analysis more realistic but may reduce the apparent stability margin
    print("\n9. Generator Configuration:")
    consider_gen_limits = input("   Consider generator reactive power limits? (y/n) [default: y]: ").strip().lower() != 'n'
    
    # Tolerance settings - Control the numerical accuracy of power flow calculations
    # MVA tolerance: how close power balance must be (smaller = more accurate)
    # AGC tolerance: automatic generation control precision (prevents generator hunting)
    # Tighter tolerances give more accurate results but may slow down computation
    print("\n10. Tolerance Settings:")
    mva_tolerance = float(input("   MVA convergence tolerance [default: 1.0]: ") or "1.0")
    agc_tolerance = float(input("   Island-based AGC tolerance [default: 5.0]: ") or "5.0")
    
    # System parameters - Basic electrical characteristics of the power system
    # Base MVA: reference power level for per-unit calculations (typically 100 MVA)
    # Nominal frequency: standard operating frequency (60 Hz in North America, 50 Hz elsewhere)
    # These are used for normalizing and scaling the analysis results
    print("\n11. System Parameters:")
    base_mva = float(input("   System base MVA [default: 100]: ") or "100")
    nominal_frequency = float(input("   Nominal frequency (Hz) [default: 60]: ") or "60")
    
    # Compile all inputs
    inputs = {
        'system_config': {
            'grid_model': grid_size,
            'base_mva': base_mva,
            'nominal_frequency': nominal_frequency
        },
        'transfer_config': {
            'source_buses': [int(x.strip()) for x in source_bus.split(',')],
            'sink_buses': [int(x.strip()) for x in sink_bus.split(',')],
            'monitor_bus': int(monitor_bus)
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
    print(f"Transfer from bus(es) {source_bus} to {sink_bus}")
    print(f"Monitoring voltage at bus {monitor_bus}")
    print(f"Step size: {initial_step} MW (min: {min_step} MW)")
    
    return inputs

def calculate_pv_curve(inputs):
    """
    Calculate PV curve using the collected inputs and power system analysis
    
    Args:
        inputs (dict): Dictionary containing all PV curve parameters
        
    Returns:
        dict: Results containing PV curve data and analysis
    """
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import pandapower as pp
    import os
    from scipy.interpolate import interp1d
    from datetime import datetime
    
    print("\n=== Starting PV Curve Calculation ===")
    
    # Create timestamped results directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results_base_dir = "./results"
    results_dir = os.path.join(results_base_dir, timestamp)
    
    if not os.path.exists(results_base_dir):
        os.makedirs(results_base_dir)
        print(f"Created base results directory: {results_base_dir}")
    
    os.makedirs(results_dir)
    print(f"Created timestamped results directory: {results_dir}")
    
    # Extract configuration
    sys_config = inputs['system_config']
    transfer_config = inputs['transfer_config']
    step_config = inputs['step_config']
    load_config = inputs['load_config']
    gen_config = inputs['generator_config']
    
    # Create power system network based on grid model
    print(f"Creating {sys_config['grid_model']} power system model...")
    
    if "ieee" in sys_config['grid_model'].lower():
        net = create_ieee_network(sys_config['grid_model'])
    else:
        net = create_simple_test_network(sys_config, transfer_config)
    
    print(f"✓ Network created with {len(net.bus)} buses")
    
    # Configure load model
    if load_config['load_model'] != 'constant_power':
        configure_load_model(net, load_config)
    
    # Initialize results storage
    pv_results = {
        'base_case': {'power_mw': [], 'voltage_pu': [], 'converged': []},
        'contingencies': {}
    }
    
    # Get initial power flow solution
    print("Solving initial power flow...")
    try:
        pp.runpp(net, algorithm='nr', max_iteration=50, 
                enforce_q_lims=gen_config['consider_limits'])
        initial_voltage = net.res_bus.vm_pu.loc[transfer_config['monitor_bus']]
        print(f"✓ Initial voltage at bus {transfer_config['monitor_bus']}: {initial_voltage:.4f} pu")
    except Exception as e:
        print(f"❌ Initial power flow failed: {e}")
        return None
    
    # Base case PV curve calculation
    print("\nCalculating base case PV curve...")
    base_results = calculate_single_pv_curve(
        net, transfer_config, step_config, gen_config, "Base Case"
    )
    pv_results['base_case'] = base_results
    
    # Contingency analysis (if enabled)
    if inputs['contingency_config']['include_contingencies']:
        print("\nCalculating contingency PV curves...")
        for i, contingency in enumerate(inputs['contingency_config']['contingencies']):
            print(f"Processing contingency {i+1}/{len(inputs['contingency_config']['contingencies'])}: {contingency}")
            cont_results = calculate_contingency_pv_curve(
                net, contingency, transfer_config, step_config, gen_config
            )
            pv_results['contingencies'][contingency] = cont_results
    
    # Generate plots and save results
    print("\nGenerating plots and saving results...")
    plot_results = generate_pv_plots(pv_results, inputs, results_dir)
    
    # Save numerical results
    save_numerical_results(pv_results, inputs, results_dir)
    
    print("✓ PV curve calculation completed successfully!")
    print(f"Results saved in timestamped directory: {results_dir}")
    print(f"Generation timestamp: {timestamp}")
    
    return pv_results

def create_ieee_network(grid_model):
    """Create IEEE test network based on model name"""
    import pandapower.networks as nw
    
    if "39" in grid_model:
        return nw.case39()
    elif "118" in grid_model:
        return nw.case118()
    elif "300" in grid_model:
        return nw.case300() 
    elif "14" in grid_model:
        return nw.case14()
    else:
        # Default to IEEE 14-bus for unrecognized models
        print(f"Warning: {grid_model} not recognized, using IEEE 14-bus")
        return nw.case14()

def create_simple_test_network(sys_config, transfer_config):
    """Create a simple test network for custom configurations"""
    net = pp.create_empty_network(sn_mva=sys_config['base_mva'])
    
    # Create buses
    buses = []
    for i in range(max(max(transfer_config['source_buses']), 
                      max(transfer_config['sink_buses']), 
                      transfer_config['monitor_bus']) + 1):
        bus = pp.create_bus(net, vn_kv=20.0, name=f"Bus_{i}")
        buses.append(bus)
    
    # Create lines connecting buses
    for i in range(len(buses)-1):
        pp.create_line(net, from_bus=buses[i], to_bus=buses[i+1], 
                      length_km=10, std_type="NAYY 4x50 SE")
    
    # Create external grid at source bus
    for source_bus in transfer_config['source_buses']:
        pp.create_ext_grid(net, bus=source_bus, vm_pu=1.0)
    
    # Create load at sink bus  
    for sink_bus in transfer_config['sink_buses']:
        pp.create_load(net, bus=sink_bus, p_mw=10, q_mvar=5)
    
    return net

def configure_load_model(net, load_config):
    """Configure voltage-dependent load model"""
    if load_config['load_model'] == 'constant_current':
        net.load['const_i_percent'] = 100
        net.load['const_z_percent'] = 0
    elif load_config['load_model'] == 'constant_impedance':
        net.load['const_i_percent'] = 0
        net.load['const_z_percent'] = 100

def calculate_single_pv_curve(net, transfer_config, step_config, gen_config, case_name):
    """Calculate PV curve for a single case (base or contingency)"""
    import pandapower as pp
    import copy
    
    # Make a copy of the network
    net_copy = copy.deepcopy(net)
    
    # Initialize results
    power_mw = []
    voltage_pu = []
    converged = []
    
    current_step = step_config['initial_step_mw']
    total_transfer = 0
    consecutive_failures = 0
    
    print(f"  Starting {case_name} calculation...")
    
    while current_step >= step_config['minimum_step_mw']:
        # Increase load at sink buses
        for sink_bus in transfer_config['sink_buses']:
            load_indices = net_copy.load[net_copy.load.bus == sink_bus].index
            for load_idx in load_indices:
                net_copy.load.at[load_idx, 'p_mw'] += current_step / len(transfer_config['sink_buses'])
        
        total_transfer += current_step
        
        # Check maximum transfer limit
        if (step_config['max_transfer_mw'] is not None and 
            total_transfer > step_config['max_transfer_mw']):
            print(f"  Maximum transfer limit ({step_config['max_transfer_mw']} MW) reached")
            break
        
        try:
            # Run power flow
            pp.runpp(net_copy, algorithm='nr', max_iteration=50,
                    enforce_q_lims=gen_config['consider_limits'],
                    tolerance_mva=1e-6)
            
            # Get voltage at monitoring bus
            monitor_voltage = net_copy.res_bus.vm_pu.loc[transfer_config['monitor_bus']]
            
            # Store results
            power_mw.append(total_transfer)
            voltage_pu.append(monitor_voltage)
            converged.append(True)
            
            print(f"  Transfer: {total_transfer:6.1f} MW, Voltage: {monitor_voltage:.4f} pu ✓")
            
            consecutive_failures = 0
            
            # Check for very low voltage (approaching collapse)
            if monitor_voltage < 0.5:
                print(f"  Very low voltage detected ({monitor_voltage:.4f} pu), stopping calculation")
                break
                
        except Exception as e:
            # Power flow failed - reduce step size
            total_transfer -= current_step  # Revert the failed step
            
            # Revert load changes
            for sink_bus in transfer_config['sink_buses']:
                load_indices = net_copy.load[net_copy.load.bus == sink_bus].index
                for load_idx in load_indices:
                    net_copy.load.at[load_idx, 'p_mw'] -= current_step / len(transfer_config['sink_buses'])
            
            consecutive_failures += 1
            current_step = current_step / step_config['step_reduction_factor']
            
            print(f"  Power flow failed, reducing step to {current_step:.1f} MW")
            
            if consecutive_failures > 5:
                print(f"  Too many consecutive failures, stopping calculation")
                break
    
    # Add continuation beyond nose point using reduced step sizes
    if len(voltage_pu) > 0:
        power_mw, voltage_pu, converged = continue_beyond_nose_point(
            net_copy, transfer_config, power_mw, voltage_pu, converged, 
            step_config, gen_config
        )
    
    print(f"  {case_name} completed: {len(power_mw)} points calculated")
    
    return {
        'power_mw': power_mw,
        'voltage_pu': voltage_pu, 
        'converged': converged
    }

def continue_beyond_nose_point(net, transfer_config, power_mw, voltage_pu, converged, 
                              step_config, gen_config):
    """Continue calculation beyond the nose point to complete PV curve"""
    import pandapower as pp
    
    if len(voltage_pu) < 2:
        return power_mw, voltage_pu, converged
    
    # Find approximate nose point (minimum voltage gradient)
    voltage_gradients = [abs(voltage_pu[i] - voltage_pu[i-1]) for i in range(1, len(voltage_pu))]
    
    if len(voltage_gradients) < 3:
        return power_mw, voltage_pu, converged
    
    # Use very small steps beyond the apparent nose point
    small_step = step_config['minimum_step_mw'] / 2
    total_transfer = power_mw[-1]
    continuation_points = 0
    max_continuation_points = 10
    
    print(f"  Continuing beyond nose point with {small_step:.1f} MW steps...")
    
    while continuation_points < max_continuation_points:
        # Increase load with small step
        for sink_bus in transfer_config['sink_buses']:
            load_indices = net.load[net.load.bus == sink_bus].index
            for load_idx in load_indices:
                net.load.at[load_idx, 'p_mw'] += small_step / len(transfer_config['sink_buses'])
        
        total_transfer += small_step
        
        try:
            # Try power flow with relaxed convergence
            pp.runpp(net, algorithm='nr', max_iteration=100,
                    enforce_q_lims=gen_config['consider_limits'],
                    tolerance_mva=1e-5)
            
            monitor_voltage = net.res_bus.vm_pu.loc[transfer_config['monitor_bus']]
            
            power_mw.append(total_transfer)
            voltage_pu.append(monitor_voltage)
            converged.append(True)
            
            continuation_points += 1
            
            print(f"  Continuation {continuation_points}: {total_transfer:6.1f} MW, {monitor_voltage:.4f} pu ✓")
            
            # Stop if voltage drops too low
            if monitor_voltage < 0.3:
                break
                
        except Exception:
            # Failed to converge - try to continue with even smaller steps  
            small_step = small_step / 2
            total_transfer -= small_step * 2  # Revert
            
            # Revert load changes
            for sink_bus in transfer_config['sink_buses']:
                load_indices = net.load[net.load.bus == sink_bus].index
                for load_idx in load_indices:
                    net.load.at[load_idx, 'p_mw'] -= small_step * 2 / len(transfer_config['sink_buses'])
            
            if small_step < 0.1:  # Stop if steps become too small
                break
    
    return power_mw, voltage_pu, converged

def calculate_contingency_pv_curve(net, contingency, transfer_config, step_config, gen_config):
    """Calculate PV curve with a specific contingency applied"""
    import pandapower as pp
    import copy
    
    # Make a copy and apply contingency
    net_cont = copy.deepcopy(net)
    
    # Apply contingency (assume format "bus1_bus2" for line outage)
    if "_" in contingency:
        from_bus, to_bus = map(int, contingency.split("_"))
        
        # Find and disconnect the line
        line_indices = net_cont.line[
            ((net_cont.line.from_bus == from_bus) & (net_cont.line.to_bus == to_bus)) |
            ((net_cont.line.from_bus == to_bus) & (net_cont.line.to_bus == from_bus))
        ].index
        
        if len(line_indices) > 0:
            net_cont.line.loc[line_indices, 'in_service'] = False
            print(f"  Applied contingency: Line {from_bus}-{to_bus} out of service")
        else:
            print(f"  Warning: Line {from_bus}-{to_bus} not found")
    
    # Calculate PV curve for this contingency
    return calculate_single_pv_curve(
        net_cont, transfer_config, step_config, gen_config, f"Contingency {contingency}"
    )

def generate_pv_plots(pv_results, inputs, results_dir):
    """Generate and save PV curve plots"""
    import matplotlib.pyplot as plt
    import os
    
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot base case
    base_data = pv_results['base_case']
    ax.plot(base_data['power_mw'], base_data['voltage_pu'], 
           'b-', linewidth=2, label='Base Case', marker='o', markersize=4)
    
    # Plot contingencies
    colors = ['r', 'g', 'm', 'c', 'orange', 'purple']
    for i, (cont_name, cont_data) in enumerate(pv_results['contingencies'].items()):
        color = colors[i % len(colors)]
        ax.plot(cont_data['power_mw'], cont_data['voltage_pu'],
               color=color, linewidth=2, label=f'Contingency {cont_name}',
               marker='s', markersize=3, linestyle='--')
    
    # Formatting
    ax.set_xlabel('Power Transfer (MW)', fontsize=12)
    ax.set_ylabel('Voltage Magnitude (pu)', fontsize=12) 
    ax.set_title(f'PV Curves - {inputs["system_config"]["grid_model"]} System\n'
                f'Monitor Bus: {inputs["transfer_config"]["monitor_bus"]}', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Add nose point annotations
    if len(base_data['power_mw']) > 0:
        max_power = max(base_data['power_mw'])
        max_power_idx = base_data['power_mw'].index(max_power)
        max_voltage = base_data['voltage_pu'][max_power_idx]
        
        ax.annotate(f'Nose Point\n({max_power:.1f} MW, {max_voltage:.3f} pu)',
                   xy=(max_power, max_voltage), xytext=(max_power*0.7, max_voltage+0.1),
                   arrowprops=dict(arrowstyle='->', color='black', alpha=0.7),
                   fontsize=10, ha='center')
    
    # Save plot
    plot_filename = os.path.join(results_dir, 'pv_curves.png')
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(results_dir, 'pv_curves.pdf'), bbox_inches='tight')
    
    print(f"✓ PV curve plots saved: {plot_filename}")
    
    # Interactive plotly version
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        fig_plotly = go.Figure()
        
        # Base case
        fig_plotly.add_trace(go.Scatter(
            x=base_data['power_mw'], y=base_data['voltage_pu'],
            mode='lines+markers', name='Base Case',
            line=dict(color='blue', width=3)
        ))
        
        # Contingencies
        for i, (cont_name, cont_data) in enumerate(pv_results['contingencies'].items()):
            fig_plotly.add_trace(go.Scatter(
                x=cont_data['power_mw'], y=cont_data['voltage_pu'],
                mode='lines+markers', name=f'Contingency {cont_name}',
                line=dict(dash='dash', width=2)
            ))
        
        fig_plotly.update_layout(
            title=f'Interactive PV Curves - {inputs["system_config"]["grid_model"]} System',
            xaxis_title='Power Transfer (MW)',
            yaxis_title='Voltage Magnitude (pu)',
            hovermode='x unified'
        )
        
        plotly_file = os.path.join(results_dir, 'pv_curves_interactive.html')
        fig_plotly.write_html(plotly_file)
        print(f"✓ Interactive plot saved: {plotly_file}")
        
    except ImportError:
        print("  Plotly not available, skipping interactive plot")
    
    plt.close()

def save_numerical_results(pv_results, inputs, results_dir):
    """Save numerical results to CSV files"""
    import pandas as pd
    import os
    
    # Save base case results
    base_df = pd.DataFrame({
        'Power_MW': pv_results['base_case']['power_mw'],
        'Voltage_pu': pv_results['base_case']['voltage_pu'],
        'Converged': pv_results['base_case']['converged']
    })
    
    base_file = os.path.join(results_dir, 'base_case_results.csv')
    base_df.to_csv(base_file, index=False)
    print(f"✓ Base case results saved: {base_file}")
    
    # Save contingency results
    for cont_name, cont_data in pv_results['contingencies'].items():
        cont_df = pd.DataFrame({
            'Power_MW': cont_data['power_mw'],
            'Voltage_pu': cont_data['voltage_pu'],
            'Converged': cont_data['converged']
        })
        
        cont_file = os.path.join(results_dir, f'contingency_{cont_name}_results.csv')
        cont_df.to_csv(cont_file, index=False)
        print(f"✓ Contingency {cont_name} results saved: {cont_file}")
    
    # Save summary
    summary = {
        'Grid Model': inputs['system_config']['grid_model'],
        'Source Buses': inputs['transfer_config']['source_buses'],
        'Sink Buses': inputs['transfer_config']['sink_buses'],
        'Monitor Bus': inputs['transfer_config']['monitor_bus'],
        'Load Model': inputs['load_config']['load_model'],
        'Initial Step (MW)': inputs['step_config']['initial_step_mw'],
        'Minimum Step (MW)': inputs['step_config']['minimum_step_mw']
    }
    
    if len(pv_results['base_case']['power_mw']) > 0:
        summary['Max Power Transfer (MW)'] = max(pv_results['base_case']['power_mw'])
        min_voltage_idx = pv_results['base_case']['voltage_pu'].index(min(pv_results['base_case']['voltage_pu']))
        summary['Min Voltage (pu)'] = pv_results['base_case']['voltage_pu'][min_voltage_idx]
        summary['Power at Min Voltage (MW)'] = pv_results['base_case']['power_mw'][min_voltage_idx]
    
    summary_df = pd.DataFrame(list(summary.items()), columns=['Parameter', 'Value'])
    summary_file = os.path.join(results_dir, 'analysis_summary.csv')
    summary_df.to_csv(summary_file, index=False)
    print(f"✓ Analysis summary saved: {summary_file}")

if __name__ == "__main__":
    # Collect inputs
    pv_inputs = collect_pv_curve_inputs()
    
    # Calculate PV curves
    if pv_inputs:
        results = calculate_pv_curve(pv_inputs)
        
        if results:
            print("\n=== PV Curve Analysis Complete ===")
            print("Check the ./results/[timestamp] directory for:")
            print("  • pv_curves.png - Main PV curve plot")
            print("  • pv_curves_interactive.html - Interactive plotly visualization")
            print("  • base_case_results.csv - Numerical results")
            print("  • analysis_summary.csv - Summary of analysis parameters")
            print("Each generation creates a new timestamped folder to preserve analysis history.")
        else:
            print("\n❌ PV curve calculation failed. Check your inputs and try again.")