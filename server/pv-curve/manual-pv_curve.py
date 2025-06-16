import pandapower as pp
import pandapower.networks as pn
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime

def create_pv_curve():
    """
    Generates a PV curve by prompting the user for inputs, running a pandapower simulation,
    and saving the resulting plot.
    """
    # 1. Get user inputs
    print("--- PV Curve Generator ---")
    network_case_str = input("Enter the network case (e.g., case14, case39, case118): ")
    bus_idx_str = input("Enter the bus index to monitor: ")
    max_scale_str = input("Enter the maximum load scaling factor (e.g., 2.5): ")
    num_points_str = input("Enter the number of points for the curve (e.g., 50): ")

    # 2. Validate and convert inputs
    try:
        if hasattr(pn, network_case_str):
            net = getattr(pn, network_case_str)()
        else:
            print(f"Error: Network case '{network_case_str}' not found in pandapower.networks.")
            return

        bus_idx = int(bus_idx_str)
        if bus_idx not in net.bus.index:
            print(f"Error: Bus index {bus_idx} is not valid for {network_case_str}.")
            print(f"Valid bus indices are from {net.bus.index.min()} to {net.bus.index.max()}.")
            return

        max_scale = float(max_scale_str)
        num_points = int(num_points_str)
    except (ValueError, AttributeError) as e:
        print(f"Invalid input. Please check your entries. Details: {e}")
        return

    # Add choice for scaling method
    scaling_choice = input("Scale [A]ll loads or only loads at the [S]elected bus? (A/S): ").upper()
    if scaling_choice not in ['A', 'S']:
        print("Invalid choice. Defaulting to scaling ALL loads.")
        scaling_choice = 'A'
    
    # 3. Prepare for the simulation sweep
    # Store original loads to scale them in each step
    base_p = net.load.p_mw.copy()
    base_q = net.load.q_mvar.copy()

    # Identify the specific loads connected to the target bus for the 'single bus' case
    target_load_indices = net.load[net.load.bus == bus_idx].index
    if scaling_choice == 'S' and target_load_indices.empty:
        print(f"Warning: No loads were found at bus {bus_idx}. Cannot perform single-bus scaling.")
        print("Defaulting to scaling ALL loads instead.")
        scaling_choice = 'A'

    # Create an array of load scaling factors
    scale_factors = np.linspace(1.0, max_scale, num_points)

    p_values = []
    v_values = []
    
    print("\nStarting PV curve simulation...")
    print("-" * 30)

    # 4. Run the simulation loop
    for i, factor in enumerate(scale_factors):
        # Apply the scaling factor based on user's choice
        if scaling_choice == 'A':
            # Scale all loads in the network
            net.load['p_mw'] = base_p * factor
            net.load['q_mvar'] = base_q * factor
        else: # 'S'
            # Scale only the loads connected to the selected bus
            net.load.loc[target_load_indices, 'p_mw'] = base_p[target_load_indices] * factor
            net.load.loc[target_load_indices, 'q_mvar'] = base_q[target_load_indices] * factor

        try:
            # Run the power flow calculation
            pp.runpp(net, enforce_q_lims=True)
            if not net.converged:
                print(f"Step {i+1}/{num_points}: Power flow did not converge at scaling factor {factor:.3f}. Stopping.")
                break
        except Exception as e:
            print(f"Step {i+1}/{num_points}: An exception occurred at scaling factor {factor:.3f}: {e}. Stopping.")
            break
            
        # If converged, store the results
        if scaling_choice == 'A':
            # For system-wide scaling, the x-axis is the total system load
            p_val = net.res_load.p_mw.sum()
        else:  # 'S'
            # For single-bus scaling, the x-axis is the power at that bus
            p_val = net.res_load.p_mw[net.load.bus == bus_idx].sum()

        bus_voltage = net.res_bus.vm_pu.at[bus_idx]
        
        p_values.append(p_val)
        v_values.append(bus_voltage)

        if scaling_choice == 'A':
            print(f"Step {i+1}/{num_points}: Factor={factor:.3f} | Total Load={p_val:.2f} MW | Bus {bus_idx} Voltage={bus_voltage:.4f} p.u.")
        else:
            print(f"Step {i+1}/{num_points}: Factor={factor:.3f} | Load at Bus {bus_idx}={p_val:.2f} MW | Bus {bus_idx} Voltage={bus_voltage:.4f} p.u.")

    if not p_values:
        print("\nNo successful power flow simulations were completed. Cannot generate a plot.")
        return

    # 5. Identify the "nose" of the curve (voltage collapse point)
    nose_p_index = np.argmax(p_values)
    nose_p = p_values[nose_p_index]
    nose_v = v_values[nose_p_index]
    print("-" * 30)
    print(f"Voltage collapse point (nose) identified at P = {nose_p:.2f} MW, V = {nose_v:.4f} p.u.")

    # 6. Plot the results
    plt.figure(figsize=(12, 7))
    plt.plot(p_values, v_values, '-o', markersize=5, label=f'Bus {bus_idx} Voltage')
    
    # Mark the nose point clearly
    plt.scatter([nose_p], [nose_v], color='red', s=150, zorder=5, edgecolors='black', label=f'Nose Point ({nose_p:.2f} MW)')
    plt.axvline(x=nose_p, color='r', linestyle='--', linewidth=1)
    plt.axhline(y=nose_v, color='r', linestyle='--', linewidth=1)
    
    # Add titles and labels
    date_str = datetime.now().strftime('%Y-%m-%d')
    scaling_desc = "All Loads Scaled" if scaling_choice == 'A' else f"Load at Bus {bus_idx} Scaled"
    plt.title(f"PV Curve for Bus {bus_idx} in {network_case_str.upper()} ({scaling_desc}) - {date_str}", fontsize=16)
    
    if scaling_choice == 'A':
        plt.xlabel("Total System Active Power Load (MW)", fontsize=12)
    else:  # 'S'
        plt.xlabel(f"Active Power Load at Bus {bus_idx} (MW)", fontsize=12)

    plt.ylabel(f"Voltage at Bus {bus_idx} (p.u.)", fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend(fontsize=10)
    plt.tight_layout()

    # 7. Save the plot to the specified directory
    output_dir = 'server/pv-curve/generated-graphs'
    os.makedirs(output_dir, exist_ok=True)
        
    filename_date = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"pv_curve_{network_case_str}_bus{bus_idx}_{filename_date}.png"
    filepath = os.path.join(output_dir, filename)
    
    plt.savefig(filepath, dpi=300)
    print(f"\nGraph successfully saved to: {filepath}")

# Entry point for the script
if __name__ == "__main__":
    create_pv_curve()
