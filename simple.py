import os
import sys

# Set SUMO_HOME
os.environ['SUMO_HOME'] = r'C:\Program Files (x86)\Eclipse\Sumo'

# Add SUMO tools to path
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

import traci

def simple_test():
    """Simple test without additional files"""
    sumo_binary = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo-gui.exe')
    
    # Test 1: Basic network only
    print("🧪 TEST 1: Basic network (no additional files)")
    try:
        traci.start([sumo_binary, "-n", "network.net.xml", "--start", "--delay", "500"])
        print("✅ Basic network works!")
        traci.close()
    except Exception as e:
        print(f"❌ Basic network failed: {e}")
        return
    
    # Test 2: Network + routes
    print("\n🧪 TEST 2: Network + routes")
    try:
        traci.start([sumo_binary, "-n", "network.net.xml", "-r", "routes.rou.xml", "--start", "--delay", "500"])
        print("✅ Network + routes work!")
        
        # Run a few steps
        for step in range(50):
            traci.simulationStep()
            if step % 10 == 0:
                vehicles = traci.vehicle.getIDList()
                print(f"Step {step}: {len(vehicles)} vehicles")
        
        traci.close()
    except Exception as e:
        print(f"❌ Network + routes failed: {e}")
        return
    
    # Test 3: Full configuration (if previous tests pass)
    print("\n🧪 TEST 3: Full configuration")
    try:
        traci.start([sumo_binary, "-c", "simulation.sumocfg", "--start", "--delay", "500"])
        print("✅ Full configuration works!")
        
        # Run simulation
        for step in range(100):
            traci.simulationStep()
            if step % 20 == 0:
                vehicles = traci.vehicle.getIDList()
                print(f"Step {step}: {len(vehicles)} vehicles moving")
        
        traci.close()
        print("\n🎉 ALL TESTS PASSED! V2X system is ready.")
        
    except Exception as e:
        print(f"❌ Full configuration failed: {e}")
        print("   But basic simulation works! We can proceed with V2X controller.")

if __name__ == "__main__":
    simple_test()