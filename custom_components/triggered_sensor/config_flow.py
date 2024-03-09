from collections.abc import Mapping
from typing import Any, cast

from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import selector

from homeassistant.const import (
    CONF_NAME,
)

from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
)

from .constants import (
    DOMAIN,
    CONF_OFF_TRIGGERS,
    CONF_ON_TRIGGERS,
)

import voluptuous as vol
import logging

_LOGGER = logging.getLogger(__name__)

OPTIONS_SCHEMA = vol.Schema({
    vol.Required(CONF_ON_TRIGGERS, description={"suggested_value": []}): selector.TriggerSelector(),
    vol.Required(CONF_OFF_TRIGGERS, description={"suggested_value": []}): selector.TriggerSelector(),
})

CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): selector.TextSelector(),
}).extend(OPTIONS_SCHEMA.schema)

async def _validate(step, user_input):
    _LOGGER.debug(f"_validate: {user_input}")
    return user_input

CONFIG_FLOW = {
    "user": SchemaFlowFormStep(CONFIG_SCHEMA, _validate),
}

OPTIONS_FLOW = {
    "init": SchemaFlowFormStep(OPTIONS_SCHEMA, _validate),
}

class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config or options flow for Derivative."""

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        return cast(str, options[CONF_NAME])
