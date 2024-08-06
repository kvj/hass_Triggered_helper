from __future__ import annotations
from .constants import DOMAIN, PLATFORMS
from .coordinator import Coordinator, Platform

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
# from homeassistant.helpers import service

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
import logging

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
    }, extra=vol.ALLOW_EXTRA),
}, extra=vol.ALLOW_EXTRA)

async def _async_update_entry(hass, entry):
    _LOGGER.debug(f"_async_update_entry: {entry}")
    coordinator = hass.data[DOMAIN]["devices"][entry.entry_id]
    await coordinator.async_unload()
    await coordinator.async_load()

async def async_setup_entry(hass: HomeAssistant, entry):
    _LOGGER.debug(f"async_setup_entry: {entry}")
    data = entry.as_dict()["data"]

    platform = hass.data[DOMAIN]["platform"]
    coordinator = Coordinator(platform, entry)
    hass.data[DOMAIN]["devices"][entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_update_entry))
    await coordinator.async_config_entry_first_refresh()
    await coordinator.async_load()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry):
    _LOGGER.debug(f"async_unload_entry: {entry}")
    coordinator = hass.data[DOMAIN]["devices"][entry.entry_id]
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    await coordinator.async_unload()
    hass.data[DOMAIN]["devices"].pop(entry.entry_id)
    return True


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    platform = Platform(hass)
    await platform.async_load()
    hass.data[DOMAIN] = {"devices": {}, "platform": platform}
    return True
