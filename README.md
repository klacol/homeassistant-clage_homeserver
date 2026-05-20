# Home Assistant integration for the water heater CLAGE DSX Touch connected through a Clage Homeserver

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![Validate with hassfest](https://github.com/klacol/homeassistant-clage_homeserver/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/klacol/homeassistant-clage_homeserver/actions/workflows/hassfest.yaml)

Integration for Homeassistant to view and Control the Clage Homeserver for continuous electric waterheaters via the local ip-interface via API Version 1.4.

## Features
- Register in Home Assistant in the UI based configuration flow (no yaml)
- Show sensor values from the heater
- Change the water temperature of the heater
- Change connection settings (IP address, password) after setup via Options
- No cloud connection needed to control the heater - only local ip-access needed.

# Installation

## Option 1: Install it through HACS (recommended)
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=klacol&repository=homeassistant-clage_homeserver&category=integration)

## Option 2: Install it manually

- Clone this repository
```
git clone https://github.com/klacol/homeassistant-clage_homeserver.git
```
- Copy the content of the `custom_components`-Folder to the `custom_components` folder of your home-assistant installation

```
# mkdir -p <your-ha-config-dir>/custom_components
# cp -r custom_components/clage_homeserver <your-ha-config-dir>/custom_components
```

- Restart Home Assistant
- Go to Settings → Devices & Services → Add Integration → search for "CLAGE Homeserver"

# Configuration

## Setup via UI

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **CLAGE Homeserver**
3. Enter:
   - **Name**: A name for your homeserver (e.g. `dsx_server_keller`)
   - **IP Address**: The local IP of the homeserver (e.g. `192.168.0.78`)
   - **Homeserver ID**: Found in CLAGE Smart-Control App under Settings/Devices/DSX Server/Server ID
   - **Heater ID**: Found in CLAGE Smart-Control App under Settings/Devices/DSX Touch/Device ID
   - **Password**: The app password (default: `smart`)

## Changing Settings After Setup

Go to **Settings → Devices & Services → CLAGE Homeserver → Configure** to change the IP address, IDs, or password without removing the integration.

# Setting the Temperature

## Via Developer Tools (Actions)

1. Go to **Developer Tools → Actions**
2. Search for `clage_homeserver.set_temperature`
3. Fill in:
   - **homeserver_name**: The name you gave during setup (slugified, e.g. `dsx_server_keller`)
   - **heater_id**: Your heater device ID (e.g. `2016FFEE22`)
   - **temperature**: Target temperature in °C (20-60)

## Via Automation

```yaml
automation:
  - alias: "Set water heater temperature from input"
    trigger:
      - platform: state
        entity_id: input_number.clage_homeserver_temperature
    action:
      - action: clage_homeserver.set_temperature
        data:
          homeserver_name: "dsx_server_keller"
          heater_id: "2016FFEE22"
          temperature: "{{ states('input_number.clage_homeserver_temperature') | int }}"
```

### Helper for temperature slider

Add this to your `configuration.yaml`:

```yaml
input_number:
  clage_homeserver_temperature:
    name: Soll-Temperatur
    min: 20
    max: 60
    initial: 45
    step: 1
    unit_of_measurement: °C
```
