# 🚦 V2X Traffic Management System

A sophisticated V2X-enabled traffic simulation demonstrating intelligent transportation systems with real-time accident prevention and traffic optimization.

## 🚀 Features

- **📡 V2X Communication** - Vehicle-to-Infrastructure real-time data exchange
- **🛡️ Accident Prevention** - AI-powered collision avoidance system  
- **🏢 RSU Infrastructure** - 5 Road Side Units for traffic monitoring
- **📊 Live Analytics** - 8-panel real-time monitoring dashboard
- **⚡ Auto-Reporting** - Comprehensive performance analysis
- **🚗 Multi-Vehicle Types** - Cars, SUVs, Trucks with V2X capabilities
- **🔄 Traffic Optimization** - Adaptive signal control and flow management

## 🛠️ Tech Stack

- **SUMO** - Traffic simulation backend
- **Python 3.8+** - Core programming language
- **Matplotlib** - Real-time visualization
- **TraCI** - Traffic Control Interface

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate road network
python create_network.py

# 3. Run V2X simulation
python v2x_controller_safe.py
```

## 📈 Simulation Output

- **Real-time Dashboard** - Live vehicle tracking & safety monitoring
- **Safety Scoring** - Intelligent accident prevention metrics
- **Performance Reports** - Automated analysis with timestamps
- **Traffic Analytics** - Flow efficiency and V2X communication stats

## 🏗️ Project Structure

```
v2x-traffic-simulation/
├── 🐍 create_network.py     # Network generator
├── 🛣️ routes.rou.xml       # Vehicle configurations  
├── 🎮 v2x_controller_safe.py # Main controller
├── 📋 requirements.txt     # Dependencies
└── 📖 README.md           # Documentation
```

## 🎯 Use Cases

- **Research** - V2X protocols & traffic safety studies
- **Education** - Transportation engineering courses
- **Development** - Smart city infrastructure testing
- **Analysis** - Traffic flow optimization research

## 📄 License

MIT License - Open source for academic and research use.

---

**Ready to simulate?** Run `python v2x_controller_safe.py` and watch intelligent traffic management in action! 🚗💨
