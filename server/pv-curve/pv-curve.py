import pandapower as pp
import pandapower.networks as pn
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List, Optional, Dict, Any
import io
import base64
import os

# Create generated-graphs directory if it doesn't exist
GRAPHS_DIR = os.path.join(os.path.dirname(__file__), "generated-graphs")
os.makedirs(GRAPHS_DIR, exist_ok=True)

def create_pv_curve(
    network_case: str = "case39",
    bus_idx: int = 10,
    max_scale: float = 2.0,
    num_points: int = 41,
    return_plot: bool = True
) -> Dict[str, Any]:
    """
    Create a PV curve for voltage stability analysis.
    
    Args:
        network_case: IEEE test case to use ('case39', 'case118', etc.)
        bus_idx: Bus index to monitor for voltage
        max_scale: Maximum load scaling factor (e.g., 2.0 = 200% of base load)
        num_points: Number of points to calculate along the curve
        return_plot: Whether to return base64 encoded plot image
        
    Returns:
        Dictionary containing:
        - P_list: List of total power values [MW]
        - V_list: List of voltage values [p.u.]
        - nose_point: Dictionary with nose point information
        - voltage_margin: Voltage margin information
        - plot_base64: Base64 encoded plot (if return_plot=True)
        - success: Boolean indicating if analysis completed successfully
        - error_message: Error message if analysis failed
    """
    
    try:
        # Load the specified IEEE test network
        if network_case == "case39":
            net = pn.case39()
        elif network_case == "case118":
            net = pn.case118()
        elif network_case == "case14":
            net = pn.case14()
        elif network_case == "case30":
            net = pn.case30()
        else:
            return {
                "success": False,
                "error_message": f"Unsupported network case: {network_case}. Use 'case39', 'case118', 'case14', or 'case30'."
            }
        
        # Validate bus index
        if bus_idx >= len(net.bus):
            return {
                "success": False,
                "error_message": f"Bus index {bus_idx} is out of range. Network has {len(net.bus)} buses (0-{len(net.bus)-1})."
            }
        
        # Save base loads
        if len(net.load) == 0:
            return {
                "success": False,
                "error_message": "Network has no loads defined."
            }
            
        base_p = net.load['p_mw'].values.copy()
        base_q = net.load['q_mvar'].values.copy()
        
        # Run initial power flow to get base case
        try:
            pp.runpp(net)
            base_voltage = net.res_bus.at[bus_idx, 'vm_pu']
            base_total_p = net.res_load['p_mw'].sum()
        except pp.LoadflowNotConverged:
            return {
                "success": False,
                "error_message": "Base case power flow failed to converge."
            }
        
        # Initialize lists to store results
        P_list, V_list = [], []
        scale_factors = []
        
        # Incrementally increase loading
        for scale in np.linspace(1.0, max_scale, num_points):
            # Update loads
            net.load['p_mw'] = base_p * scale
            net.load['q_mvar'] = base_q * scale
            
            try:
                # Run power flow
                pp.runpp(net)
                
                # Record results
                total_p = net.res_load['p_mw'].sum()
                v_bus = net.res_bus.at[bus_idx, 'vm_pu']
                
                P_list.append(total_p)
                V_list.append(v_bus)
                scale_factors.append(scale)
                
            except pp.LoadflowNotConverged:
                # Voltage collapse reached
                break
        
        if len(P_list) < 2:
            return {
                "success": False,
                "error_message": "Insufficient data points - voltage collapse occurred too early."
            }
        
        # Find nose point (maximum power point)
        nose_idx = np.argmax(P_list)
        nose_power = P_list[nose_idx]
        nose_voltage = V_list[nose_idx]
        nose_scale = scale_factors[nose_idx]
        
        # Calculate voltage margin
        voltage_margin_mw = nose_power - base_total_p
        voltage_margin_percent = ((nose_scale - 1.0) * 100)
        
        # Create plot if requested
        plot_base64 = None
        if return_plot:
            plt.figure(figsize=(10, 6))
            plt.plot(P_list, V_list, 'b-o', linewidth=2, markersize=4, label='PV Curve')
            plt.plot(base_total_p, base_voltage, 'go', markersize=8, label=f'Base Case (Bus {bus_idx})')
            plt.plot(nose_power, nose_voltage, 'ro', markersize=8, label=f'Nose Point')
            
            plt.xlabel('Total Load P [MW]', fontsize=12)
            plt.ylabel(f'Voltage at Bus {bus_idx} [p.u.]', fontsize=12)
            plt.title(f'PV Curve - {network_case.upper()} Network (Bus {bus_idx})', fontsize=14)
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            # Add annotations
            plt.annotate(f'Base: {base_total_p:.1f} MW\n{base_voltage:.3f} p.u.', 
                        xy=(base_total_p, base_voltage), xytext=(10, 10),
                        textcoords='offset points', fontsize=10,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7))
            
            plt.annotate(f'Nose: {nose_power:.1f} MW\n{nose_voltage:.3f} p.u.', 
                        xy=(nose_power, nose_voltage), xytext=(10, -30),
                        textcoords='offset points', fontsize=10,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7))
            
            plt.tight_layout()
            
            # Convert plot to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            plot_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
        
        # Prepare results
        results = {
            "success": True,
            "network_case": network_case,
            "monitored_bus": bus_idx,
            "P_list": P_list,
            "V_list": V_list,
            "scale_factors": scale_factors,
            "base_case": {
                "power_mw": float(base_total_p),
                "voltage_pu": float(base_voltage),
                "scale_factor": 1.0
            },
            "nose_point": {
                "power_mw": float(nose_power),
                "voltage_pu": float(nose_voltage),
                "scale_factor": float(nose_scale),
                "index": int(nose_idx)
            },
            "voltage_margin": {
                "power_margin_mw": float(voltage_margin_mw),
                "percent_margin": float(voltage_margin_percent)
            },
            "analysis_info": {
                "total_points": len(P_list),
                "max_scale_reached": float(scale_factors[-1]),
                "convergence_failure": scale_factors[-1] < max_scale
            }
        }
        
        if return_plot and plot_base64:
            results["plot_base64"] = plot_base64
            
        return results
        
    except Exception as e:
        return {
            "success": False,
            "error_message": f"Unexpected error: {str(e)}"
        }

