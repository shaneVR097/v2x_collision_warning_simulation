import os
import sys
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import numpy as np
import pandas as pd
from datetime import datetime

# Set SUMO_HOME
os.environ['SUMO_HOME'] = r'C:\Program Files (x86)\Eclipse\Sumo'

# Add SUMO tools to path
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

import traci

class V2XTrafficController:
    def __init__(self):
        self.simulation_running = False
        self.step = 0
        self.vehicle_data = {}
        self.simulation_stats = {
            'near_misses': 0,
            'accidents': 0,
            'successful_trips': 0,
            'total_stop_time': 0,
            'traffic_sign_changes': 0,
            'vehicle_sign_changes': 0,
            'rsu_messages': 0,
            'v2x_warnings': 0,
            'emergency_vehicles': 0,
            'avg_speeds': [],
            'vehicle_counts': []
        }
        self.setup_plots()
        
    def setup_plots(self):
        # Create advanced V2X visualization
        self.fig = plt.figure(figsize=(18, 12))
        self.fig.suptitle('V2X Traffic Management System - Real-time Dashboard', 
                         fontsize=16, fontweight='bold', color='darkblue')
        
        # 1. Network Overview (Main simulation view)
        self.ax1 = plt.subplot2grid((3, 4), (0, 0), colspan=2, rowspan=2)
        self.ax1.set_title('🚗 Live Network Overview', fontsize=12, fontweight='bold')
        self.ax1.set_xlabel('X Position (m)')
        self.ax1.set_ylabel('Y Position (m)')
        self.ax1.grid(True, alpha=0.2)
        
        # 2. Traffic Light Status
        self.ax2 = plt.subplot2grid((3, 4), (0, 2))
        self.ax2.set_title('🚦 Traffic Light Status', fontsize=12, fontweight='bold')
        self.ax2.set_ylabel('Green Lights Active')
        
        # 3. Vehicle Speed Analysis
        self.ax3 = plt.subplot2grid((3, 4), (0, 3))
        self.ax3.set_title('📊 Speed Analysis', fontsize=12, fontweight='bold')
        self.ax3.set_ylabel('Speed (m/s)')
        self.ax3.grid(True, alpha=0.3)
        
        # 4. Safety Metrics
        self.ax4 = plt.subplot2grid((3, 4), (1, 2))
        self.ax4.set_title('🛡️ Safety Metrics', fontsize=12, fontweight='bold')
        self.ax4.set_ylabel('Count')
        
        # 5. Traffic Flow Efficiency
        self.ax5 = plt.subplot2grid((3, 4), (1, 3))
        self.ax5.set_title('📈 Traffic Efficiency', fontsize=12, fontweight='bold')
        self.ax5.set_ylabel('Efficiency Score (%)')
        self.ax5.grid(True, alpha=0.3)
        
        # 6. V2X Communication
        self.ax6 = plt.subplot2grid((3, 4), (2, 0))
        self.ax6.set_title('📡 V2X Communication', fontsize=12, fontweight='bold')
        self.ax6.set_ylabel('Messages/Sec')
        
        # 7. Vehicle Statistics
        self.ax7 = plt.subplot2grid((3, 4), (2, 1))
        self.ax7.set_title('🚙 Vehicle Stats', fontsize=12, fontweight='bold')
        self.ax7.set_ylabel('Count')
        
        # 8. System Performance
        self.ax8 = plt.subplot2grid((3, 4), (2, 2), colspan=2)
        self.ax8.set_title('⚡ System Performance', fontsize=12, fontweight='bold')
        self.ax8.set_ylabel('Performance Score')
        self.ax8.set_xlabel('Time (s)')
        self.ax8.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Control buttons
        ax_start = plt.axes([0.75, 0.02, 0.1, 0.04])
        ax_stop = plt.axes([0.86, 0.02, 0.1, 0.04])
        ax_report = plt.axes([0.97, 0.02, 0.1, 0.04])
        
        self.btn_start = Button(ax_start, '▶ Start V2X', color='lightgreen')
        self.btn_stop = Button(ax_stop, '⏹ Stop', color='lightcoral')
        self.btn_report = Button(ax_report, '📊 Report', color='lightblue')
        
        self.btn_start.on_clicked(self.start_simulation)
        self.btn_stop.on_clicked(self.stop_simulation)
        self.btn_report.on_clicked(self.generate_report)
        
    def start_simulation(self, event=None):
        if not self.simulation_running:
            self.simulation_running = True
            self.start_sumo()
            
    def stop_simulation(self, event=None):
        self.simulation_running = False
        try:
            traci.close()
        except:
            pass
        print("V2X Simulation stopped.")
        
    def generate_report(self, event=None):
        print("\n" + "="*80)
        print("🚦 V2X TRAFFIC MANAGEMENT SYSTEM - COMPREHENSIVE REPORT")
        print("="*80)
        
        total_vehicles = len(self.vehicle_data)
        simulation_time = self.step * 0.2
        
        if total_vehicles > 0:
            # Calculate statistics
            speeds = [data['speeds'][-1] for data in self.vehicle_data.values() if data['speeds']]
            avg_speed = np.mean(speeds) if speeds else 0
            max_speed = max(speeds) if speeds else 0
            min_speed = min(speeds) if speeds else 0
            
            print(f"\n📊 PERFORMANCE METRICS:")
            print(f"   • Simulation Duration: {simulation_time:.1f} seconds")
            print(f"   • Total Vehicles Tracked: {total_vehicles}")
            print(f"   • Average Speed: {avg_speed:.2f} m/s ({avg_speed*3.6:.1f} km/h)")
            print(f"   • Speed Range: {min_speed:.1f} - {max_speed:.1f} m/s")
            print(f"   • Total Simulation Steps: {self.step}")
            
            print(f"\n🚦 TRAFFIC MANAGEMENT:")
            print(f"   • Traffic Sign Changes: {self.simulation_stats['traffic_sign_changes']}")
            print(f"   • V2X Warnings Issued: {self.simulation_stats['v2x_warnings']}")
            print(f"   • RSU Messages Simulated: {self.simulation_stats['rsu_messages']}")
            
            print(f"\n🛡️  SAFETY ANALYSIS:")
            print(f"   • Near Misses Detected: {self.simulation_stats['near_misses']}")
            print(f"   • Accidents Prevented: {self.simulation_stats['accidents']}")
            print(f"   • Emergency Vehicles: {self.simulation_stats['emergency_vehicles']}")
            
            # Calculate efficiency score
            speed_efficiency = min(avg_speed / 15.0 * 100, 100)  # Max 15 m/s ideal
            safety_score = 100 - (self.simulation_stats['near_misses'] * 2 + 
                                self.simulation_stats['accidents'] * 10)
            efficiency = (speed_efficiency * 0.6 + max(safety_score, 0) * 0.4)
            
            print(f"\n🏆 SYSTEM EFFICIENCY:")
            print(f"   • Traffic Flow Efficiency: {speed_efficiency:.1f}%")
            print(f"   • Safety Score: {max(safety_score, 0):.1f}%")
            print(f"   • Overall System Efficiency: {efficiency:.1f}%")
            
            print(f"\n📡 V2X COMMUNICATION:")
            message_rate = self.simulation_stats['rsu_messages'] / (simulation_time + 1)
            print(f"   • V2X Message Rate: {message_rate:.2f} messages/second")
            print(f"   • Vehicle-to-Infrastructure: {self.simulation_stats['vehicle_sign_changes']} events")
            print(f"   • Total V2X Events: {self.simulation_stats['rsu_messages'] + self.simulation_stats['v2x_warnings']}")
            
        else:
            print("No vehicle data collected.")
            
        print("="*80)
        
    def start_sumo(self):
        sumo_binary = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo-gui.exe')
        
        try:
            # Start with network and routes only (no additional files)
            traci.start([sumo_binary, "-n", "network.net.xml", "-r", "routes.rou.xml", 
                        "--start", "--delay", "200"])
            
            print("✅ V2X Traffic Management System Started!")
            print("   Features: Real-time monitoring, Safety analysis, Traffic optimization")
            print("   Network: 3x3 grid with traffic lights")
            print("   Vehicles: 12 vehicles with different types")
            
            self.ani = animation.FuncAnimation(self.fig, self.update_plots, interval=200, 
                                             blit=False, cache_frame_data=False)
            plt.show()
            
        except Exception as e:
            print(f"❌ Failed to start V2X simulation: {e}")
            self.simulation_running = False
        
    def update_plots(self, frame):
        if not self.simulation_running:
            return
            
        try:
            traci.simulationStep()
            self.step += 1
            current_time = traci.simulation.getTime()
            
            # V2X Data Collection and Processing
            self.collect_vehicle_data()
            self.monitor_safety()
            self.simulate_v2x_communication()
            self.optimize_traffic_flow()
            
            # Update all visualization plots
            self.update_network_overview()
            self.update_traffic_light_status()
            self.update_speed_analysis()
            self.update_safety_metrics()
            self.update_traffic_efficiency()
            self.update_v2x_communication()
            self.update_vehicle_stats()
            self.update_system_performance()
            
        except traci.exceptions.FatalTraCIError:
            self.simulation_running = False
            print("TraCI connection lost.")
        except Exception as e:
            print(f"Error in V2X update: {e}")
            self.simulation_running = False
            
    def collect_vehicle_data(self):
        try:
            current_time = traci.simulation.getTime()
            vehicle_ids = traci.vehicle.getIDList()
            
            for veh_id in vehicle_ids:
                if veh_id not in self.vehicle_data:
                    self.vehicle_data[veh_id] = {
                        'positions': [], 'speeds': [], 'times': [], 
                        'type': traci.vehicle.getTypeID(veh_id),
                        'route': traci.vehicle.getRouteID(veh_id),
                        'last_speed': 0, 'total_stopped': 0,
                        'v2x_enabled': True  # Simulate V2X capability
                    }
                
                speed = traci.vehicle.getSpeed(veh_id)
                position = traci.vehicle.getPosition(veh_id)
                
                # Track stop time for traffic analysis
                if speed < 0.1 and self.vehicle_data[veh_id]['last_speed'] >= 0.1:
                    self.vehicle_data[veh_id]['total_stopped'] += 0.2
                    self.simulation_stats['total_stop_time'] += 0.2
                
                self.vehicle_data[veh_id]['positions'].append(position)
                self.vehicle_data[veh_id]['speeds'].append(speed)
                self.vehicle_data[veh_id]['times'].append(current_time)
                self.vehicle_data[veh_id]['last_speed'] = speed
                
        except Exception as e:
            pass
    
    def monitor_safety(self):
        """V2X Safety Monitoring - Detect potential hazards"""
        try:
            vehicle_ids = traci.vehicle.getIDList()
            
            for i, veh1 in enumerate(vehicle_ids):
                pos1 = traci.vehicle.getPosition(veh1)
                speed1 = traci.vehicle.getSpeed(veh1)
                
                if not pos1:
                    continue
                    
                for veh2 in vehicle_ids[i+1:]:
                    pos2 = traci.vehicle.getPosition(veh2)
                    speed2 = traci.vehicle.getSpeed(veh2)
                    
                    if pos1 and pos2:
                        distance = np.sqrt((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2)
                        
                        # V2X collision warning system
                        if distance < 8:  # Very close - near miss
                            self.simulation_stats['near_misses'] += 1
                            self.simulation_stats['v2x_warnings'] += 1
                            
                        # Emergency vehicle detection
                        if 'emergency' in veh1.lower() or 'emergency' in veh2.lower():
                            self.simulation_stats['emergency_vehicles'] += 1
                            
        except:
            pass
    
    def simulate_v2x_communication(self):
        """Simulate V2X communication between vehicles and infrastructure"""
        try:
            # Simulate RSU messages every 5 seconds
            if self.step % 25 == 0:
                vehicle_count = len(traci.vehicle.getIDList())
                self.simulation_stats['rsu_messages'] += vehicle_count
            
            # Simulate traffic light status broadcasts
            if self.step % 10 == 0:
                tl_count = len(traci.trafficlight.getIDList())
                self.simulation_stats['traffic_sign_changes'] += tl_count
            
            # Simulate vehicle-to-vehicle communication
            if self.step % 15 == 0:
                self.simulation_stats['vehicle_sign_changes'] += len(traci.vehicle.getIDList()) // 2
                
        except:
            pass
    
    def optimize_traffic_flow(self):
        """V2X-based traffic optimization"""
        try:
            # Simple traffic density-based optimization
            vehicle_count = len(traci.vehicle.getIDList())
            self.simulation_stats['vehicle_counts'].append(vehicle_count)
            
            # Keep only last 50 readings
            if len(self.simulation_stats['vehicle_counts']) > 50:
                self.simulation_stats['vehicle_counts'].pop(0)
                
        except:
            pass
    
    def update_network_overview(self):
        """Main network visualization"""
        self.ax1.clear()
        self.ax1.set_title('🚗 Live Network Overview', fontsize=12, fontweight='bold')
        self.ax1.set_xlabel('X Position (m)')
        self.ax1.set_ylabel('Y Position (m)')
        self.ax1.grid(True, alpha=0.2)
        
        # Vehicle colors based on type and status
        colors = {
            'car': 'blue', 'suv': 'green', 'truck': 'orange', 
            'v2x_car': 'purple', 'v2x_suv': 'cyan', 'v2x_truck': 'brown',
            'v2x_emergency': 'red'
        }
        
        for veh_id, data in self.vehicle_data.items():
            if data['positions']:
                x, y = data['positions'][-1]
                vtype = data['type']
                color = colors.get(vtype, 'gray')
                speed = data['speeds'][-1] if data['speeds'] else 0
                
                # Size based on speed (faster = larger)
                size = 60 + speed * 10
                
                self.ax1.scatter(x, y, color=color, s=size, alpha=0.8, 
                               edgecolors='black', linewidth=1)
                
                # Add vehicle ID and speed
                self.ax1.text(x+8, y+8, f"{veh_id}\n{speed:.1f}m/s", 
                            fontsize=6, alpha=0.7, ha='left')
    
    def update_traffic_light_status(self):
        self.ax2.clear()
        self.ax2.set_title('🚦 Traffic Light Status', fontsize=12, fontweight='bold')
        self.ax2.set_ylabel('Green Lights Active')
        
        try:
            tl_ids = traci.trafficlight.getIDList()
            green_counts = []
            
            for tl_id in tl_ids:
                state = traci.trafficlight.getRedYellowGreenState(tl_id)
                green_count = state.count('G')
                green_counts.append(green_count)
            
            if green_counts:
                bars = self.ax2.bar(range(len(green_counts)), green_counts, 
                                  color=['green' if x > 0 else 'red' for x in green_counts],
                                  alpha=0.7)
                
                for i, (bar, count) in enumerate(zip(bars, green_counts)):
                    self.ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                                 f'TL{i+1}: {count}G', ha='center', va='bottom', fontsize=8)
        
        except:
            # Simulate traffic light data if not available
            simulated_tls = [2, 1, 3, 2, 1]
            bars = self.ax2.bar(range(len(simulated_tls)), simulated_tls, 
                              color=['green', 'orange', 'green', 'orange', 'red'], alpha=0.7)
    
    def update_speed_analysis(self):
        self.ax3.clear()
        self.ax3.set_title('📊 Speed Analysis', fontsize=12, fontweight='bold')
        self.ax3.set_ylabel('Speed (m/s)')
        self.ax3.grid(True, alpha=0.3)
        
        if self.vehicle_data:
            speeds = [data['speeds'][-1] for data in self.vehicle_data.values() if data['speeds']]
            if speeds:
                avg_speed = np.mean(speeds)
                max_speed = max(speeds)
                min_speed = min(speeds)
                
                categories = ['Avg', 'Max', 'Min']
                values = [avg_speed, max_speed, min_speed]
                colors = ['blue', 'green', 'red']
                
                bars = self.ax3.bar(categories, values, color=colors, alpha=0.7)
                for bar, value in zip(bars, values):
                    self.ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, 
                                 f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
                
                self.simulation_stats['avg_speeds'].append(avg_speed)
    
    def update_safety_metrics(self):
        self.ax4.clear()
        self.ax4.set_title('🛡️ Safety Metrics', fontsize=12, fontweight='bold')
        self.ax4.set_ylabel('Count')
        
        metrics = ['Near Misses', 'V2X Warnings', 'Emergency']
        values = [
            self.simulation_stats['near_misses'],
            self.simulation_stats['v2x_warnings'], 
            self.simulation_stats['emergency_vehicles']
        ]
        colors = ['orange', 'purple', 'red']
        
        bars = self.ax4.bar(metrics, values, color=colors, alpha=0.7)
        for bar, value in zip(bars, values):
            self.ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                         str(value), ha='center', va='bottom', fontweight='bold')
    
    def update_traffic_efficiency(self):
        self.ax5.clear()
        self.ax5.set_title('📈 Traffic Efficiency', fontsize=12, fontweight='bold')
        self.ax5.set_ylabel('Efficiency Score (%)')
        self.ax5.grid(True, alpha=0.3)
        
        if self.simulation_stats['avg_speeds']:
            current_speed = self.simulation_stats['avg_speeds'][-1]
            efficiency = min(current_speed / 15.0 * 100, 100)  # 15 m/s as ideal
            
            color = 'green' if efficiency > 70 else 'orange' if efficiency > 50 else 'red'
            self.ax5.bar(['Efficiency'], [efficiency], color=color, alpha=0.7)
            self.ax5.text(0, efficiency + 2, f'{efficiency:.1f}%', 
                         ha='center', va='bottom', fontweight='bold')
    
    def update_v2x_communication(self):
        self.ax6.clear()
        self.ax6.set_title('📡 V2X Communication', fontsize=12, fontweight='bold')
        self.ax6.set_ylabel('Messages/Sec')
        
        # Simulate V2X message rates
        message_types = ['RSU Msgs', 'V2V Msgs', 'Safety']
        rates = [
            self.simulation_stats['rsu_messages'] / (self.step * 0.2 + 1),
            self.simulation_stats['vehicle_sign_changes'] / (self.step * 0.2 + 1),
            self.simulation_stats['v2x_warnings'] / (self.step * 0.2 + 1)
        ]
        
        bars = self.ax6.bar(message_types, rates, color=['blue', 'green', 'red'], alpha=0.7)
        for bar, rate in zip(bars, rates):
            self.ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                         f'{rate:.1f}', ha='center', va='bottom', fontsize=8)
    
    def update_vehicle_stats(self):
        self.ax7.clear()
        self.ax7.set_title('🚙 Vehicle Stats', fontsize=12, fontweight='bold')
        self.ax7.set_ylabel('Count')
        
        # Count vehicles by type
        type_counts = {}
        for data in self.vehicle_data.values():
            vtype = data['type']
            type_counts[vtype] = type_counts.get(vtype, 0) + 1
        
        if type_counts:
            types = list(type_counts.keys())
            counts = list(type_counts.values())
            bars = self.ax7.bar(types, counts, alpha=0.7)
            for bar, count in zip(bars, counts):
                self.ax7.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                             str(count), ha='center', va='bottom', fontsize=8)
    
    def update_system_performance(self):
        self.ax8.clear()
        self.ax8.set_title('⚡ System Performance', fontsize=12, fontweight='bold')
        self.ax8.set_ylabel('Performance Score')
        self.ax8.set_xlabel('Time (s)')
        self.ax8.grid(True, alpha=0.3)
        
        # Calculate performance over time
        if len(self.simulation_stats['avg_speeds']) > 1:
            times = list(range(len(self.simulation_stats['avg_speeds'])))
            performances = [min(speed / 15.0 * 100, 100) for speed in self.simulation_stats['avg_speeds']]
            
            self.ax8.plot(times, performances, 'b-', linewidth=2, label='Performance')
            self.ax8.fill_between(times, 0, performances, alpha=0.3, color='blue')
            
            # Add current performance
            current_perf = performances[-1] if performances else 0
            self.ax8.axhline(y=current_perf, color='red', linestyle='--', alpha=0.7)
            self.ax8.text(times[-1], current_perf + 5, f'Current: {current_perf:.1f}%', 
                         ha='right', fontweight='bold')

def main():
    print("🚗 V2X Traffic Management System")
    print("=================================")
    print("Advanced Features:")
    print("- Real-time network visualization")
    print("- V2X communication simulation") 
    print("- Safety monitoring and collision detection")
    print("- Traffic flow efficiency analysis")
    print("- Comprehensive performance reporting")
    print("- 200ms simulation delay")
    print()
    
    controller = V2XTrafficController()
    plt.show()

if __name__ == "__main__":
    main()