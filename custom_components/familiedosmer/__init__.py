"""FamilieDosmer integration setup and teardown."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import FamilieDosmerApi
from .const import (
    COORDINATOR_MEALPLAN,
    COORDINATOR_SHOPPING,
    COORDINATOR_TODO,
    DATA_KEY_API,
    DATA_KEY_COORDINATORS,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import MealPlanCoordinator, ShoppingCoordinator, TodoCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    api = FamilieDosmerApi(session, entry.data["token"])

    coordinators: dict[str, dict[str, object]] = {}
    for family_id in entry.data["family_ids"]:
        coordinators[family_id] = {
            COORDINATOR_SHOPPING: ShoppingCoordinator(hass, api, family_id),
            COORDINATOR_TODO: TodoCoordinator(hass, api, family_id),
            COORDINATOR_MEALPLAN: MealPlanCoordinator(hass, api, family_id),
        }
        for coord in coordinators[family_id].values():
            await coord.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        DATA_KEY_API: api,
        DATA_KEY_COORDINATORS: coordinators,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
