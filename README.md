# Home Assistant NextEnergy Battery Modbus Integration

**This project is not endorsed by, directly affiliated with, maintained, authorized, or sponsored by NextEnergy**

This is a custom integration for Home Assistant to monitor NextEnergy batteries via Modbus TCP.

## Installation

### HACS

1. Add this repository as a custom repository in HACS.
2. Search for "NextEnergy Battery" and install the integration.
3. Restart Home Assistant.

### Manual Installation

1. Copy the `custom_components/nextenergy_battery` directory to your Home Assistant configuration directory.
2. Restart Home Assistant.

## Configuration

1. Go to **Configuration** > **Integrations**.
2. Click the **+** button and search for "NextEnergy Battery".
3. Enter the host, port, and slave ID of your battery.

## Sensors

The integration will create the following sensors:

- Model Name
- SN
- Master Version
- Slave Version
- Manager Version
- BMS Connection Status
- BMS Master Version
- BMS Master SN
- BMS Slave Number
- BMS Slave 1 Version
- BMS Slave 1 SN
- BMS Slave 2 Version
- BMS Slave 2 SN
- BMS Slave 3 Version
- BMS Slave 3 SN
- BMS Slave 4 Version
- BMS Slave 4 SN
- BMS Slave 5 Version
- BMS Slave 5 SN
- BMS Voltage
- BMS Current
- BMS Ambient Temp
- BMS SoC
- BMS SOH
- BMS Remain Energy
- Meter Connection Status
- R Phase Voltage
- S Phase Voltage
- T Phase Voltage
- R Phase Current
- S Phase Current
- T Phase Current
- Combined Active Power
- Frequency
- Rated Power (Pn)
- Max Active Power (Pmax)
- Status
- Grid R Voltage
- Grid S Voltage
- Grid T Voltage
- Grid Frequency
- Inverter Temp
- System SoC
- Active Power
- Reactive Power
- Grid Power (Meter)
- EPS Power
- Load Power
- Battery Power
- Load Consumption Today
- Load Consumption Total
- Grid Export Today
- Grid Export Total
- Grid Import Today
- Grid Import Total
- Battery Charge Today
- Battery Charge Total
- Battery Discharge Today
- Battery Discharge Total
- Battery Charging
- Battery Discharging
- Grid Import
- Grid Export

---

![NextEnergy Logo](custom_components/nextenergy_battery/logo.png)