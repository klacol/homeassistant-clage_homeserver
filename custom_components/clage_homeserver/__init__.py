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

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_HOMESERVERS,
    CONF_HOMESERVER_IP_ADDRESS,
    CONF_HOMESERVER_ID,
    CONF_HEATER_ID,
    HOMESERVER_API,
)

from clage_homeserver import ClageHomeServer

_LOGGER = logging.getLogger(__name__)

HEATER_TEMPERATURE = "heater_temperature"
HEATER_ID_ATTR = "heater id"

MIN_UPDATE_INTERVAL = timedelta(seconds=10)
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=20)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_HOMESERVERS, default=[]): vol.All(
                    [
                        cv.ensure_list,
                        [
                            vol.All(
                                {
                                    vol.Required(CONF_NAME): vol.All(cv.string),
                                    vol.Required(CONF_HOMESERVER_IP_ADDRESS): vol.All(
                                        ipaddress.ip_address, cv.string
                                    ),
                                }
                            )
                        ],
                    ]
                ),
                vol.Optional(CONF_HOMESERVER_IP_ADDRESS): vol.All(
                    ipaddress.ip_address, cv.string
                ),
                vol.Optional(CONF_HOMESERVER_ID): vol.All(cv.string),
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                ): vol.All(cv.time_period, vol.Clamp(min=MIN_UPDATE_INTERVAL)),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup_entry(hass, config):
    _LOGGER.debug("async_Setup_entry for clage_homeserver component")
    _LOGGER.debug(repr(config.data))

    name = config.data[CONF_NAME]
    clageHomeServer = ClageHomeServer(
        config.data[CONF_HOMESERVER_IP_ADDRESS],
        config.data[CONF_HOMESERVER_ID],
        config.data[CONF_HEATER_ID],
    )
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


class HomeserverStateFetcher:
    def __init__(self, hass):
        self._hass = hass

    async def fetch_states(self):
        _LOGGER.debug("Updating status...")
        homeservers = self._hass.data[DOMAIN]["api"]
        data = self.coordinator.data if self.coordinator.data else {}
        for homeserverId in homeservers.keys():
            _LOGGER.debug(f"update for '{homeserverId}'..")
            fetchedStatus = await self._hass.async_add_executor_job(
                homeservers[homeserverId].requestStatus
            )
            if fetchedStatus.get("homeserver_status", "unknown") != "unknown":
                data[homeserverId] = fetchedStatus
            else:
                _LOGGER.error(f"Unable to fetch state for Homeserver {homeserverId}")
        return data


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up clage_homeserver platforms and services."""

    _LOGGER.debug("clage_homeserver: async_setup")
    scan_interval = DEFAULT_UPDATE_INTERVAL

    hass.data[DOMAIN] = {}
    homeserverApi = {}
    homeservers = []
    if DOMAIN in config:
        scan_interval = config[DOMAIN].get(CONF_SCAN_INTERVAL, DEFAULT_UPDATE_INTERVAL)

        ipAddress = config[DOMAIN].get(CONF_HOMESERVER_IP_ADDRESS, False)
        homeserverId = config[DOMAIN].get(CONF_HOMESERVER_ID, "unknown")
        heaterId = config[DOMAIN].get(CONF_HEATER_ID, "unknown")

        clageHomeServer = ClageHomeServer(ipAddress, homeserverId, heaterId)

        if ipAddress:
            if not ipAddress:
                clageHomeServer = ClageHomeServer(ipAddress, homeserverId, heaterId)
                status = clageHomeServer.requestStatus()
                serial = status["serial_number"]
            homeservers.append(
                [{CONF_NAME: serial, CONF_HOMESERVER_IP_ADDRESS: ipAddress}]
            )
        _LOGGER.debug(repr(homeservers))

        for homeserver in homeservers:
            ipAddress = homeserver[0][CONF_HOMESERVER_IP_ADDRESS]
            homeserverId = homeserver[0][CONF_HOMESERVER_ID]
            heaterId = homeserver[0][CONF_HEATER_ID]
            _LOGGER.debug(
                f"ipAddress: '{ipAddress}' homeserverId: '{homeserverId}' heaterId: '{heaterId}'"
            )

            clageHomeServer = ClageHomeServer(ipAddress, homeserverId, heaterId)
            homeserverApi[homeserverId] = clageHomeServer

    hass.data[DOMAIN]["api"] = homeserverApi

    homeserverStateFecher = HomeserverStateFetcher(hass)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=homeserverStateFecher.fetch_states,
        update_interval=scan_interval,
    )
    homeserverStateFecher.coordinator = coordinator

    hass.data[DOMAIN]["coordinator"] = coordinator

    await coordinator.async_refresh()

    async def async_handle_set_temperature(call):
        """Handle the service call to set the temperature of the heater."""
        heaterIdInput = call.data.get(HEATER_ID_ATTR, "")

        temperatureInput = call.data.get(
            HEATER_TEMPERATURE,
            32,
        )
        temperature = 0
        if isinstance(temperatureInput, str):
            if temperatureInput.isnumeric():
                temperature = int(temperatureInput)
            elif valid_entity_id(temperatureInput):
                temperature = int(hass.states.get(temperatureInput).state)
            else:
                _LOGGER.error(
                    "No valid value for '%s': %s", HEATER_TEMPERATURE, temperature
                )
                return
        else:
            temperature = temperatureInput

        if temperature < 10:
            temperature = 10
        if temperature > 60:
            temperature = 60

        if len(heaterIdInput) > 0:
            _LOGGER.debug(
                f"set heater_temperature for homeserver/heater '{heaterIdInput}' to {temperature}"
            )
            try:
                await hass.async_add_executor_job(
                    hass.data[DOMAIN]["api"][heaterIdInput].setTemperature,
                    temperature,
                )
            except KeyError:
                _LOGGER.error(f"Heater with id '{heaterIdInput}' not found!")

        else:
            for homeserver in hass.data[DOMAIN]["api"].keys():
                try:
                    _LOGGER.debug(
                        f"set_temperature for heater '{homeserver}' to {temperature}"
                    )
                    await hass.async_add_executor_job(
                        hass.data[DOMAIN]["api"][homeserver].setTemperature, temperature
                    )
                except KeyError:
                    _LOGGER.error(f"Heater with id '{heaterIdInput}' not found!")

        await hass.data[DOMAIN]["coordinator"].async_refresh()

    hass.services.async_register(
        DOMAIN, "set_temperature", async_handle_set_temperature
    )

    hass.async_create_task(
        async_load_platform(
            hass,
            "sensor",
            DOMAIN,
            {CONF_HOMESERVERS: homeservers, HOMESERVER_API: homeserverApi},
            config,
        )
    )

    return True
