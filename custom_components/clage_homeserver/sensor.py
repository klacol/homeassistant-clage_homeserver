"""Platform for clage_homeserver sensor integration."""
import logging
from homeassistant.const import (
    CURRENCY_CENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_TIMESTAMP,
    ENERGY_KILO_WATT_HOUR,
    PERCENTAGE,
    TEMP_CELSIUS,
    TIME_SECONDS,
    VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    VOLUME_LITERS,
)

from homeassistant import core, config_entries
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
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
        "unit": None,
        "name": "Uhrzeit (UTC)",
        "description": "Uhrzeit des Homeservers in der UTC-Zeitzone (+00:00 Greenwich)",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": DEVICE_CLASS_TIMESTAMP,
    },
    "homeserver_success": {
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
        "description": "Speicherplatz 1 für individuelle Temperatureinstellungen",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": DEVICE_CLASS_TEMPERATURE,
    },
    "heater_status_tP2": {
        "unit": TEMP_CELSIUS,
        "name": "Temperaturspeicher 2",
        "description": "Speicherplatz 2 für individuelle Temperatureinstellungen",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": DEVICE_CLASS_TEMPERATURE,
    },
    "heater_status_tP3": {
        "unit": TEMP_CELSIUS,
        "name": "Temperaturspeicher 3",
        "description": "Speicherplatz 3 für individuelle Temperatureinstellungen",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": DEVICE_CLASS_TEMPERATURE,
    },
    "heater_status_tP4": {
        "unit": TEMP_CELSIUS,
        "name": "Temperaturspeicher 4",
        "description": "Speicherplatz 4 für individuelle Temperatureinstellungen",
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
    "heater_status_powerMax": {
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
    "heater_status_error": {
        "unit": None,
        "name": "",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_setup_swVersion": {
        "unit": None,
        "name": "Softwareversion",
        "description": "Version der Gerätesoftware",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_setup_serialDevice": {
        "unit": None,
        "name": "Gerätseriennummer",
        "description": "Seriennummer des Gerätes",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_setup_serialPowerUnit": {
        "unit": None,
        "name": "Leistungsteilsseriennummer",
        "description": "Seriennummer des Leistungsteils",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_setup_flowMax": {
        "unit": VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
        "name": "Durchflussmengenbegrenzung (Liter/Minute)",
        "description": "Durchflussmengenbegrenzung 0/255=aus, 253=ECO,254=AUTO",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_setup_loadShedding": {
        "unit": None,
        "name": "Lastabwurf",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_setup_scaldProtection": {
        "unit": None,
        "name": "Verbrühschutztemperatur",
        "description": "Verbrühschutztemperatur; 0=aus; entspr. tLimit",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_setup_sound": {
        "unit": None,
        "name": "Signalton",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_setup_fcpAddr": {
        "unit": None,
        "name": "Adresse",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_setup_powerCosts": {
        "unit": CURRENCY_CENT,
        "name": "Kosten pro kWh (Cent)",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_setup_powerMax": {
        "unit": POWER_KILO_WATT,
        "name": "Leistungsaufnahme (max.)",
        "description": "Höchstwert der Leistungsaufnahme",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_setup_calValue": {
        "unit": None,
        "name": "Interner Kontrollwert",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_setup_timerPowerOn": {
        "unit": TIME_SECONDS,
        "name": "Heizdauer",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_setup_timerLifetime": {
        "unit": TIME_SECONDS,
        "name": "Gesamtbetriebsdauer",
        "description": "",
        "stateclass": STATE_CLASS_TOTAL_INCREASING,
        "deviceclass": None,
    },
    "heater_setup_timerStandby": {
        "unit": TIME_SECONDS,
        "name": "Betriebsdauer seit dem letzten Stromausfall",
        "description": "",
        "stateclass": STATE_CLASS_MEASUREMENT,
        "deviceclass": None,
    },
    "heater_setup_totalPowerConsumption": {
        "unit": ENERGY_KILO_WATT_HOUR,
        "name": "Gesamtleistungsaufnahme",
        "description": "",
        "stateclass": STATE_CLASS_TOTAL_INCREASING,
        "deviceclass": None,
    },
    "heater_setup_totalWaterConsumption": {
        "unit": VOLUME_LITERS,
        "name": "Gesamtwassermenge",
        "description": "",
        "stateclass": STATE_CLASS_TOTAL_INCREASING,
        "deviceclass": None,
    },
    "number_of_watertaps": {
        "unit": None,
        "name": "Anzahl Zapfungen",
        "description": "Gesamtanzahl aller Zapfungen seit Inbetriebnahme",
        "stateclass": STATE_CLASS_TOTAL_INCREASING,
        "deviceclass": None,
    },
    "usage_time": {
        "unit": TIME_SECONDS,
        "name": "Gesamt-Nutzungsdauer",
        "description": "Gesamte Nutzungsdauer aller Zapfungen seit Inbetriebnahme",
        "stateclass": STATE_CLASS_TOTAL_INCREASING,
        "deviceclass": None,
    },
    "consumption_energy": {
        "unit": ENERGY_KILO_WATT_HOUR,
        "name": "Gesamt-Energieverbrauch",
        "description": "Gesamter Energieverbrauch aller Zapfungen seit Inbetriebnahme",
        "stateclass": STATE_CLASS_TOTAL_INCREASING,
        "deviceclass": DEVICE_CLASS_ENERGY,
    },
    "consumption_water": {
        "unit": VOLUME_LITERS,
        "name": "Gesamt-Wasserverbrauch",
        "description": "Gesamter Wasserverbrauch aller Zapfungen seit Inbetriebnahme",
        "stateclass": STATE_CLASS_TOTAL_INCREASING,
        "deviceclass": None,
    },
}


def _create_sensors_for_homeserver(homeserver_name, hass):
    _entities = []
    for _sensor in _sensors:
        _LOGGER.debug("Adding Sensor: %s for homeserver %s", _sensor, homeserver_name)
        sensor_name = _sensors.get(_sensor).get("name", "")
        sensor_attribute = _sensor
        sensor_unit = _sensors.get(_sensor).get("unit", "")
        sensor_state_class = _sensors.get(_sensor).get("stateclass")
        sensor_device_class = _sensors.get(_sensor).get("deviceClass")
        _entities.append(
            ClageHomeserverSensor(
                coordinator=hass.data[DOMAIN]["coordinator"],
                entity_id=f"sensor.clagehomeserver_{homeserver_name}_{_sensor}",
                homeserverName=homeserver_name,
                name=sensor_name,
                attribute=sensor_attribute,
                unit=sensor_unit,
                stateClass=sensor_state_class,
                deviceClass=sensor_device_class,
            )
        )
    return _entities


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Set up CLAGE homeserver Sensor platform."""

    _LOGGER.debug("Setup sensors")
    _config = config_entry.as_dict()["data"]

    homeserver_name = _config[CONF_NAME]

    _LOGGER.debug("homeserver name: %s", homeserver_name)
    async_add_entities(_create_sensors_for_homeserver(homeserver_name, hass))


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up CLAGE Homeserver sensor platform."""
    _LOGGER.debug("setup_platform")
    if discovery_info is None:
        return

    homeservers = discovery_info[CONF_HOMESERVERS]

    entities = []
    for homeserver in homeservers:
        homeserver_name = homeserver[0][CONF_NAME]
        _LOGGER.debug("homeserver name: %s", homeserver_name)
        entities.extend(_create_sensors_for_homeserver(homeserver_name, hass))

    async_add_entities(entities)


class ClageHomeserverSensor(CoordinatorEntity, SensorEntity):
    """Management of all sensors of the CLAGE Homeserver."""

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
        """Initializes the CLAGE Homeserver sensors."""

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
