
# Home Assistant NextEnergy Battery Modbus Integration

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

- SoC
- Generation
- Consumption
- Grid
- Battery Charging
- Battery Discharging
- Grid Export
- Grid Import
- Grid Frequency
- Battery Temp
- Inverter Temp
- Today's Generation
- Cumulative Generation
- Today's Load Consumption
- Total Load Consumption
- Today's Grid Export
- Total Grid Export
- Today's Grid Import
- Total Grid Import
- Today's Battery Charge
- Total Battery Charge
- Today's Battery Discharge
- Total Battery Discharge
