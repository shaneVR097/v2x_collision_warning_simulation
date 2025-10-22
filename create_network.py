import os
import sys
import subprocess
import xml.etree.ElementTree as ET

def create_network_file():
    sumo_home = os.environ.get('SUMO_HOME', '')
    if not sumo_home:
        print("ERROR: SUMO_HOME environment variable not set!")
        return
    
    netgenerate_path = os.path.join(sumo_home, 'bin', 'netgenerate.exe')
    
    # Create a simple but effective network
    command = [
        netgenerate_path,
        '--grid',
        '--grid.number', '3',  # 3x3 grid for good complexity
        '--grid.length', '200',
        '--default.lanenumber', '2',
        '--tls.guess', 'true',
        '--output-file', 'network.net.xml'
    ]
    
    try:
        print("🛣️  Generating road network...")
        subprocess.run(command, check=True, capture_output=True)
        print("✅ Network generated successfully: network.net.xml")
        
        # Now discover the actual network elements
        discover_network_elements()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating network: {e}")
        if e.stderr:
            print(f"STDERR: {e.stderr.decode()}")

def discover_network_elements():
    """Discover all network elements to create proper configuration"""
    print("\n🔍 Discovering Network Elements...")
    
    try:
        # Parse the generated network file
        tree = ET.parse('network.net.xml')
        root = tree.getroot()
        
        print("\n📋 NETWORK DISCOVERY REPORT:")
        print("="*50)
        
        # Discover edges
        edges = root.findall('.//edge')
        print(f"\n🛣️  EDGES FOUND ({len(edges)}):")
        edge_ids = []
        for edge in edges:
            edge_id = edge.get('id')
            if edge_id and not edge_id.startswith(':'):  # Skip internal edges
                edge_ids.append(edge_id)
                print(f"   • {edge_id}")
        
        # Discover lanes for each edge
        print(f"\n🚗 LANES FOUND:")
        lane_data = {}
        for edge in edges:
            edge_id = edge.get('id')
            if edge_id and not edge_id.startswith(':'):
                lanes = edge.findall('.//lane')
                lane_ids = [lane.get('id') for lane in lanes if lane.get('id')]
                lane_data[edge_id] = lane_ids
                if lane_ids:
                    print(f"   • {edge_id}: {', '.join(lane_ids)}")
        
        # Discover traffic lights
        tls = root.findall('.//tlLogic')
        print(f"\n🚦 TRAFFIC LIGHTS FOUND ({len(tls)}):")
        for tl in tls:
            tl_id = tl.get('id')
            print(f"   • {tl_id}")
        
        # Discover junctions
        junctions = root.findall('.//junction')
        print(f"\n📍 JUNCTIONS FOUND ({len(junctions)}):")
        junction_ids = []
        for junction in junctions:
            j_id = junction.get('id')
            j_type = junction.get('type')
            if j_type != 'internal':
                junction_ids.append(j_id)
                print(f"   • {j_id} (type: {j_type})")
        
        # Save discovery results to file
        save_discovery_results(edge_ids, lane_data, junction_ids, tls)
        
        print(f"\n✅ Discovery complete! Check 'network_discovery.txt' for details.")
        
    except Exception as e:
        print(f"❌ Error during network discovery: {e}")

def save_discovery_results(edge_ids, lane_data, junction_ids, tls):
    """Save discovered network elements to a file"""
    with open('network_discovery.txt', 'w') as f:
        f.write("SUMO NETWORK DISCOVERY REPORT\n")
        f.write("="*50 + "\n\n")
        
        f.write("EDGES:\n")
        f.write("-" * 20 + "\n")
        for edge_id in edge_ids:
            f.write(f"{edge_id}\n")
        
        f.write("\nLANES:\n")
        f.write("-" * 20 + "\n")
        for edge_id, lanes in lane_data.items():
            f.write(f"{edge_id}:\n")
            for lane in lanes:
                f.write(f"  - {lane}\n")
        
        f.write("\nTRAFFIC LIGHTS:\n")
        f.write("-" * 20 + "\n")
        for tl in tls:
            f.write(f"{tl.get('id')}\n")
        
        f.write("\nJUNCTIONS:\n")
        f.write("-" * 20 + "\n")
        for junction in junction_ids:
            f.write(f"{junction}\n")
        
        f.write("\nUSAGE EXAMPLES:\n")
        f.write("-" * 20 + "\n")
        f.write("For routes.rou.xml:\n")
        if edge_ids:
            f.write(f'<route id="route1" edges="{edge_ids[0]} {edge_ids[1]} {edge_ids[2]}"/>\n\n')
        
        f.write("For additional files:\n")
        if lane_data:
            first_edge = list(lane_data.keys())[0]
            if lane_data[first_edge]:
                f.write(f'<inductionLoop id="detector1" lane="{lane_data[first_edge][0]}" pos="50"/>\n')

