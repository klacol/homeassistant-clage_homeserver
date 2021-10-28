"""Platform for clage_homeserver sensor integration."""
import logging
from homeassistant.const import (
    PERCENTAGE,
    TEMP_CELSIUS,
    ENERGY_KILO_WATT_HOUR,
    TIME_SECONDS,
    VOLUME_FLOW_RATE_CUBIC_FEET_PER_MINUTE,
    VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
)

from homeassistant import core, config_entries
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    STATE_CLASS_TOTAL_INCREASING,
    DEVICE_CLASS_ENERGY,
    SensorEntity,
)


from .const import (
    DOMAIN,
    CONF_HOMESERVERS,
    CONF_HOMESERVER_IP_ADDRESS,
    CONF_HOMESERVER_ID,
    CONF_HEATER_ID,
)

AMPERE = "A"
VOLT = "V"
POWER_KILO_WATT = "kW"
CARD_ID = "Card ID"
PERCENT = "%"

_LOGGER = logging.getLogger(__name__)

_sensorUnits = {
    "posixTimestamp": {
        "unit": TIME_SECONDS,
        "name": "Time of the Homeserver in Unix format",
    },
    "homeserver_time": {"unit": TIME_SECONDS, "name": "Time of the Homeserver"},
    "heater_signal": {"unit": TEMP_CELSIUS, "name": ""},
    "heater_rssi": {"unit": TEMP_CELSIUS, "name": ""},
    "heater_lqi": {"unit": TEMP_CELSIUS, "name": ""},
    "heater_status_setpoint": {
        "unit": TEMP_CELSIUS,
        "name": "Temperature of the water",
    },
    "heater_status_tIn": {
        "unit": TEMP_CELSIUS,
        "name": "Temperature of the inbound water (cold)",
    },
    "heater_status_tOut": {
        "unit": TEMP_CELSIUS,
        "name": "Temperature of the outbound water (warm)",
    },
    "heater_status_tP1": {"unit": POWER_KILO_WATT, "name": ""},
    "heater_status_tP2": {"unit": POWER_KILO_WATT, "name": ""},
    "heater_status_tP3": {"unit": POWER_KILO_WATT, "name": ""},
    "heater_status_tP4": {"unit": POWER_KILO_WATT, "name": ""},
    "heater_status_flow": {"unit": VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR, "name": ""},
    "heater_status_flowMax": {
        "unit": VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
        "name": "",
    },
    "heater_status_valvePos": {"unit": PERCENTAGE, "name": "Position of the valve"},
    "heater_status_valveFlags": {"unit": TEMP_CELSIUS, "name": ""},
    "heater_status_power": {"unit": POWER_KILO_WATT, "name": ""},
    "heater_status_powerMax": {"unit": POWER_KILO_WATT, "name": ""},
    "heater_status_power100": {"unit": POWER_KILO_WATT, "name": ""},
    "heater_status_fillingLeft": {
        "unit": TEMP_CELSIUS,
        "name": "Temperature of the water",
    },
}

_sensorStateClass = {"heater_status_power": STATE_CLASS_TOTAL_INCREASING}

_sensorDeviceClass = {
    "heater_status_power": DEVICE_CLASS_ENERGY,
}

_sensors = [
    "homeserver_version",
    "homeserver_error",
    "posixTimestamp",
    "homeserver_time",
    "homeserver_success",
    "homeserver_cached",
    "heater_id",
    "heater_busId",
    "heater_name",
    "heater_connected",
    "heater_signal",
    "heater_rssi",
    "heater_lqi",
    "heater_status",
    "heater_status_setpoint",
    "heater_status_tIn",
    "heater_status_tOut",
    "heater_status_tP1",
    "heater_status_tP2",
    "heater_status_tP3",
    "heater_status_tP4",
    "heater_status_flow",
    "heater_status_flowMax",
    "heater_status_valvePos",
    "heater_status_valveFlags",
    "heater_status_power",
    "heater_status_powerMax",
    "heater_status_power100",
    "heater_status_fillingLeft",
    "heater_status_flags",
    "heater_status_sysFlags",
    "heater_status_error",
]


def _create_sensors_for_homeserver(homeserverName, hass):
    entities = []

    for sensor in _sensors:

        _LOGGER.debug(f"adding Sensor: {sensor} for charger {homeserverName}")
        sensorUnit = (
            _sensorUnits.get(sensor).get("unit") if _sensorUnits.get(sensor) else ""
        )
        sensorName = (
            _sensorUnits.get(sensor).get("name") if _sensorUnits.get(sensor) else sensor
        )
        sensorStateClass = (
            _sensorStateClass[sensor] if sensor in _sensorStateClass else ""
        )
        sensorDeviceClass = (
            _sensorDeviceClass[sensor] if sensor in _sensorDeviceClass else ""
        )
        entities.append(
            ClageHomeserverSensor(
                hass.data[DOMAIN]["coordinator"],
                f"sensor.clagehomeserver_{homeserverName}_{sensor}",
                homeserverName,
                sensorName,
                sensor,
                sensorUnit,
                sensorStateClass,
                sensorDeviceClass,
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

    _LOGGER.debug(f"charger name: '{homeserverName}'")
    async_add_entities(_create_sensors_for_homerserver(homeserverName, hass))


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up go-eCharger Sensor platform."""
    _LOGGER.debug("setup_platform")
    if discovery_info is None:
        return

    homeservers = discovery_info[CONF_HOMESERVERS]

    entities = []
    for homeserver in homeservers:
        homeserverName = homeserver[0][CONF_NAME]
        _LOGGER.debug(f"homeserver id: '{homeserverId}'")
        entities.extend(_create_sensors_for_homeserver(homeserverId, hass))

    async_add_entities(entities)


class HomserverSensor(CoordinatorEntity, SensorEntity):
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
        """Initialize the go-eCharger sensor."""

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
                (DOMAIN, self._homeservername)
            },
            "name": self._homeservername,
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
        return f"{self._chargername}_{self._attribute}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self._chargername][self._attribute]

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit
