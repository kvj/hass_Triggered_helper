from homeassistant.components import binary_sensor
from homeassistant.helpers.entity import EntityCategory

from .coordinator import BaseEntity
from .constants import DOMAIN

import logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_setup_entities):
    coordinator = hass.data[DOMAIN]["devices"][entry.entry_id]
    async_setup_entities([_Sensor(coordinator)])

class _Sensor(BaseEntity, binary_sensor.BinarySensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"binary_sensor", coordinator._config["name"])

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get("binary_sensor")