def generate_simple_config():
    """Generate a simple working configuration based on discovery"""
    print("\n🛠️  Generating simple working configuration...")
    
    try:
        # Read discovery results
        with open('network_discovery.txt', 'r') as f:
            content = f.read()
        
        # Extract edge IDs
        edges_section = False
        edge_ids = []
        for line in content.split('\n'):
            if line.strip() == "EDGES:":
                edges_section = True
                continue
            elif line.strip().startswith("-") and edges_section:
                edges_section = False
                continue
            elif edges_section and line.strip() and not line.startswith(" "):
                edge_ids.append(line.strip())
        
        # Generate simple routes using discovered edges
        if len(edge_ids) >= 4:
            generate_simple_routes(edge_ids[:4])
            generate_simple_additional()
            generate_simple_config_file()
            
            print("✅ Simple configuration generated!")
            print("   - routes.rou.xml (with valid edges)")
            print("   - additional.add.xml (with valid lanes)")
            print("   - simulation.sumocfg")
        else:
            print("❌ Not enough edges discovered for route generation")
            
    except Exception as e:
        print(f"❌ Error generating configuration: {e}")

def generate_simple_routes(edge_ids):
    """Generate simple routes using discovered edges"""
    routes_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="4.3" minGap="2.5" maxSpeed="55" color="1,0,0"/>
    <vType id="suv" accel="2.3" decel="4.0" sigma="0.5" length="5.0" minGap="3.0" maxSpeed="50" color="0,1,0"/>
    
    <!-- Simple routes using discovered edges -->
    <route id="route1" edges="{edge_ids[0]} {edge_ids[1]}"/>
    <route id="route2" edges="{edge_ids[1]} {edge_ids[2]}"/>
    <route id="route3" edges="{edge_ids[2]} {edge_ids[3]}"/>
    <route id="route4" edges="{edge_ids[3]} {edge_ids[0]}"/>
    
    <!-- 8 vehicles -->
    <vehicle id="veh0" type="car" route="route1" depart="0"/>
    <vehicle id="veh1" type="suv" route="route2" depart="2"/>
    <vehicle id="veh2" type="car" route="route3" depart="4"/>
    <vehicle id="veh3" type="suv" route="route4" depart="6"/>
    <vehicle id="veh4" type="car" route="route1" depart="8"/>
    <vehicle id="veh5" type="suv" route="route2" depart="10"/>
    <vehicle id="veh6" type="car" route="route3" depart="12"/>
    <vehicle id="veh7" type="suv" route="route4" depart="14"/>
</routes>'''
    
    with open('routes.rou.xml', 'w') as f:
        f.write(routes_content)

def generate_simple_additional():
    """Generate simple additional file without specific lane references"""
    additional_content = '''<?xml version="1.0" encoding="UTF-8"?>
<additional>
    <!-- Simple RSU points without lane dependencies -->
    <poi id="rsu_central" type="rsu" color="0,1,0" x="300" y="300" width="10"/>
    <poi id="rsu_north" type="rsu" color="0,1,0" x="300" y="500" width="10"/>
    <poi id="rsu_south" type="rsu" color="0,1,0" x="300" y="100" width="10"/>
    
    <!-- Traffic light visualization -->
    <tlLogic id="cluster_0" type="static" programID="0" offset="0">
        <phase duration="31" state="GGGrrrGGGrrr"/>
        <phase duration="6" state="yyyrrryyyrrr"/>
        <phase duration="31" state="rrrGGGrrrGGG"/>
        <phase duration="6" state="rrryyyrrryyy"/>
    </tlLogic>
</additional>'''
    
    with open('additional.add.xml', 'w') as f:
        f.write(additional_content)

def generate_simple_config_file():
    """Generate simulation configuration file"""
    config_content = '''<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="network.net.xml"/>
        <route-files value="routes.rou.xml"/>
        <additional-files value="additional.add.xml"/>
    </input>
    
    <time>
        <begin value="0"/>
        <end value="1000"/>
    </time>
    
    <processing>
        <step-length value="0.2"/>
    </processing>
    
    <report>
        <no-step-log value="true"/>
    </report>
    
    <gui_only>
        <start value="true"/>
        <delay value="200"/>
    </gui_only>
</configuration>'''
    
    with open('simulation.sumocfg', 'w') as f:
        f.write(config_content)

if __name__ == "__main__":
    print("🚦 SUMO Network Generator & Discovery Tool")
    print("="*50)
    create_network_file()
    
    # Ask if user wants to generate simple config
    response = input("\nGenerate simple working configuration? (y/n): ")
    if response.lower() == 'y':
        generate_simple_config()
        print("\n🎉 Setup complete! You can now run the simulation.")
        print("   Run: python test_simulation.py")
    else:
        print("\n📋 Check 'network_discovery.txt' for network details.")
        print("   Create your configuration files using the discovered elements.")