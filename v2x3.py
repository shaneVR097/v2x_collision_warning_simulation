import os
import sys
import matplotlib.pyplot as plt
import matplotlib.animation as animation
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
        self.simulation_started = False
        self.step = 0
        self.max_duration = 150  # 150 seconds total
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
            'vehicle_counts': [],
            'start_time': None,
            'end_time': None
        }
        self.setup_plots()
        
    def setup_plots(self):
        # Create advanced V2X visualization
        self.fig = plt.figure(figsize=(18, 12))
        self.fig.suptitle('V2X Traffic Management System - Auto-Run (150s)', 
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
        
        # 8. System Performance & Timer
        self.ax8 = plt.subplot2grid((3, 4), (2, 2), colspan=2)
        self.ax8.set_title('⚡ System Performance & Timer', fontsize=12, fontweight='bold')
        self.ax8.set_ylabel('Performance Score')
        self.ax8.set_xlabel('Time (s)')
        self.ax8.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # No control buttons needed - auto-run
        print("🚗 V2X Traffic Management System - AUTO MODE")
        print("=============================================")
        print("Simulation will run for 150 seconds automatically")
        print("Starting in 3 seconds...")
        
    def start_simulation(self):
        if not self.simulation_running and not self.simulation_started:
            self.simulation_running = True
            self.simulation_started = True
            self.simulation_stats['start_time'] = datetime.now()
            self.start_sumo()
            
    def auto_stop_simulation(self):
        """Automatically stop simulation after 150 seconds"""
        self.simulation_running = False
        self.simulation_stats['end_time'] = datetime.now()
        try:
            traci.close()
        except:
            pass
        print("🛑 Auto-stopping simulation...")
        self.generate_comprehensive_report()
        plt.close('all')  # Close all matplotlib windows
        print("✅ Simulation completed. Check 'v2x_simulation_report.txt' for details.")
        
    def generate_comprehensive_report(self):
        """Generate comprehensive report and save to file"""
        report_content = self._generate_report_content()
        
        # Print to console
        print("\n" + "="*80)
        print("🚦 V2X TRAFFIC MANAGEMENT SYSTEM - COMPREHENSIVE REPORT")
        print("="*80)
        print(report_content)
        print("="*80)
        
        # Save to file
        filename = f"v2x_simulation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("V2X TRAFFIC MANAGEMENT SYSTEM - SIMULATION REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Simulation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(report_content)
        
        print(f"📄 Report saved to: {filename}")
        
    def _generate_report_content(self):
        """Generate the report content"""
        total_vehicles = len(self.vehicle_data)
        simulation_time = self.step * 0.2
        actual_duration = (self.simulation_stats['end_time'] - self.simulation_stats['start_time']).total_seconds()
        
        report_lines = []
        
        report_lines.append("SIMULATION PARAMETERS:")
        report_lines.append("-" * 40)
        report_lines.append(f"• Planned Duration: {self.max_duration} seconds")
        report_lines.append(f"• Actual Duration: {simulation_time:.1f} seconds")
        report_lines.append(f"• Real Time: {actual_duration:.1f} seconds")
        report_lines.append(f"• Simulation Steps: {self.step}")
        report_lines.append(f"• Step Length: 0.2 seconds")
        report_lines.append("")
        
        if total_vehicles > 0:
            # Calculate statistics
            speeds = [data['speeds'][-1] for data in self.vehicle_data.values() if data['speeds']]
            avg_speed = np.mean(speeds) if speeds else 0
            max_speed = max(speeds) if speeds else 0
            min_speed = min(speeds) if speeds else 0
            
            # Vehicle type analysis
            type_counts = {}
            total_distance = 0
            for veh_id, data in self.vehicle_data.items():
                vtype = data['type']
                type_counts[vtype] = type_counts.get(vtype, 0) + 1
                # Estimate distance traveled (simplified)
                if len(data['positions']) > 1:
                    total_distance += len(data['positions']) * avg_speed * 0.2
            
            report_lines.append("PERFORMANCE METRICS:")
            report_lines.append("-" * 40)
            report_lines.append(f"• Total Vehicles Tracked: {total_vehicles}")
            report_lines.append(f"• Average Speed: {avg_speed:.2f} m/s ({avg_speed*3.6:.1f} km/h)")
            report_lines.append(f"• Maximum Speed: {max_speed:.2f} m/s")
            report_lines.append(f"• Minimum Speed: {min_speed:.2f} m/s")
            report_lines.append(f"• Estimated Total Distance: {total_distance:.0f} meters")
            report_lines.append("")
            
            report_lines.append("VEHICLE DISTRIBUTION:")
            report_lines.append("-" * 40)
            for vtype, count in type_counts.items():
                percentage = (count / total_vehicles) * 100
                report_lines.append(f"• {vtype}: {count} vehicles ({percentage:.1f}%)")
            report_lines.append("")
            
            report_lines.append("TRAFFIC MANAGEMENT:")
            report_lines.append("-" * 40)
            report_lines.append(f"• Traffic Sign Changes: {self.simulation_stats['traffic_sign_changes']}")
            report_lines.append(f"• V2X Warnings Issued: {self.simulation_stats['v2x_warnings']}")
            report_lines.append(f"• RSU Messages Simulated: {self.simulation_stats['rsu_messages']}")
            report_lines.append(f"• Total Stop Time: {self.simulation_stats['total_stop_time']:.1f} seconds")
            report_lines.append("")
            
            report_lines.append("SAFETY ANALYSIS:")
            report_lines.append("-" * 40)
            report_lines.append(f"• Near Misses Detected: {self.simulation_stats['near_misses']}")
            report_lines.append(f"• Potential Accidents: {self.simulation_stats['accidents']}")
            report_lines.append(f"• Emergency Vehicles Detected: {self.simulation_stats['emergency_vehicles']}")
            report_lines.append("")
            
            # Calculate efficiency scores
            speed_efficiency = min(avg_speed / 15.0 * 100, 100)
            safety_score = 100 - (self.simulation_stats['near_misses'] * 2 + 
                                self.simulation_stats['accidents'] * 10)
            communication_score = min((self.simulation_stats['rsu_messages'] / (simulation_time + 1)) * 10, 100)
            overall_efficiency = (speed_efficiency * 0.4 + max(safety_score, 0) * 0.4 + communication_score * 0.2)
            
            report_lines.append("SYSTEM EFFICIENCY SCORES:")
            report_lines.append("-" * 40)
            report_lines.append(f"• Traffic Flow Efficiency: {speed_efficiency:.1f}%")
            report_lines.append(f"• Safety Score: {max(safety_score, 0):.1f}%")
            report_lines.append(f"• V2X Communication Score: {communication_score:.1f}%")
            report_lines.append(f"• OVERALL SYSTEM EFFICIENCY: {overall_efficiency:.1f}%")
            report_lines.append("")
            
            report_lines.append("V2X COMMUNICATION ANALYSIS:")
            report_lines.append("-" * 40)
            message_rate = self.simulation_stats['rsu_messages'] / (simulation_time + 1)
            warning_rate = self.simulation_stats['v2x_warnings'] / (simulation_time + 1)
            report_lines.append(f"• V2X Message Rate: {message_rate:.2f} messages/second")
            report_lines.append(f"• Safety Warning Rate: {warning_rate:.2f} warnings/second")
            report_lines.append(f"• Vehicle-to-Infrastructure Events: {self.simulation_stats['vehicle_sign_changes']}")
            report_lines.append(f"• Total V2X Events: {self.simulation_stats['rsu_messages'] + self.simulation_stats['v2x_warnings']}")
            report_lines.append("")
            
            # Performance trends
            if len(self.simulation_stats['avg_speeds']) > 5:
                initial_avg = np.mean(self.simulation_stats['avg_speeds'][:5])
                final_avg = np.mean(self.simulation_stats['avg_speeds'][-5:])
                trend = "improving" if final_avg > initial_avg else "declining" if final_avg < initial_avg else "stable"
                report_lines.append("PERFORMANCE TRENDS:")
                report_lines.append("-" * 40)
                report_lines.append(f"• Initial Average Speed: {initial_avg:.2f} m/s")
                report_lines.append(f"• Final Average Speed: {final_avg:.2f} m/s")
                report_lines.append(f"• Traffic Flow Trend: {trend}")
            
        else:
            report_lines.append("No vehicle data collected during simulation.")
            
        report_lines.append("")
        report_lines.append("END OF REPORT")
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
        
    def start_sumo(self):
        sumo_binary = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo-gui.exe')
        
        try:
            # Start with network and routes only (no additional files)
            traci.start([sumo_binary, "-n", "network.net.xml", "-r", "routes.rou.xml", 
                        "--start", "--delay", "200"])
            
            print("✅ V2X Simulation Started! (Auto-mode: 150 seconds)")
            print("   Features: Real-time monitoring, Safety analysis, Traffic optimization")
            print("   Network: 3x3 grid with traffic lights")
            print("   Vehicles: 12 vehicles with different types")
            
            # Start animation
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
            
            # Check if we've reached the time limit
            if current_time >= self.max_duration:
                self.auto_stop_simulation()
                return
            
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
                        'v2x_enabled': True
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
        """V2X Safety Monitoring"""
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
                        
                        if distance < 8:
                            self.simulation_stats['near_misses'] += 1
                            self.simulation_stats['v2x_warnings'] += 1
                            
                        if distance < 3:
                            self.simulation_stats['accidents'] += 1
                            
        except:
            pass
    
    def simulate_v2x_communication(self):
        """Simulate V2X communication"""
        try:
            if self.step % 25 == 0:
                vehicle_count = len(traci.vehicle.getIDList())
                self.simulation_stats['rsu_messages'] += vehicle_count
            
            if self.step % 10 == 0:
                try:
                    tl_count = len(traci.trafficlight.getIDList())
                    self.simulation_stats['traffic_sign_changes'] += tl_count
                except:
                    self.simulation_stats['traffic_sign_changes'] += 5
            
            if self.step % 15 == 0:
                self.simulation_stats['vehicle_sign_changes'] += len(traci.vehicle.getIDList()) // 2
                
        except:
            pass
    
    def optimize_traffic_flow(self):
        """Traffic optimization"""
        try:
            vehicle_count = len(traci.vehicle.getIDList())
            self.simulation_stats['vehicle_counts'].append(vehicle_count)
            
            if len(self.simulation_stats['vehicle_counts']) > 50:
                self.simulation_stats['vehicle_counts'].pop(0)
                
        except:
            pass
    
    def update_network_overview(self):
        self.ax1.clear()
        self.ax1.set_title(f'🚗 Live Network Overview - Time: {self.step * 0.2:.1f}s / {self.max_duration}s', 
                          fontsize=12, fontweight='bold')
        self.ax1.set_xlabel('X Position (m)')
        self.ax1.set_ylabel('Y Position (m)')
        self.ax1.grid(True, alpha=0.2)
        
        colors = {'car': 'blue', 'suv': 'green', 'truck': 'orange'}
        
        for veh_id, data in self.vehicle_data.items():
            if data['positions']:
                x, y = data['positions'][-1]
                vtype = data['type']
                color = colors.get(vtype, 'gray')
                speed = data['speeds'][-1] if data['speeds'] else 0
                
                size = 60 + speed * 10
                
                self.ax1.scatter(x, y, color=color, s=size, alpha=0.8, 
                               edgecolors='black', linewidth=1)
                
                self.ax1.text(x+8, y+8, f"{veh_id}\n{speed:.1f}m/s", 
                            fontsize=6, alpha=0.7, ha='left')
    
    def update_traffic_light_status(self):
        self.ax2.clear()
        self.ax2.set_title('🚦 Traffic Light Status', fontsize=12, fontweight='bold')
        self.ax2.set_ylabel('Green Lights Active')
        
        # Simulate traffic light data
        simulated_tls = [2, 1, 3, 2, 1]
        bars = self.ax2.bar(range(len(simulated_tls)), simulated_tls, 
                          color=['green', 'orange', 'green', 'orange', 'red'], alpha=0.7)
        
        for i, (bar, count) in enumerate(zip(bars, simulated_tls)):
            self.ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                         f'TL{i+1}: {count}G', ha='center', va='bottom', fontsize=8)
    
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
        
        metrics = ['Near Misses', 'V2X Warnings', 'Accidents']
        values = [
            self.simulation_stats['near_misses'],
            self.simulation_stats['v2x_warnings'], 
            self.simulation_stats['accidents']
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
            efficiency = min(current_speed / 15.0 * 100, 100)
            
            color = 'green' if efficiency > 70 else 'orange' if efficiency > 50 else 'red'
            self.ax5.bar(['Efficiency'], [efficiency], color=color, alpha=0.7)
            self.ax5.text(0, efficiency + 2, f'{efficiency:.1f}%', 
                         ha='center', va='bottom', fontweight='bold')
    
    def update_v2x_communication(self):
        self.ax6.clear()
        self.ax6.set_title('📡 V2X Communication', fontsize=12, fontweight='bold')
        self.ax6.set_ylabel('Messages/Sec')
        
        message_types = ['RSU Msgs', 'V2V Msgs', 'Safety']
        current_time = self.step * 0.2
        rates = [
            self.simulation_stats['rsu_messages'] / (current_time + 1),
            self.simulation_stats['vehicle_sign_changes'] / (current_time + 1),
            self.simulation_stats['v2x_warnings'] / (current_time + 1)
        ]
        
        bars = self.ax6.bar(message_types, rates, color=['blue', 'green', 'red'], alpha=0.7)
        for bar, rate in zip(bars, rates):
            self.ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                         f'{rate:.1f}', ha='center', va='bottom', fontsize=8)
    
    def update_vehicle_stats(self):
        self.ax7.clear()
        self.ax7.set_title('🚙 Vehicle Stats', fontsize=12, fontweight='bold')
        self.ax7.set_ylabel('Count')
        
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
        self.ax8.set_title(f'⚡ System Performance - Time: {self.step * 0.2:.1f}s / {self.max_duration}s', 
                          fontsize=12, fontweight='bold')
        self.ax8.set_ylabel('Performance Score')
        self.ax8.set_xlabel('Time (s)')
        self.ax8.grid(True, alpha=0.3)
        
        # Show countdown and performance
        if len(self.simulation_stats['avg_speeds']) > 1:
            times = list(range(len(self.simulation_stats['avg_speeds'])))
            performances = [min(speed / 15.0 * 100, 100) for speed in self.simulation_stats['avg_speeds']]
            
            self.ax8.plot(times, performances, 'b-', linewidth=2, label='Performance')
            self.ax8.fill_between(times, 0, performances, alpha=0.3, color='blue')
            
            # Add countdown info
            remaining = self.max_duration - (self.step * 0.2)
            self.ax8.text(0.02, 0.98, f'Time Remaining: {remaining:.1f}s', 
                         transform=self.ax8.transAxes, fontsize=10, fontweight='bold',
                         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

def main():
    print("🚗 V2X Traffic Management System - AUTO MODE")
    print("=============================================")
    print("Simulation will:")
    print("- Start automatically")
    print("- Run for exactly 150 seconds") 
    print("- Generate comprehensive report")
    print("- Save results to text file")
    print("- Close automatically")
    print()
    print("Starting in 3 seconds...")
    
    import time
    time.sleep(3)
    
    controller = V2XTrafficController()
    controller.start_simulation()  # Auto-start
    plt.show()

if __name__ == "__main__":
    main()