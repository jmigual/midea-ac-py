"""Platform for binary sensor integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID, STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

# Local constants
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    add_entities: AddEntitiesCallback,
) -> None:
    """Setup the binary sensor platform for Midea Smart AC."""

    _LOGGER.info("Setting up binary sensor platform.")

    # Get config data from entry
    config = config_entry.data

    # Fetch device from global data
    id = config.get(CONF_ID)
    device = hass.data[DOMAIN][id]

    # Query library support
    if getattr(device, "filter_alert", None) is None:
        _LOGGER.warn("Device does not support 'filter_alert' property.")
    else:
        # Create sensor entities from device
        add_entities([
            MideaBinarySensor(device, "filter_alert"),
        ])


class MideaBinarySensor(BinarySensorEntity, RestoreEntity):
    """Binary sensor for Midea AC."""

    def __init__(self, device, prop):
        self._device = device
        self._prop = prop
        self._on = False

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        if (last_state := await self.async_get_last_state()) is None:
            return

        # Restore previous state
        if last_state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            self._on = last_state.state == STATE_ON

    async def async_update(self) -> None:
        # Grab the property from the device
        if self.available:
            self._on = getattr(self._device, self._prop)

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {
                (DOMAIN, self._device.id)
            },
        }

    @property
    def name(self) -> str:
        return f"{DOMAIN}_{self._prop}_{self._device.id}"

    @property
    def unique_id(self) -> str:
        return f"{self._device.id}-{self._prop}"

    @property
    def available(self) -> bool:
        return self._device.online

    @property
    def is_on(self) -> bool:
        return self._on

    @property
    def device_class(self) -> str:
        return BinarySensorDeviceClass.PROBLEM

    @property
    def entity_category(self) -> str:
        return EntityCategory.DIAGNOSTIC