def get_available_networks() -> Dict[str, Dict[str, Any]]:
    """
    Get information about available IEEE test networks.
    
    Returns:
        Dictionary with network information
    """
    networks = {
        "case14": {
            "name": "IEEE 14-bus system",
            "buses": 14,
            "description": "Small test system, good for quick analysis"
        },
        "case30": {
            "name": "IEEE 30-bus system", 
            "buses": 30,
            "description": "Medium-sized test system"
        },
        "case39": {
            "name": "IEEE 39-bus system",
            "buses": 39, 
            "description": "New England 39-bus system, commonly used for stability studies"
        },
        "case118": {
            "name": "IEEE 118-bus system",
            "buses": 118,
            "description": "Large test system for comprehensive analysis"
        }
    }
    return networks

def get_network_info(network_case: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific network case.
    
    Args:
        network_case: IEEE test case name
        
    Returns:
        Dictionary with network details
    """
    try:
        if network_case == "case39":
            net = pn.case39()
        elif network_case == "case118":
            net = pn.case118()
        elif network_case == "case14":
            net = pn.case14()
        elif network_case == "case30":
            net = pn.case30()
        else:
            return {"success": False, "error": f"Unknown network case: {network_case}"}
        
        # Get network statistics
        info = {
            "success": True,
            "network_case": network_case,
            "num_buses": len(net.bus),
            "num_lines": len(net.line),
            "num_loads": len(net.load),
            "num_generators": len(net.gen),
            "num_transformers": len(net.trafo) if hasattr(net, 'trafo') else 0,
            "load_buses": net.load['bus'].tolist() if len(net.load) > 0 else [],
            "total_load_mw": float(net.load['p_mw'].sum()) if len(net.load) > 0 else 0.0,
            "total_load_mvar": float(net.load['q_mvar'].sum()) if len(net.load) > 0 else 0.0
        }
        
        return info
        
    except Exception as e:
        return {"success": False, "error": f"Error getting network info: {str(e)}"}

# Example usage and testing
if __name__ == "__main__":
    print("Testing PV Curve Analysis...")
    
    # Test with IEEE 39-bus system - Generate and SHOW the plot
    result = create_pv_curve(
        network_case="case39",
        bus_idx=10,
        max_scale=1.8,
        num_points=31,
        return_plot=True  # Generate the plot
    )
    
    if result["success"]:
        print(f"\nPV Curve Analysis Results:")
        print(f"Network: {result['network_case']}")
        print(f"Monitored Bus: {result['monitored_bus']}")
        print(f"Base Case: {result['base_case']['power_mw']:.1f} MW, {result['base_case']['voltage_pu']:.3f} p.u.")
        print(f"Nose Point: {result['nose_point']['power_mw']:.1f} MW, {result['nose_point']['voltage_pu']:.3f} p.u.")
        print(f"Voltage Margin: {result['voltage_margin']['power_margin_mw']:.1f} MW ({result['voltage_margin']['percent_margin']:.1f}%)")
        print(f"Analysis Points: {result['analysis_info']['total_points']}")
        
        # Create and display the plot directly
        plt.figure(figsize=(10, 6))
        plt.plot(result['P_list'], result['V_list'], 'b-o', linewidth=2, markersize=4, label='PV Curve')
        plt.plot(result['base_case']['power_mw'], result['base_case']['voltage_pu'], 
                'go', markersize=8, label=f"Base Case (Bus {result['monitored_bus']})")
        plt.plot(result['nose_point']['power_mw'], result['nose_point']['voltage_pu'], 
                'ro', markersize=8, label='Nose Point')
        
        plt.xlabel('Total Load P [MW]', fontsize=12)
        plt.ylabel(f"Voltage at Bus {result['monitored_bus']} [p.u.]", fontsize=12)
        plt.title(f"PV Curve - {result['network_case'].upper()} Network (Bus {result['monitored_bus']})", fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Add annotations
        plt.annotate(f"Base: {result['base_case']['power_mw']:.1f} MW\n{result['base_case']['voltage_pu']:.3f} p.u.", 
                    xy=(result['base_case']['power_mw'], result['base_case']['voltage_pu']), xytext=(10, 10),
                    textcoords='offset points', fontsize=10,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7))
        
        plt.annotate(f"Nose: {result['nose_point']['power_mw']:.1f} MW\n{result['nose_point']['voltage_pu']:.3f} p.u.", 
                    xy=(result['nose_point']['power_mw'], result['nose_point']['voltage_pu']), xytext=(10, -30),
                    textcoords='offset points', fontsize=10,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7))
        
        plt.tight_layout()
        
        # Save the plot as a file in the generated-graphs directory
        filename = os.path.join(GRAPHS_DIR, 'pv_curve_case39_bus10.png')
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"\nPlot saved as: {filename}")
        
        # Show the plot (this will open a window)
        plt.show()
        
    else:
        print(f"Error: {result['error_message']}")
    
    # Show available networks
    print(f"\nAvailable Networks:")
    networks = get_available_networks()
    for case, info in networks.items():
        print(f"  {case}: {info['name']} ({info['buses']} buses)")

def generate_and_save_pv_curve(network_case="case39", bus_idx=10, filename=None):
    """
    Simple function to generate and save a PV curve plot.
    
    Args:
        network_case: IEEE test case ('case14', 'case30', 'case39', 'case118')
        bus_idx: Bus number to monitor
        filename: Output filename (optional)
    """
    result = create_pv_curve(network_case=network_case, bus_idx=bus_idx, return_plot=False)
    
    if not result["success"]:
        print(f"Error: {result['error_message']}")
        return
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    plt.plot(result['P_list'], result['V_list'], 'b-o', linewidth=2, markersize=6, label='PV Curve')
    plt.plot(result['base_case']['power_mw'], result['base_case']['voltage_pu'], 
            'go', markersize=10, label=f"Base Case")
    plt.plot(result['nose_point']['power_mw'], result['nose_point']['voltage_pu'], 
            'ro', markersize=10, label='Nose Point (Voltage Collapse)')
    
    plt.xlabel('Total Load P [MW]', fontsize=14)
    plt.ylabel(f"Voltage at Bus {bus_idx} [p.u.]", fontsize=14)
    plt.title(f"PV Curve Analysis - {network_case.upper()} Network\nBus {bus_idx} Voltage Stability", fontsize=16)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=12)
    
    # Add detailed annotations
    plt.annotate(f"Base Operating Point\n{result['base_case']['power_mw']:.1f} MW, {result['base_case']['voltage_pu']:.3f} p.u.", 
                xy=(result['base_case']['power_mw'], result['base_case']['voltage_pu']), xytext=(20, 20),
                textcoords='offset points', fontsize=11,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.8),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    plt.annotate(f"Voltage Collapse Point\n{result['nose_point']['power_mw']:.1f} MW, {result['nose_point']['voltage_pu']:.3f} p.u.\nMargin: {result['voltage_margin']['power_margin_mw']:.1f} MW", 
                xy=(result['nose_point']['power_mw'], result['nose_point']['voltage_pu']), xytext=(-80, -40),
                textcoords='offset points', fontsize=11,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcoral', alpha=0.8),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    plt.tight_layout()
    
    # Save with default filename if none provided
    if filename is None:
        filename = f"pv_curve_{network_case}_bus{bus_idx}.png"
    
    # Save to generated-graphs directory
    filepath = os.path.join(GRAPHS_DIR, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"PV Curve saved as: {filepath}")
    
    # Display the plot
    plt.show()
    
    return result

def list_generated_graphs() -> List[str]:
    """
    List all generated PV curve graphs in the generated-graphs directory.
    
    Returns:
        List of filenames in the generated-graphs directory
    """
    try:
        files = [f for f in os.listdir(GRAPHS_DIR) if f.endswith('.png')]
        return sorted(files)
    except FileNotFoundError:
        return []

def get_graph_path(filename: str) -> str:
    """
    Get the full path to a graph file in the generated-graphs directory.
    
    Args:
        filename: Name of the graph file
        
    Returns:
        Full path to the graph file
    """
    return os.path.join(GRAPHS_DIR, filename)

def clear_generated_graphs() -> int:
    """
    Clear all generated graph files.
    
    Returns:
        Number of files deleted
    """
    count = 0
    try:
        for filename in os.listdir(GRAPHS_DIR):
            if filename.endswith('.png'):
                os.remove(os.path.join(GRAPHS_DIR, filename))
                count += 1
    except FileNotFoundError:
        pass
    return count
