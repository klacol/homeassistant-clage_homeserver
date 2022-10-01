"""Platform for clage_homeserver sensor integration."""
import logging
from .sensor_definition import SensorDefinition
from homeassistant import core, config_entries
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntity,
)

from homeassistant.const import (
    CURRENCY_CENT,
    ENERGY_KILO_WATT_HOUR,
    PERCENTAGE,
    TEMP_CELSIUS,
    TIME_HOURS,
    TIME_MINUTES,
    TIME_SECONDS,
    VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    VOLUME_LITERS,
)

from homeassistant.const import (
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_TIMESTAMP,
)

from homeassistant.helpers.entity import EntityCategory

from .const import (
    DOMAIN,
    CONF_HOMESERVERS,
    CONF_NAME,
    CONF_HOMESERVER_IP_ADDRESS,
    CONF_HOMESERVER_ID,
    CONF_HEATER_ID,
)

AMPERE = "A"
VOLT = "V"
POWER_KILO_WATT = "kW"
PERCENT = "%"

_LOGGER = logging.getLogger(__name__)

_sensors = [
    SensorDefinition(
        system_name="homeserver_version",
        name="Homeserver Version",
        definition="Version der Software und des API des Homeservers",
        unit=None,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTICT,
    ),
    SensorDefinition(
        system_name="homeserver_error",
        name="Fehlerstatus",
        definition="Fehlerstatus beim Abfragen des Homeservers",
        unit=None,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTICT,
    ),
    SensorDefinition(
        system_name="homeserver_time",
        name="Uhrzeit (UTC)",
        definition="Uhrzeit des Homeservers in der UTC-Zeitzone (+00:00 Greenwich)",
        unit=None,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTICT,
    ),
    SensorDefinition(
        system_name="homeserver_success",
        name="Erfolgsstatus API",
        definition="",
        unit=None,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTICT,
    ),
    SensorDefinition(
        system_name="heater_id",
        name="Durchlauferhitzer ID",
        definition="Individuelle ID des Durchlauferhitzers (z.B. CLAGE DSX Touch), so wie in der CLAGE Smart Control App angezeigt",
        unit=None,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.CONFIG,
    ),
    SensorDefinition(
        system_name="heater_busId",
        name="Bus ID",
        definition="Adresse des Durchlauferhitzers auf dem Bus",
        unit=None,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.CONFIG,
    ),
    SensorDefinition(
        system_name="heater_name",
        name="Name",
        definition="Individueller Name des Durchlauferhitzers, der bei der Konfiguration vergeben wurde, z.B. 'Warmwasser Bad oben'",
        unit=None,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.CONFIG,
    ),
    SensorDefinition(
        system_name="heater_connected",
        name="Verbindungsstatus",
        definition="",
        unit=None,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.CONFIG,
    ),
    SensorDefinition(
        system_name="heater_signal",
        name="Signalstatus",
        definition="",
        unit=None,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_SIGNAL_STRENGTH,
        entity_category=EntityCategory.DIAGNOSTICT,
    ),
    SensorDefinition(
        system_name="heater_rssi",
        name="Funksignalstärke",
        definition="Funksignalstärke des Gerätes am Server (größer => besser)",
        unit=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_SIGNAL_STRENGTH,
        entity_category=EntityCategory.DIAGNOSTICT,
    ),
    SensorDefinition(
        system_name="heater_lqi",
        name="Verbindungsqualität",
        definition="Zahlenwert als Indikator für Verbindungsqualität (kleiner => besser)",
        unit=None,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTICT,
    ),
    SensorDefinition(
        system_name="heater_status_setpoint",
        name="Soll-Auslauftemperatur",
        definition="",
        unit=TEMP_CELSIUS,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_TEMPERATURE,
        entity_category=None,
    ),
    SensorDefinition(
        system_name="heater_status_tIn",
        name="Einlauftemperatur",
        definition="Temperatur des kalten Wassers, das in den Durchlauferhitzer reinfließt",
        unit=TEMP_CELSIUS,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_TEMPERATURE,
        entity_category=None,
    ),
    SensorDefinition(
        system_name="heater_status_tOut",
        name="Auslauftemperatur",
        definition="Temperatur des warmen Wassers, das aus dem Durchlauferhitzer rausfließt",
        unit=TEMP_CELSIUS,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_TEMPERATURE,
        entity_category=None,
    ),
    SensorDefinition(
        system_name="heater_status_tP1",
        name="Temperaturspeicher 1",
        definition="Speicherplatz 1 für individuelle Temperatureinstellungen",
        unit=TEMP_CELSIUS,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
    ),
    SensorDefinition(
        system_name="heater_status_tP2",
        name="Temperaturspeicher 2",
        definition="Speicherplatz 2 für individuelle Temperatureinstellungen",
        unit=TEMP_CELSIUS,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
    ),
    SensorDefinition(
        system_name="heater_status_tP3",
        name="Temperaturspeicher 3",
        definition="Speicherplatz 3 für individuelle Temperatureinstellungen",
        unit=TEMP_CELSIUS,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
    ),
    SensorDefinition(
        system_name="heater_status_tP4",
        name="Temperaturspeicher 4",
        definition="Speicherplatz 4 für individuelle Temperatureinstellungen",
        unit=TEMP_CELSIUS,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
    ),
    SensorDefinition(
        system_name="heater_status_flow",
        name="Aktuelle Durchflussmenge",
        definition="",
        unit=VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=None,
    ),
    SensorDefinition(
        system_name="heater_status_flowMax",
        name="Maximale Durchflussmenge",
        definition="",
        unit=VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.CONFIG,
    ),
    SensorDefinition(
        system_name="heater_status_valvePos",
        name="Ventilposition",
        definition="Stellposition des elektrischen Ventils (0 = Zu, 100 = Offen)",
        unit=PERCENTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=None,
    ),
    SensorDefinition(
        system_name="heater_status_valveFlags",
        name="Einstellung Ventil",
        definition="",
        unit=None,
        state_class=None,
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTICT,
    ),
    SensorDefinition(
        system_name="heater_status_power",
        name="Leistungsaufnahme",
        definition="Aktuelle Leistungsaufnahme des Durchlauferhitzers",
        unit=POWER_KILO_WATT,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=None,
    ),
    SensorDefinition(
        system_name="heater_status_powerMax",
        name="Leistungsaufnahme max.",
        definition="Höchstwert der Leistungsaufnahme des Durchlauferhitzers",
        unit=POWER_KILO_WATT,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.CONFIG,
    ),
    SensorDefinition(
        system_name="heater_status_power100",
        name="Maximale Leistung",
        definition="Höchstwert der Leistungsaufnahme des Durchlauferhitzers",
        unit=POWER_KILO_WATT,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.CONFIG,
    ),
    SensorDefinition(
        system_name="heater_status_error",
        name="Fehlerstatus",
        definition="",
        unit=None,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTICT,
    ),
    SensorDefinition(
        system_name="heater_setup_swVersion",
        name="Softwareversion",
        definition="Version der Gerätesoftware",
        unit=None,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTICT,
    ),
    SensorDefinition(
        system_name="heater_setup_serialDevice",
        name="Geräteseriennummer",
        definition="Seriennummer des Gerätes",
        unit=None,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTICT,
    ),
    SensorDefinition(
        system_name="heater_setup_serialPowerUnit",
        name="Leistungsteilsseriennummer",
        definition="Seriennummer des Leistungsteils",
        unit=None,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTICT,
    ),
    SensorDefinition(
        system_name="heater_setup_flowMax",
        name="Durchflussmengenbegrenzung (Liter/Minute)",
        definition="Durchflussmengenbegrenzung 0/255=aus, 253=ECO,254=AUTO",
        unit=VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.CONFIG,
    ),
    SensorDefinition(
        system_name="heater_setup_loadShedding",
        name="Lastabwurf",
        definition="Durchflussmengenbegrenzung 0/255=aus, 253=ECO,254=AUTO",
        unit=None,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.CONFIG,
    ),
    SensorDefinition(
        system_name="heater_setup_scaldProtection",
        name="Verbrühschutztemperatur",
        definition="utztemperatur; 0=aus; entspr. tLimit",
        unit=TEMP_CELSIUS,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
    ),
    SensorDefinition(
        system_name="heater_setup_sound",
        name="Signalton",
        definition="Signalton bei Fehlern",
        unit=None,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.CONFIG,
    ),
    SensorDefinition(
        system_name="heater_setup_fcpAddr",
        name="Adresse",
        definition="Interne Busadresse",
        unit=None,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.CONFIG,
    ),
    SensorDefinition(
        system_name="heater_setup_powerCosts",
        name="Kosten pro kWh (Cent)",
        definition="Interne Busadresse",
        unit=CURRENCY_CENT,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.CONFIG,
    ),
    SensorDefinition(
        system_name="heater_setup_powerMax",
        name="Leistungsaufnahme (max.)",
        definition="Höchstwert der Leistungsaufnahme",
        unit=POWER_KILO_WATT,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.CONFIG,
    ),
    SensorDefinition(
        system_name="heater_setup_calValue",
        name="Interner Kontrollwert",
        definition="",
        unit=None,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTICT,
    ),
    SensorDefinition(
        system_name="heater_setup_timerPowerOn",
        name="Heizdauer",
        definition="",
        unit=TIME_MINUTES,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=None,
        entity_category=None,
    ),
    SensorDefinition(
        system_name="heater_setup_timerLifetime",
        name="Gesamt-Betriebsdauer",
        definition="",
        unit=TIME_HOURS,
        state_class=STATE_CLASS_TOTAL_INCREASING,
        device_class=None,
        entity_category=None,
    ),
    SensorDefinition(
        system_name="heater_setup_timerStandby",
        name="Betriebsdauer seit dem letzten Stromausfall",
        definition="",
        unit=TIME_HOURS,
        state_class=STATE_CLASS_TOTAL_INCREASING,
        device_class=None,
        entity_category=None,
    ),
    # SensorDefinition(
    #     system_name="heater_setup_totalPowerConsumption",
    #     name="Gesamtleistungsaufnahme",
    #     definition="",
    #     unit=ENERGY_KILO_WATT_HOUR,
    #     state_class=STATE_CLASS_TOTAL_INCREASING,
    #     device_class=None,
    #     entity_category=None,
    # ),
    # SensorDefinition(
    #     system_name="heater_setup_totalWaterConsumption",
    #     name="Gesamtwassermenge",
    #     definition="",
    #     unit=VOLUME_LITERS,
    #     state_class=STATE_CLASS_TOTAL_INCREASING,
    #     device_class=None,
    #     entity_category=None,
    # ),
    SensorDefinition(
        system_name="number_of_watertaps",
        name="Anzahl Zapfungen",
        definition="Gesamtanzahl aller Zapfungen seit Inbetriebnahme",
        unit=None,
        state_class=STATE_CLASS_TOTAL_INCREASING,
        device_class=None,
        entity_category=None,
    ),
    SensorDefinition(
        system_name="usage_time",
        name="Gesamt-Nutzungsdauer",
        definition="Gesamte Nutzungsdauer aller Zapfungen seit Inbetriebnahme",
        unit=TIME_MINUTES,
        state_class=STATE_CLASS_TOTAL_INCREASING,
        device_class=None,
        entity_category=None,
    ),
    SensorDefinition(
        system_name="consumption_energy",
        name="Gesamt-Energieverbrauch",
        definition="Gesamter Energieverbrauch aller Zapfungen seit Inbetriebnahme",
        unit=ENERGY_KILO_WATT_HOUR,
        state_class=STATE_CLASS_TOTAL_INCREASING,
        device_class=DEVICE_CLASS_ENERGY,
        entity_category=None,
    ),
    SensorDefinition(
        system_name="consumption_water",
        name="Gesamt-Wasserverbrauch",
        definition="Gesamter Wasserverbrauch aller Zapfungen seit Inbetriebnahme",
        unit=VOLUME_LITERS,
        state_class=STATE_CLASS_TOTAL_INCREASING,
        device_class=None,
        entity_category=None,
    ),
]


def _create_sensors_for_homeserver(
    homeserver_name, homeserver_ip_address, homeserver_id, heater_id, hass
):
    _entities = []
    for _sensor in _sensors:
        _LOGGER.debug("Adding Sensor: %s for homeserver %s", _sensor, homeserver_name)
        _entities.append(
            ClageHomeserverSensor(
                coordinator=hass.data[DOMAIN]["coordinator"],
                entity_id=f"sensor.clagehomeserver_{homeserver_name}_{_sensor.system_name}",
                homeserver_name=homeserver_name,
                homeserver_ip_address=homeserver_ip_address,
                homeserver_id=homeserver_id,
                heater_id=heater_id,
                name=_sensor.name,
                attribute=_sensor.system_name,
                unit=_sensor.unit,
                state_class=_sensor.state_class,
                device_class=_sensor.device_class,
                entity_category=_sensor.entity_category,
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
    async_add_entities(
        _create_sensors_for_homeserver(
            homeserver_name,
            _config[CONF_HOMESERVER_IP_ADDRESS],
            _config[CONF_HOMESERVER_ID],
            _config[CONF_HEATER_ID],
            hass,
        )
    )


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
        entities.extend(
            _create_sensors_for_homeserver(
                homeserver_name,
                homeserver[0][CONF_HOMESERVER_IP_ADDRESS],
                homeserver[0][CONF_HOMESERVER_ID],
                homeserver[0][CONF_HEATER_ID],
                hass,
            )
        )

    async_add_entities(entities)


class ClageHomeserverSensor(CoordinatorEntity, SensorEntity):
    """Management of all sensors of the CLAGE Homeserver."""

    def __init__(
        self,
        coordinator,
        entity_id,
        homeserver_name,
        homeserver_ip_address,
        homeserver_id,
        heater_id,
        name,
        attribute,
        unit,
        state_class,
        device_class,
        entity_category,
    ):
        """Initializes the CLAGE Homeserver sensors."""

        super().__init__(coordinator)
        self.homeservername = homeserver_name
        self.homeserver_ip_address = homeserver_ip_address
        self.homeserver_id = homeserver_id
        self.heater_id = heater_id
        self.entity_id = entity_id
        self._name = name
        self._attribute = attribute
        self._unit = unit
        self._attr_state_class = state_class
        self._attr_device_class = device_class
        if entity_category is not None:
            self._attr_entity_category = entity_category

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.homeservername)},
            "name": self.homeservername,
            "manufacturer": "CLAGE GmbH",
            "model": f"DSX Touch {self.heater_id}@{self.homeserver_id}",
            "configuration_url": f"https://{self.homeserver_ip_address}",
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
