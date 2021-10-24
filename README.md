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

* setup your Homeserver in the `configuration.yaml`:

```yaml
clage_homeserver:
  host: <ip of your homeserver>
  name: <id of your homeserver>
  heater:
    - name: <ip of your heater>
```

<!-- # Sample View
![screenshot of Home Assistant](doc/ha_entity_view.png) -->