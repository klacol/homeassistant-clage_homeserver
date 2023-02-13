# Home Assistant integration for the water heater CLAGE DSX Touch connected through a Clage Homeserver

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![Validate with hassfest](https://github.com/klacol/homeassistant-clage_homeserver/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/klacol/homeassistant-clage_homeserver/actions/workflows/hassfest.yaml)

Integration for Homeassistant to view and Control the Clage Homeserver for continuous electric waterheaters via the local ip-interface via API Version 1.4.

## Features
- Register in Home Assistant in the UI based configuration flow (no yaml)
- Show sensor values from the heater
- Change the water temperature of the heater
- No cloud connection needed to control the heater - only local ip-access needed.

# Warning: WIP - Work in progress
This is an early version of the Integration (custom component).
It uses the Python module [clage_homeserver](https://pypi.org/project/clage-homeserver/) to connect to the REST API of the heater.



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

- Install the integration and use the config flow in the frontent

# Example Config

## `configuration.yaml`

```yaml
input_number:
  clage_homeserver_temperature:
    name: Soll-Temperatur
    min: 0
    max: 60
    initial: 45
    step: 1
    unit_of_measurement: °C
```

## `automations.yaml`

```yaml
- id: '38237023328'
  alias: 'clage_homeserver: set temperature based on input'
  description: ''
  trigger:
  - entity_id: input_number.clage_homeserver_temperature
    platform: state
  condition: []
  action:
  - data_template:
      homeserver_name: durchlauferhitzer_keller
      heater_id: 2049DB0CD7
      temperature: '{{ states(''input_number.clage_homeserver_temperature'') }}'
    service: clage_homeserver.set_temperature
- id: '38237023329'
  alias: 'clage_homeserver: set temperature input based on heater'
  description: ''
  trigger:
  - entity_id: sensor.clagehomeserver_durchlauferhitzer_keller_heater_status_setpoint
    platform: state
  condition: []
  action:
  - data_template:
      entity_id: input_number.clage_homeserver_temperature
      value: '{{ states.sensor.clagehomeserver_durchlauferhitzer_keller_heater_status_setpoint.state }}'
    service: input_number.set_value
```
