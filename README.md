[![release][release-badge]][release-url]
![downloads][downloads-badge]

[![hacs][hacs-badge]][hacs-url]
![license][lic-badge]
[![buymecoffeebadge]][buymecoffeeurl]

# Home Assistant NextEnergy Battery Modbus Integration

This is a custom integration for Home Assistant to monitor the [NextEnergy Plug-in battery](https://www.nextenergy.nl/smart-home/plug-in-batterij) (in Dutch) via Modbus TCP.

The battery has Modbus TCP (port 502) enabled on the WiFi and LAN interface, and is used by this integration to communicate with the battery.

The battery is a Fox ESS MQ2200-M-AC and the expansion batteries are Fox ESS MQ2200-M-S.

Currently implements Fox ESS Modbus registers from [`FoxESS Modbus Protocol--20250115 (V1.05.03.00)(1).pdf`](https://github.com/wimb0/home-assistant-nextenergy-battery-modbus/blob/main/FoxESS%20Modbus%20Protocol--20250115%20(V1.05.03.00)(1).pdf).

![NextEnergy Battery Master Unit](https://github.com/wimb0/home-assistant-nextenergy-battery-modbus/blob/main/images/nextenergy_battery/Plug-in_Master-small.png)

## Compatibility ⚠️

This integration has been tested and is known to work with the following firmware versions:
- **Inverter (INV):** `2.010`
- **Battery Management System (BMS):** `1.007`

**Please note:** This integration is confirmed **not** to be working with BMS version `1.000`, as modbus port 502 is not enabled.

## Installation ⚙️

This integration is available in the Home Assistant Community Store [HACS][hacs].

Use this link to directly go to the repository in HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=wimb0&repository=home-assistant-nextenergy-battery-modbus)

_or_

1.  **Install HACS:** If you don't have HACS installed, follow the [installation instructions](https://hacs.xyz/docs/setup/download).
2.  **Add Integration:**
    * Open HACS in Home Assistant.
    * Go to "Integrations".
    * Click the three dots in the top right and select "Custom repositories".
    * Add the repository URL: `https://github.com/wimb0/home-assistant-nextenergy-battery-modbus` and select the "Integration" category.
    * Search for "NextEnergy Battery" and click "Install".
3.  **Restart Home Assistant:** After installation, you must restart Home Assistant.

_or_

1.  **Manual:** Copy the `custom_components/nextenergy_battery` directory to your Home Assistant `custom_components` directory.
2.  Restart Home Assistant.

## Configuration 🛠️

1.  Go to **Settings** > **Devices & Services**.
2.  Click **+ Add Integration** and search for "NextEnergy Battery".
3.  Enter the Host IP, Port, and Modbus Slave ID of your battery.
4.  (Optional) Enter a prefix for the sensor names. The default is `nextenergy`.

After installation, you can change the Host, Port, Slave ID and Polling Interval by clicking **Configure** on the integration card.

## Sensors 🧩

The integration creates a device with a number of sensors to monitor your battery system. The entity IDs of the sensors will be prefixed with the value you provided during configuration (e.g. `sensor.nextenergy_system_soc`). Many non-critical sensors are disabled by default but can be enabled from the device page.

#### Key Metrics (Enabled by Default)
- **System SoC:** Overall State of Charge of the system.
- **BMS SoC:** State of Charge of the Battery Management System.
- **Battery Power:** Current power flow of the battery (positive is charging, negative is discharging).
- **Load Power:** Current power consumption of your house.
- **Grid Power (Meter):** Current power flow from/to the grid (positive is import, negative is export).

#### Derived Power Sensors (Enabled by Default)
These sensors provide a more granular view of power flow.
- **Battery Charging**
- **Battery Discharging**
- **Grid Import**
- **Grid Export**

#### Energy Statistics (Enabled by Default)
- **Battery Charge (Today/Total)**
- **Battery Discharge (Today/Total)**
- **Grid Export (Today/Total)**
- **Grid Import (Today/Total)**

#### Status & Alarms (Enabled by Default)
- **Work Mode:** The current operational mode of the battery (e.g., Self-Use, Force Charge).
- **Inverter Status 1 & 3:** Human-readable status of the inverter (e.g., Operation, Fault, On-grid).
- **Alarm Status 1, 2 & 3:** Human-readable alarm messages if the system is in a fault state.
- **Power Factor:** The efficiency of the power exchange with the grid.

#### BMS & Inverter Details (Enabled by Default)
- **BMS SOH** (State of Health)
- **BMS Ambient Temp**
- **Inverter Temp**
- **Grid Frequency**

#### Disabled by Default
The following sensors are disabled by default and can be enabled manually if needed:
- **Device Information:** Model Name, Serial Numbers, and all firmware versions.
- **BMS Slave Devices:** Version and Serial Number for all 5 slave slots.
- **Connection Status:** Raw status codes for the BMS and meter.
- **Grid Phase Details:** Individual voltage and current for all three phases (R/S/T).
- **Power Ratings:** Rated Power, Max Active Power.
- **Other Power Metrics:** Reactive Power, EPS Power.
- **Detailed BMS Health:** Max/Min cell voltage and temperature.
- **Capacity Info:** Full Charge Capacity (FCC) and Design Energy.
- **System States:** Raw status for System Power, Battery Power, and Network.
- **Total Load Power:** Cumulative lifetime energy consumed by the load.

## Troubleshooting 🐛

If you encounter any issues with the integration, there are two main ways to gather more information to help diagnose the problem.

### Enabling Debug Logging

For detailed logs, you can enable debug logging for this integration by adding the following to your `configuration.yaml` file:

```yaml
logger:
  default: info
  logs:
    custom_components.nextenery_battery: debug
```

After adding this, restart Home Assistant. The logs can be found in **Settings > System > Logs**.

### Downloading Diagnostics

You can download diagnostic data directly from Home Assistant. This data provides information about the inverter and the integration's status.

1.  Navigate to **Settings > Devices & Services**.
2.  Find the **NextEnergy Battery* integration and click on the device.
3.  Click the three-dot menu on the device card and select **Download diagnostics**.

This will download a text file with diagnostic information that you can share when creating a bug report.

---

## Disclaimer

**This project is not endorsed by, directly affiliated with, maintained, authorized, or sponsored by NextEnergy.**

[![NextEnergy Logo](https://github.com/wimb0/home-assistant-nextenergy-battery-modbus/blob/main/images/nextenergy_battery/logo.png)](https://www.nextenergy.nl)

![NextEnergy Battery Master Unit](https://github.com/wimb0/home-assistant-nextenergy-battery-modbus/blob/main/images/nextenergy_battery/Plug-in_Master-small.png)
![NextEnergy Battery Slave Unit](https://github.com/wimb0/home-assistant-nextenergy-battery-modbus/blob/main/images/nextenergy_battery/Plug-in_Uitbreiding-small.png)

[hacs-url]: https://github.com/hacs/integration
[hacs-badge]: https://img.shields.io/badge/hacs-default-orange.svg?style=for-the-badge
[release-badge]: https://img.shields.io/github/v/release/wimb0/home-assistant-nextenergy-battery-modbus?style=for-the-badge
[downloads-badge]: https://img.shields.io/github/downloads/wimb0/home-assistant-nextenergy-battery-modbus/total?style=for-the-badge
[active-badge]: https://badge.t-haber.de/badge/nextenergy_battery?kill_cache=1
[lic-badge]: https://img.shields.io/github/license/wimb0/home-assistant-nextenergy-battery-modbus?style=for-the-badge
[buymecoffeeurl]: https://www.buymeacoffee.com/wimbo
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[home-assistant]: https://www.home-assistant.io/
[hacs]: https://hacs.xyz
[release-url]: https://github.com/wimb0/home-assistant-nextenergy-battery-modbus/releases
