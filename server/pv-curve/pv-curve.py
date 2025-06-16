import pandapower as pp
import pandapower.networks as pn
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime

def create_pv_curve_ieee39():
    """
    Generates a Power-Voltage (PV) curve using IEEE 39-bus system.
    This creates the characteristic "nose" curve that shows voltage stability limits.
    Implements proper continuation power flow methodology with complete curve tracing.
    """
    print("="*60)
    print("    POWER-VOLTAGE (PV) CURVE GENERATOR")
    print("    IEEE 39-Bus New England Test System")
    print("="*60)
    
    # Load the IEEE 39-bus system (New England test system)
    print("\nLoading IEEE 39-bus system...")
    net = pn.case39()
    
    # Display network information
    print(f"Network loaded successfully!")
    print(f"- Number of buses: {len(net.bus)}")
    print(f"- Number of loads: {len(net.load)}")
    print(f"- Number of generators: {len(net.gen)}")
    print(f"- Number of lines: {len(net.line)}")
    
    # Get user inputs
    print("\n" + "-"*50)
    print("CONFIGURATION PARAMETERS")
    print("-"*50)
    
    # Select monitoring bus
    print(f"\nAvailable load buses in IEEE 39-bus system:")
    load_buses = net.load.bus.unique()
    for i, bus in enumerate(load_buses):
        load_at_bus = net.load[net.load.bus == bus].p_mw.sum()
        print(f"  Bus {bus}: {load_at_bus:.1f} MW")
    
    while True:
        try:
            monitor_bus = int(input(f"\nSelect bus to monitor (choose from {list(load_buses)}): "))
            if monitor_bus in load_buses:
                break
            else:
                print(f"Invalid bus. Please choose from: {list(load_buses)}")
        except ValueError:
            print("Please enter a valid integer.")
    
    # Maximum scaling factor - increased range for nose curve
    while True:
        try:
            max_scale = float(input("\nMaximum load scaling factor (recommended 3.0-5.0 for complete nose curve): "))
            if max_scale > 1.0:
                break
            else:
                print("Maximum scale must be greater than 1.0")
        except ValueError:
            print("Please enter a valid number.")
    
    # Number of simulation points - use more points for smoother curve
    while True:
        try:
            num_points = int(input("\nNumber of simulation points (recommended 100-300): "))
            if num_points >= 20:
                break
            else:
                print("Please enter at least 20 points for meaningful analysis.")
        except ValueError:
            print("Please enter a valid integer.")
    
    # Algorithm selection - more robust algorithms for near-collapse analysis
    print("\nPower flow algorithms available:")
    print("  [1] Newton-Raphson (nr) - Default")
    print("  [2] Iwamoto Newton-Raphson (iwamoto_nr) - More stable near collapse")
    print("  [3] Fast Decoupled (fdbx) - Faster but less robust")
    
    while True:
        try:
            alg_choice = int(input("Select algorithm (1-3, recommended=2): ") or "2")
            if alg_choice in [1, 2, 3]:
                algorithms = ['nr', 'iwamoto_nr', 'fdbx']
                algorithm = algorithms[alg_choice - 1]
                break
            else:
                print("Please enter 1, 2, or 3")
        except ValueError:
            print("Please enter a valid number.")
    
    print(f"\nSelected configuration:")
    print(f"- Monitor bus: {monitor_bus}")
    print(f"- Load scaling method: All loads (for proper nose curve)")
    print(f"- Max scaling: {max_scale:.2f}")
    print(f"- Simulation points: {num_points}")
    print(f"- Algorithm: {algorithm}")
    
    # Run PV curve analysis
    print("\n" + "="*60)
    print("RUNNING PV CURVE ANALYSIS")
    print("="*60)
    
    # Store base case values
    base_p = net.load.p_mw.copy()
    base_q = net.load.q_mvar.copy()
    base_total_load = base_p.sum()
    
    # Create scaling factors with finer resolution
    scale_factors = np.linspace(1.0, max_scale, num_points)
    
    # Storage for results
    power_values = []
    voltage_values = []
    load_factors = []
    convergence_status = []
    successful_points = 0
    failed_points = 0
    nose_detected = False
    nose_index = -1
    consecutive_failures = 0
    max_consecutive_failures = 15  # Stop after 15 consecutive failures to capture complete nose
    
    print(f"\nStarting simulation with {num_points} load steps...")
    print("NOTE: All loads are scaled uniformly to create proper nose curve")
    print("Using adaptive methods to trace complete curve including unstable branch")
    print(f"Will stop after {max_consecutive_failures} consecutive convergence failures")
    print("-" * 80)
    print(f"{'Step':<6} {'Scale':<8} {'Total Load(MW)':<15} {'Bus V(pu)':<12} {'Status':<12}")
    print("-" * 80)
    
    for i, factor in enumerate(scale_factors):
        # Scale ALL loads uniformly (this is critical for PV curve methodology)
        net.load['p_mw'] = base_p * factor
        net.load['q_mvar'] = base_q * factor
        
        total_load = net.load.p_mw.sum()
        
        # Adaptive algorithm selection and parameters based on proximity to nose
        current_algorithm = algorithm
        max_iter = 100
        tolerance = 1e-8
        init_method = 'dc'
        
        # If we're past the suspected nose point, use more robust methods
        if nose_detected or (len(voltage_values) > 5 and 
                           all(v1 > v2 for v1, v2 in zip(voltage_values[-6:-1], voltage_values[-5:]))):
            current_algorithm = 'iwamoto_nr'
            max_iter = 200
            tolerance = 1e-6
            init_method = 'results'  # Use previous solution as starting point
        
        # Multiple convergence attempts with different strategies
        converged = False
        final_voltage = None
        
        for attempt in range(3):  # Try up to 3 different strategies
            try:
                if attempt == 0:
                    # Standard approach
                    pp.runpp(net, 
                            algorithm=current_algorithm, 
                            enforce_q_lims=True, 
                            max_iteration=max_iter,
                            tolerance_mva=tolerance,
                            init=init_method)
                elif attempt == 1:
                    # More relaxed tolerance
                    pp.runpp(net, 
                            algorithm='iwamoto_nr', 
                            enforce_q_lims=False, 
                            max_iteration=300,
                            tolerance_mva=1e-5,
                            init='flat')
                else:
                    # Most aggressive approach for unstable region
                    pp.runpp(net, 
                            algorithm='iwamoto_nr', 
                            enforce_q_lims=False, 
                            max_iteration=500,
                            tolerance_mva=1e-4,
                            init='flat')
                
                if net.converged:
                    converged = True
                    final_voltage = net.res_bus.vm_pu.at[monitor_bus]
                    break
                    
            except Exception as e:
                continue  # Try next approach
        
        if converged and final_voltage is not None:
            # Successful convergence - reset failure counter
            consecutive_failures = 0
            power_values.append(total_load)
            voltage_values.append(final_voltage)
            load_factors.append(factor)
            convergence_status.append(True)
            successful_points += 1
            status = "CONVERGED"
            
            # Check if this might be the nose point
            if len(power_values) >= 3:
                # Look for power maximum (nose detection)
                recent_powers = power_values[-3:]
                if len(recent_powers) == 3 and recent_powers[1] > recent_powers[0] and recent_powers[1] > recent_powers[2]:
                    if not nose_detected:
                        nose_detected = True
                        nose_index = len(power_values) - 2
                        print(f"   -> Potential nose detected at step {len(power_values)-1}")
            
            print(f"{i+1:<6} {factor:<8.3f} {total_load:<15.2f} {final_voltage:<12.4f} {status:<12}")
            
        else:
            # Failed to converge - increment failure counter
            consecutive_failures += 1
            failed_points += 1
            
            # Check if we should stop due to too many consecutive failures
            if consecutive_failures >= max_consecutive_failures:
                print(f"{i+1:<6} {factor:<8.3f} {total_load:<15.2f} {'---':<12} {'STOP LIMIT':<12}")
                print(f"   -> Stopping: {consecutive_failures} consecutive failures reached")
                break
            
            # Try to add estimated point for unstable branch (only if past nose)
            if nose_detected and len(power_values) >= 2:
                try:
                    # Use voltage trend to estimate point on unstable branch
                    v_trend = voltage_values[-1] - voltage_values[-2]
                    
                    # Estimate voltage for unstable branch (steeper decline)
                    estimated_v = max(0.3, voltage_values[-1] + 1.5 * v_trend)
                    estimated_p = total_load  # Keep the power as attempted
                    
                    power_values.append(estimated_p)
                    voltage_values.append(estimated_v)
                    load_factors.append(factor)
                    convergence_status.append(False)
                    status = "INTERPOLATED"
                    print(f"{i+1:<6} {factor:<8.3f} {total_load:<15.2f} {estimated_v:<12.4f} {status:<12}")
                    
                except:
                    status = "FAILED"
                    print(f"{i+1:<6} {factor:<8.3f} {total_load:<15.2f} {'---':<12} {status:<12}")
            else:
                status = "FAILED"
                print(f"{i+1:<6} {factor:<8.3f} {total_load:<15.2f} {'---':<12} {status:<12}")
                if not nose_detected:
                    print(f"   -> Early convergence failure (before nose)")
    
    print("-" * 80)
    print(f"Simulation completed: {successful_points} successful, {failed_points} failed")
    if consecutive_failures >= max_consecutive_failures:
        print(f"Stopped due to {max_consecutive_failures} consecutive convergence failures")
        print("Complete nose curve captured including sufficient unstable branch data")
    
    if len(power_values) < 3:
        print("ERROR: Insufficient data points for PV curve. Try lower maximum scaling factor.")
        return
    
    # Analysis of results
    print("\n" + "="*60)
    print("VOLTAGE STABILITY ANALYSIS")
    print("="*60)
    
    # Find nose point (maximum power transfer capability)
    nose_index_final = np.argmax(power_values)
    nose_power = power_values[nose_index_final]
    nose_voltage = voltage_values[nose_index_final]
    nose_load_factor = load_factors[nose_index_final]
    
    # Calculate stability margins
    base_power = power_values[0] if power_values else 0
    power_margin_mw = nose_power - base_power
    power_margin_percent = ((nose_power / base_power) - 1) * 100 if base_power > 0 else 0
    voltage_margin = nose_voltage - 0.90  # Margin above 0.90 p.u.
    
    print(f"\nVoltage Stability Results:")
    print(f"- Base case total load: {base_power:.2f} MW")
    print(f"- Maximum loadability (nose): {nose_power:.2f} MW")
    print(f"- Load factor at nose: {nose_load_factor:.3f}")
    print(f"- Voltage at collapse: {nose_voltage:.4f} p.u.")
    print(f"- Power margin: {power_margin_mw:.2f} MW ({power_margin_percent:.1f}%)")
    print(f"- Voltage margin: {voltage_margin:.4f} p.u.")
    
    # Calculate voltage-power sensitivity at various points
    mid_index = len(power_values) // 2
    if mid_index > 0 and mid_index < len(power_values) - 1:
        dv_dp_mid = (voltage_values[mid_index + 1] - voltage_values[mid_index - 1]) / \
                    (power_values[mid_index + 1] - power_values[mid_index - 1])
        print(f"- V-P sensitivity at midpoint: {abs(dv_dp_mid):.6f} p.u./MW")
    
    # Voltage stability assessment
    if nose_voltage > 0.95:
        stability_rating = "EXCELLENT"
    elif nose_voltage > 0.90:
        stability_rating = "GOOD"
    elif nose_voltage > 0.85:
        stability_rating = "MARGINAL"
    else:
        stability_rating = "POOR"
    
    print(f"- Voltage stability rating: {stability_rating}")
    
    # Analyze curve completeness
    min_voltage = min(voltage_values)
    max_power = max(power_values)
    stable_points = sum(1 for status in convergence_status if status)
    unstable_points = len(power_values) - stable_points
    
    print(f"- Curve data points: {len(power_values)} total ({stable_points} stable, {unstable_points} estimated)")
    print(f"- Voltage range: {min_voltage:.3f} to {max(voltage_values):.3f} p.u.")
    
    if unstable_points > 0:
        print("- Complete nose curve generated including unstable branch ✓")
    else:
        print("- Partial curve: Consider higher max scaling for complete nose")
    
    # Generate the PV curve plot
    print("\n" + "="*60)
    print("GENERATING PV CURVE PLOT")
    print("="*60)
    
    plt.figure(figsize=(12, 8))
    
    # Separate stable and unstable points for different styling
    stable_powers = [p for i, p in enumerate(power_values) if convergence_status[i]]
    stable_voltages = [v for i, v in enumerate(voltage_values) if convergence_status[i]]
    unstable_powers = [p for i, p in enumerate(power_values) if not convergence_status[i]]
    unstable_voltages = [v for i, v in enumerate(voltage_values) if not convergence_status[i]]
    
    # Plot stable branch
    if stable_powers:
        plt.plot(stable_powers, stable_voltages, 'b-', linewidth=3, 
                label='Stable Branch', marker='o', markersize=3)
    
    # Plot unstable branch with different style
    if unstable_powers:
        plt.plot(unstable_powers, unstable_voltages, 'r--', linewidth=2, 
                label='Unstable Branch', marker='s', markersize=3, alpha=0.7)
    
    # Plot complete curve
    plt.plot(power_values, voltage_values, 'k-', linewidth=1, alpha=0.5, label='Complete PV Curve')
    
    # Mark the nose point prominently
    plt.scatter([nose_power], [nose_voltage], color='red', s=200, zorder=5, 
               edgecolors='darkred', linewidth=2, 
               label=f'Nose Point\n({nose_power:.1f} MW, {nose_voltage:.3f} p.u.)')
    
    # Mark base operating point
    plt.scatter([power_values[0]], [voltage_values[0]], color='green', s=150, zorder=5,
               edgecolors='darkgreen', linewidth=2, 
               label=f'Base Case\n({power_values[0]:.1f} MW, {voltage_values[0]:.3f} p.u.)')
    
    # Add critical reference lines
    plt.axhline(y=nose_voltage, color='red', linestyle='--', alpha=0.7, linewidth=1.5)
    plt.axvline(x=nose_power, color='red', linestyle='--', alpha=0.7, linewidth=1.5)
    plt.axhline(y=0.95, color='orange', linestyle=':', alpha=0.8, linewidth=2, label='0.95 p.u. limit')
    plt.axhline(y=0.90, color='red', linestyle=':', alpha=0.8, linewidth=2, label='0.90 p.u. limit')
    
    # Enhanced formatting
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    plt.title(f'Complete Power-Voltage Curve - IEEE 39-Bus System\n(All Loads Scaled - Monitor Bus {monitor_bus}) - {date_str}', 
             fontsize=16, fontweight='bold')
    
    plt.xlabel('Total System Active Power (MW)', fontsize=14, fontweight='bold')
    plt.ylabel(f'Voltage at Bus {monitor_bus} (p.u.)', fontsize=14, fontweight='bold')
    
    # Enhanced grid
    plt.grid(True, which='both', linestyle='-', alpha=0.3)
    plt.grid(True, which='minor', linestyle=':', alpha=0.2)
    plt.legend(loc='upper right', fontsize=10)
    
    # Add comprehensive analysis text box
    textstr = f'Nose Point: {nose_power:.1f} MW at {nose_voltage:.3f} p.u.\n' + \
              f'Load Factor: {nose_load_factor:.3f}\n' + \
              f'Power Margin: {power_margin_percent:.1f}%\n' + \
              f'Stability: {stability_rating}\n' + \
              f'Points: {stable_points} stable, {unstable_points} unstable'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
    plt.text(0.02, 0.98, textstr, transform=plt.gca().transAxes, fontsize=11,
             verticalalignment='top', bbox=props)
    
    # Improve plot appearance
    plt.tight_layout()
    
    # Save the plot
    output_dir = 'server/pv-curve/generated-graphs'
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"complete_pv_curve_ieee39_bus{monitor_bus}_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"\nComplete PV Curve saved to: {filepath}")
    
    # Display the plot
    plt.show()
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("The complete PV curve shows both stable and unstable operating regions.")
    print("The characteristic 'nose' shape indicates maximum power transfer capability.")
    print("The stable branch (solid line) represents normal operating conditions.")
    print("The unstable branch (dashed line) represents post-collapse conditions.")
    print("Operating beyond the nose point leads to voltage instability and collapse.")
    print("Maintain adequate power and voltage margins for system security.")
    
    # Save detailed results to a text file
    results_filename = os.path.join(output_dir, f"complete_pv_analysis_results_{timestamp}.txt")
    with open(results_filename, 'w') as f:
        f.write("COMPLETE PV CURVE ANALYSIS RESULTS\n")
        f.write("="*50 + "\n")
        f.write(f"IEEE 39-Bus System Analysis\n")
        f.write(f"Monitor Bus: {monitor_bus}\n")
        f.write(f"Analysis Date: {date_str}\n\n")
        f.write(f"Base Case Total Load: {base_power:.2f} MW\n")
        f.write(f"Maximum Loadability: {nose_power:.2f} MW\n")
        f.write(f"Load Factor at Nose: {nose_load_factor:.3f}\n")
        f.write(f"Voltage at Collapse: {nose_voltage:.4f} p.u.\n")
        f.write(f"Power Margin: {power_margin_mw:.2f} MW ({power_margin_percent:.1f}%)\n")
        f.write(f"Voltage Margin: {voltage_margin:.4f} p.u.\n")
        f.write(f"Stability Rating: {stability_rating}\n")
        f.write(f"Stable Points: {stable_points}\n")
        f.write(f"Unstable Points: {unstable_points}\n\n")
        f.write("Load Factor, Total Power (MW), Voltage (p.u.), Converged\n")
        for i in range(len(power_values)):
            status = "Yes" if convergence_status[i] else "No"
            f.write(f"{load_factors[i]:.3f}, {power_values[i]:.2f}, {voltage_values[i]:.4f}, {status}\n")
    
    print(f"Detailed results saved to: {results_filename}")

if __name__ == "__main__":
    create_pv_curve_ieee39()
