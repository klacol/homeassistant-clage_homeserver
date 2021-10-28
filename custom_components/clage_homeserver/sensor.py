"""Platform for clage_homeserver sensor integration."""
import logging
from homeassistant.const import (
    DEVICE_CLASS_SIGNAL_STRENGTH,
    DEVICE_CLASS_TEMPERATURE,
    PERCENTAGE,
    TEMP_CELSIUS,
    TIME_SECONDS,
    VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
)

from homeassistant import core, config_entries
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    DEVICE_CLASS_ENERGY,
    SensorEntity,
)


from .const import DOMAIN, CONF_HOMESERVERS, CONF_NAME

AMPERE = "A"
VOLT = "V"
POWER_KILO_WATT = "kW"
CARD_ID = "Card ID"
PERCENT = "%"

_LOGGER = logging.getLogger(__name__)

_sensors = {
    "homeserver_version": {
        "unit": None,
        "name": "Homeserver Version",
        "description": "Version der Software und des API des Homeservers",
        "stateClass": STATE_CLASS_MEASUREMENT,
        "deviceClass": None,
    },
    "homeserver_error": {
        "unit": None,
        "name": "Fehlerstatus",
        "description": "Fehlerstatus beim Abfragen des Homeservers",
        "stateClass": STATE_CLASS_MEASUREMENT,
        "deviceClass": None,
    },
    "homeserver_time": {
        "unit": TIME_SECONDS,
        "name": "Uhrzeit",
        "description": "Uhrzeit des Homeservers (UTC)",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "homeserver_success": {
        "unit": None,
        "name": "",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "homeserver_cached": {
        "unit": None,
        "name": "",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_id": {
        "unit": None,
        "name": "Durchlauferhitzer ID",
        "description": "Individual ID of the heater device as shown in the CLAGE Smart Control App",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_busId": {
        "unit": None,
        "name": "Bus ID",
        "description": "Adresse des Durchlauferhitzers auf dem Bus.",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_name": {
        "unit": None,
        "name": "Individueller Name",
        "description": "Individueller Name des Durchlauferhitzers, der bei der Konfiguration vergeben wurde, z.B. 'Warmwasser Bad oben'",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": DEVICE_CLASS_TEMPERATURE,
    },
    "heater_connected": {
        "unit": None,
        "name": "",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": DEVICE_CLASS_TEMPERATURE,
    },
    "heater_signal": {
        "unit": None,
        "name": "",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": DEVICE_CLASS_SIGNAL_STRENGTH,
    },
    "heater_rssi": {
        "unit": SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        "name": "Funksignalstärke",
        "description": "Funksignalstärke des Gerätes am Server (größer => besser)",
        "stateclass": DEVICE_CLASS_SIGNAL_STRENGTH,
        "deviceclass": "",
    },
    "heater_lqi": {
        "unit": TEMP_CELSIUS,
        "name": "Verbindungsqualität",
        "description": "Zahlenwert als Indikator für Verbindungsqualität (kleiner => besser)",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_status_setpoint": {
        "unit": TEMP_CELSIUS,
        "name": "Soll-Auslauftemperatur",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": DEVICE_CLASS_TEMPERATURE,
    },
    "heater_status_tIn": {
        "unit": TEMP_CELSIUS,
        "name": "Einlauftemperatur",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": DEVICE_CLASS_TEMPERATURE,
    },
    "heater_status_tOut": {
        "unit": TEMP_CELSIUS,
        "name": "Auslauftemperatur",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": DEVICE_CLASS_TEMPERATURE,
    },
    "heater_status_tP1": {
        "unit": TEMP_CELSIUS,
        "name": "Temperaturspeicher 1",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": DEVICE_CLASS_TEMPERATURE,
    },
    "heater_status_tP2": {
        "unit": TEMP_CELSIUS,
        "name": "Temperaturspeicher 2",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": DEVICE_CLASS_TEMPERATURE,
    },
    "heater_status_tP3": {
        "unit": TEMP_CELSIUS,
        "name": "Temperaturspeicher 3",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": DEVICE_CLASS_TEMPERATURE,
    },
    "heater_status_tP4": {
        "unit": TEMP_CELSIUS,
        "name": "Temperaturspeicher 4",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": DEVICE_CLASS_TEMPERATURE,
    },
    "heater_status_flow": {
        "unit": VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
        "name": "Aktuelle Durchflussmenge",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_status_flowMax": {
        "unit": VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
        "name": "Maximale Durchflussmenge",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_status_valvePos": {
        "unit": PERCENTAGE,
        "name": "Ventilposition",
        "description": "Stellposition des elektrischen Ventils (0 = Zu, 100 = Offen)",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": "",
    },
    "heater_status_valveFlags": {
        "unit": PERCENTAGE,
        "name": "",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": "",
    },
    "heater_status_power": {
        "unit": POWER_KILO_WATT,
        "name": "Leistungsaufnahme",
        "description": "Aktuelle Leistungsaufnahme des Durchlauferhitzers",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": "",
    },
    "heater_status_powermax": {
        "unit": POWER_KILO_WATT,
        "name": "Leistungsaufnahme max.",
        "description": "Höchstwert der Leistungsaufnahme des Durchlauferhitzers",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": "",
    },
    "heater_status_power100": {
        "unit": POWER_KILO_WATT,
        "name": "",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": "",
    },
    "heater_status_error": {
        "unit": None,
        "name": "",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
}


def _create_sensors_for_homeserver(homeserverName, hass):
    entities = []
    for sensor in _sensors:
        _LOGGER.debug(f"Adding Sensor: {sensor} for homeserver {homeserverName}")
        entities.append(
            ClageHomeserverSensor(
                hass.data[DOMAIN]["coordinator"],
                f"sensor.clagehomeserver_{homeserverName}_{sensor}",
                homeserverName,
                _sensors.get(sensor).get("name"),
                sensor,
                _sensors.get(sensor).get("unit"),
                _sensors.get(sensor).get("stateClass"),
                _sensors.get(sensor).get("deviceClass"),
            )
        )
    return entities


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    _LOGGER.debug("setup sensors...")
    config = config_entry.as_dict()["data"]

    homeserverName = config[CONF_NAME]

    _LOGGER.debug(f"homeserver name: '{homeserverName}'")
    async_add_entities(_create_sensors_for_homeserver(homeserverName, hass))


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up clage homeserver Sensor platform."""
    _LOGGER.debug("setup_platform")
    if discovery_info is None:
        return

    homeservers = discovery_info[CONF_HOMESERVERS]

    entities = []
    for homeserver in homeservers:
        homeserverName = homeserver[0][CONF_NAME]
        _LOGGER.debug(f"homeserver name: '{homeserverName}'")
        entities.extend(_create_sensors_for_homeserver(homeserverName, hass))

    async_add_entities(entities)


class ClageHomeserverSensor(CoordinatorEntity, SensorEntity):
    def __init__(
        self,
        coordinator,
        entity_id,
        homeserverName,
        name,
        attribute,
        unit,
        stateClass,
        deviceClass,
    ):
        """Initialize the clage homeserver sensor."""

        super().__init__(coordinator)
        self.homeservername = homeserverName
        self.entity_id = entity_id
        self._name = name
        self._attribute = attribute
        self._unit = unit
        self._attr_state_class = stateClass
        self._attr_device_class = deviceClass

    @property
    def device_info(self):
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.homeservername)
            },
            "name": self.homeservername,
            "manufacturer": "Clage",
            "model": "HOMESERVER",
        }

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique_id of the sensor."""
        return f"{self.homeservername}_{self._attribute}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self.homeservername][self._attribute]

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit
