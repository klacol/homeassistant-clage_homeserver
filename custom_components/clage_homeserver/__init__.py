"""clage_homeserver integration"""
import voluptuous as vol
import ipaddress
import logging
from datetime import timedelta
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import valid_entity_id
from homeassistant import core
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, CONF_SERIAL, CONF_CHARGERS, CONF_NAME, HOMESERVER_API
from clage_homeserver import ClageHomeServer

_LOGGER = logging.getLogger(__name__)

TEMPERATURE = "heater_temperature"
HEATER_ID_ATTR = "heater id"

MIN_UPDATE_INTERVAL = timedelta(seconds=10)
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=20)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_CHARGERS, default=[]): vol.All([
                    cv.ensure_list, [
                        vol.All({
                            vol.Required(CONF_NAME): vol.All(cv.string),
                            vol.Required(CONF_HOST): vol.All(ipaddress.ip_address, cv.string),
                        })
                    ]
                ]),
                vol.Optional(CONF_HOST): vol.All(ipaddress.ip_address, cv.string),
                vol.Optional(CONF_SERIAL): vol.All(cv.string),
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                ): vol.All(cv.time_period, vol.Clamp(min=MIN_UPDATE_INTERVAL)),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup_entry(hass, config):
    _LOGGER.debug("async_Setup_entry")
    _LOGGER.debug(repr(config.data))

    name = config.data[CONF_NAME]
    clageHomeServer = ClageHomeServer(config.data[CONF_HOMESERVER_IP_ADDRESS],config.data[CONF_HOMESERVER_ID],config.data[CONF_HEATER_ID])
    hass.data[DOMAIN]["api"][name] = clageHomeServer

    await hass.data[DOMAIN]["coordinator"].async_refresh()

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config, "sensor")
    )
    return True


async def async_unload_entry(hass, entry):
    _LOGGER.debug(f"Unloading homeserver '{entry.data[CONF_NAME]}")
    hass.data[DOMAIN]["api"].pop(entry.data[CONF_NAME])
    return True


class ChargerStateFetcher:
    def __init__(self, hass):
        self._hass = hass

    async def fetch_states(self):
        _LOGGER.debug('Updating status...')
        homeservers = self._hass.data[DOMAIN]["api"]
        data = self.coordinator.data if self.coordinator.data else {}
        for homeserverId in homeservers.keys():
            _LOGGER.debug(f"update for '{homeserverId}'..")
            fetchedStatus = await self._hass.async_add_executor_job(homeservers[homeserverId].requestStatus)
            if fetchedStatus.get("car_status", "unknown") != "unknown":
                data[homeserverId] = fetchedStatus
            else:
                _LOGGER.error(f"Unable to fetch state for Charger {homeserverId}")
        return data


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up clage_homeserver platforms and services."""

    _LOGGER.debug("async_setup")
    scan_interval = DEFAULT_UPDATE_INTERVAL

    hass.data[DOMAIN] = {}
    chargerApi = {}
    homeservers = []
    if DOMAIN in config:
        scan_interval = config[DOMAIN].get(CONF_SCAN_INTERVAL, DEFAULT_UPDATE_INTERVAL)

        ipAddress = config[DOMAIN].get(CONF_HOMESERVER_IP_ADDRESS, False)
        homeserverId = config[DOMAIN].get(CONF_HOMESERVER_ID, "unknown")
        heaterId = config[DOMAIN].get(CONF_HEATER_ID, "unknown")

        clageHomeServer = ClageHomeServer(ipAddress,homeserverId,heaterId) 

        if ipAddress:
            if not ipAddress:
                clageHomeServer = ClageHomeServer(host)
                status = clageHomeServer.requestStatus()
                serial = status["serial_number"]
            homeservers.append([{CONF_NAME: serial, CONF_HOST: host}])
        _LOGGER.debug(repr(homeservers))

        for homeserver in homeservers:
            ipAddress = homeserver[0][CONF_HOMESERVER_IP_ADDRESS]
            homeserverId = homeserver[0][CONF_HOMESERVER_ID]
            heaterId = homeserver[0][CONF_HEATER_ID]
            _LOGGER.debug(f"ipAddress: '{ipAddress}' homeserverId: '{homeserverId}' heaterId: '{heaterId}'")

            clageHomeServer = ClageHomeServer(ipAddress,homeserverId,heaterId)
            chargerApi[homeserverId] = clageHomeServer

    hass.data[DOMAIN]["api"] = chargerApi

    chargeStateFecher = ChargerStateFetcher(hass)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=chargeStateFecher.fetch_states,
        update_interval=scan_interval,
    )
    chargeStateFecher.coordinator = coordinator

    hass.data[DOMAIN]["coordinator"] = coordinator

    await coordinator.async_refresh()

    async def async_handle_set_temperature(call):
        """Handle the service call to set the temperature of the heater."""
        heaterIdInput = call.data.get(HEATER_ID_ATTR, '')

        temperatureInput = call.data.get(
            SET_TEMPERATURE, 32  # TODO: dynamic based on chargers absolute_max-setting
        )
        temperature = 0
        if isinstance(temperatureInput, str):
            if temperatureInput.isnumeric():
                temperature = int(temperatureInput)
            elif valid_entity_id(temperatureInput):
                temperature = int(hass.states.get(temperatureInput).state)
            else:
                _LOGGER.error(
                    "No valid value for '%s': %s", SET_TEMPERATURE, temperature
                )
                return
        else:
            temperature = temperatureInput

        if temperature < 10:
            temperature = 10
        if temperature > 60:
            temperature = 60

        if len(homeserverIdInput) > 0:
            _LOGGER.debug(f"set max_current for charger '{homeserverIdInput}' to {temperature}")
            try:
                await hass.async_add_executor_job(hass.data[DOMAIN]["api"][homeserverIdInput].setTemperature, temperature)
            except KeyError:
                _LOGGER.error(f"Charger with name '{homeserverIdInput}' not found!")

        else:
            for charger in hass.data[DOMAIN]["api"].keys():
                try:
                    _LOGGER.debug(f"set_temperature for heater '{charger}' to {temperature}")
                    await hass.async_add_executor_job(hass.data[DOMAIN]["api"][charger].setTemperature, temperature)
                except KeyError:
                    _LOGGER.error(f"Charger with name '{chargerName}' not found!")

        await hass.data[DOMAIN]["coordinator"].async_refresh()

    hass.services.async_register(DOMAIN, "set_temperature", async_handle_set_temperature)

    hass.async_create_task(async_load_platform(
        hass, "sensor", DOMAIN, {CONF_CHARGERS: chargers, CHARGER_API: chargerApi}, config)
    )

    return True
