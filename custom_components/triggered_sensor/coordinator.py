from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import storage, trigger

from .constants import (
    DOMAIN,
    CONF_ON_TRIGGERS,
    CONF_OFF_TRIGGERS,
)

import logging
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

class Platform():

    def __init__(self, hass):
        self.hass = hass
        self._storage = storage.Store(hass, 1, DOMAIN)

    async def async_load(self):
        data_ = await self._storage.async_load()
        _LOGGER.debug(f"async_load(): Loaded stored data: {data_}")
        self._storage_data = data_ if data_ else {}

    def get_data(self, key: str, def_={}):
        if key in self._storage_data:
            return self._storage_data[key]
        return def_

    async def async_put_data(self, key: str, data):
        if data:
            self._storage_data = {
                **self._storage_data,
                key: data,
            }
        else:
            if key in self._storage_data:
                del self._storage_data[key]
        await self._storage.async_save(self._storage_data)


class Coordinator(DataUpdateCoordinator):

    def __init__(self, platform, entry):
        super().__init__(
            platform.hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self._async_update,
        )
        self._platform = platform
        self._entry = entry
        self._entry_id = entry.entry_id

        self._config = entry.as_dict()["options"]

    async def _async_update(self):
        return self._platform.get_data(self._entry_id)

    async def _async_update_state(self, data: dict):
        self.async_set_updated_data({
            **self.data,
            **data,
        })
        await self._platform.async_put_data(self._entry_id, self.data)

    async def async_load(self):
        _LOGGER.debug(f"async_load: {self._config}")
        self._remove_on_triggers = await trigger.async_initialize_triggers(
            self.hass, 
            self._config.get(CONF_ON_TRIGGERS, []),
            self._async_on_on_condition,
            domain=DOMAIN,
            name="triggered_sensor_on_trigger",
            log_cb=_LOGGER.log,
        )
        self._remove_off_triggers = await trigger.async_initialize_triggers(
            self.hass, 
            self._config.get(CONF_OFF_TRIGGERS, []),
            self._async_on_off_condition,
            domain=DOMAIN,
            name="triggered_sensor_off_trigger",
            log_cb=_LOGGER.log,
        )

    async def async_unload(self):
        _LOGGER.debug(f"async_unload:")
        if self._remove_on_triggers:
            self._remove_on_triggers()
        if self._remove_off_triggers:
            self._remove_off_triggers()

    async def _async_on_on_condition(self, vars, ctx):
        _LOGGER.debug(f"_async_on_on_condition: {vars}, {ctx}")
        await self._async_update_state({
            "binary_sensor": True,
        })

    async def _async_on_off_condition(self, vars, ctx):
        _LOGGER.debug(f"_async_on_off_condition: {vars}, {ctx}")
        await self._async_update_state({
            "binary_sensor": False,
        })

class BaseEntity(CoordinatorEntity):

    def __init__(self, coordinator: Coordinator):
        super().__init__(coordinator)

    def with_name(self, id: str, name: str):
        self._attr_has_entity_name = True
        self._attr_unique_id = f"triggered_{self.coordinator._entry_id}_{id}"
        self._attr_name = name
        return self
