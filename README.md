# Home Assistant integration for the Clage Homeserver (WIP)

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![Validate with hassfest](https://github.com/klacol/homeassistant-clage_homeserver/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/klacol/homeassistant-clage_homeserver/actions/workflows/hassfest.yaml)

Integration for Homeassistant to view and Control the Clage Homeserver for electric waterheaters via the local ip-interface via API Version 1.4.

## Features
- attributes from heater available as sensors
- change the water temperature of the heater
- no cloud connection needed to control the heater - only local ip-access needed.

# Warning: WIP - Work in progress
This is an early test version of the Integration; it does not work yet!

# Installation

- clone this repository
```
git clone https://github.com/klacol/homeassistant-clage_homeserver.git
```
- copy the content of the `custom_components`-Folder to the `custom_components` folder of your home-assistant installation

```
# mkdir -p <your-ha-config-dir>/custom_components
# cp -r custom_components/clage_homeserver <your-ha-config-dir>/custom_components
```

# Example Config

## `configuration.yaml`

```yaml
clage_homeserver:
  homeservers:
    - name: Durchlauferhitzer Keller
      ipAddress: 192.168.0.78
      homeserverId: F8F005DB0CD7
      heaterId: 2049DB0CD7
```

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



<!-- # Sample View
![screenshot of Home Assistant](doc/ha_entity_view.png) -->