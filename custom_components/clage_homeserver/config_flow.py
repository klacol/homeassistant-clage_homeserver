"""Module for management the configuration while the setup of the integration"""
from __future__ import annotations
import logging
from datetime import timedelta

from typing import Any

from requests.exceptions import ConnectTimeout, HTTPError
import clage_homeserver
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.util import slugify

from .const import (
    DOMAIN,
    CONF_HOMESERVER_IP_ADDRESS,
    CONF_HOMESERVER_ID,
    CONF_HEATER_ID,
    CONF_NAME,
)

_LOGGER = logging.getLogger(__name__)


DEFAULT_UPDATE_INTERVAL = timedelta(seconds=20)
MIN_UPDATE_INTERVAL = timedelta(seconds=10)


@callback
def clage_homeserver_entries(hass: HomeAssistant):
    """Return the site_ids for the domain."""

    _LOGGER.debug("clage_homeserver_entries")
    return {
        (entry.data[CONF_HOMESERVER_IP_ADDRESS])
        for entry in hass.config_entries.async_entries(DOMAIN)
    }


class Clage_HomeserverConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for clage_homeserver setup."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._errors = {}

    def _ip_address_in_configuration_exists(self, ip_address: str) -> bool:
        """Return True if ip_address exists in configuration."""
        return ip_address in clage_homeserver_entries(self.hass)

    def _homeserver_id_in_configuration_exists(self, homeserver_id: str) -> bool:
        """Return True if homeserver_id exists in configuration."""
        return homeserver_id in clage_homeserver_entries(self.hass)

    def _heater_id_in_configuration_exists(self, heater_id: str) -> bool:
        """Return True if heater_id exists in configuration."""
        return heater_id in clage_homeserver_entries(self.hass)

    def _check_ip_address(
        self, ip_address: str, homeserver_id: str, heater_id: str
    ) -> bool:
        """Check if we can connect to the soleredge api service."""
        api = clage_homeserver.ClageHomeServer(
            ipAddress=ip_address, homeserverId=homeserver_id, heaterId=heater_id
        )
        try:
            response = api.requestStatus()
            if response["homeserver_success"] != True:
                self._errors[CONF_HOMESERVER_IP_ADDRESS] = "homeserver_not_active"
                return False
        except (ConnectTimeout, HTTPError):
            self._errors[CONF_HOMESERVER_IP_ADDRESS] = "could_not_connect"
            return False
        except KeyError:
            self._errors[CONF_HOMESERVER_IP_ADDRESS] = "invalid_ip"
            return False
        return True

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step when user initializes a integration."""
        self._errors = {}
        if user_input is not None:
            name = slugify(user_input.get(CONF_NAME))
            if self._ip_address_in_configuration_exists(
                user_input[CONF_HOMESERVER_IP_ADDRESS]
            ):
                self._errors[CONF_HOMESERVER_IP_ADDRESS] = "already_configured"
            else:
                ip_address = user_input[CONF_HOMESERVER_IP_ADDRESS]
                homeserver_id = user_input[CONF_HOMESERVER_ID]
                heater_id = user_input[CONF_HEATER_ID]
                can_connect = await self.hass.async_add_executor_job(
                    self._check_ip_address, ip_address, homeserver_id, heater_id
                )
                if can_connect:
                    return self.async_create_entry(
                        title=name,
                        data={
                            CONF_HOMESERVER_IP_ADDRESS: ip_address,
                            CONF_HOMESERVER_ID: homeserver_id,
                            CONF_HEATER_ID: heater_id,
                        },
                    )

        else:
            user_input = {
                CONF_HOMESERVER_IP_ADDRESS: "",
                CONF_HOMESERVER_ID: "",
                CONF_HEATER_ID: "",
            }
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=user_input.get(CONF_NAME)): str,
                    vol.Required(
                        CONF_HOMESERVER_IP_ADDRESS,
                        default=user_input[CONF_HOMESERVER_IP_ADDRESS],
                    ): str,
                    vol.Required(
                        CONF_HOMESERVER_ID, default=user_input[CONF_HOMESERVER_ID]
                    ): str,
                    vol.Required(
                        CONF_HEATER_ID, default=user_input[CONF_HEATER_ID]
                    ): str,
                }
            ),
            errors=self._errors,
        )
