"""FamilieDosmer integration setup and teardown."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_registry import async_get as get_entity_registry

from .api import FamilieDosmerApi
from .const import (
    COORDINATOR_MEALPLAN,
    COORDINATOR_SHOPPING,
    COORDINATOR_TODO,
    DATA_KEY_API,
    DATA_KEY_FAMILY_ID,
    DOMAIN,
    PLATFORMS,
    SERVICE_ADD_SHOPPING,
    SERVICE_DELETE_SHOPPING,
    SERVICE_LOG_DONE,
    SERVICE_UPDATE_SHOPPING,
    SERVICE_UPDATE_TODO,
)
from .coordinator import MealPlanCoordinator, ShoppingCoordinator, TodoCoordinator

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

_LOGGER = logging.getLogger(__name__)


def _resolve_entity_target(hass: HomeAssistant, entity_ids: list[str]) -> list[tuple[FamilieDosmerApi, str, str]]:
    """Resolve entity_ids to (api, family_id, list_id) tuples.

    list_id is extracted from the entity's unique_id (``familiedosmer_<uuid>``).
    """
    er = get_entity_registry(hass)
    results: list[tuple[FamilieDosmerApi, str, str]] = []
    for entity_id in entity_ids:
        entry = er.async_get(entity_id)
        if entry is None or entry.platform != DOMAIN:
            raise HomeAssistantError(f"Entity {entity_id} is not a FamilieDosmer entity")
        config_entry = hass.config_entries.async_get_entry(entry.config_entry_id)
        if config_entry is None:
            raise HomeAssistantError(f"Config entry not found for {entity_id}")
        api = hass.data[DOMAIN][entry.config_entry_id][DATA_KEY_API]
        family_id = config_entry.data[DATA_KEY_FAMILY_ID]
        list_id = entry.unique_id.removeprefix("familiedosmer_")
        results.append((api, family_id, list_id))
    return results


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Register global services."""

    async def handle_log_done(call: ServiceCall) -> None:
        apis = _resolve_entity_target(hass, call.data["entity_id"])
        for api, family_id, _ in apis:
            await api.create_done_entry(
                family_id,
                call.data["email"],
                call.data["item"],
                call.data.get("details"),
            )

    async def handle_add_shopping(call: ServiceCall) -> None:
        apis = _resolve_entity_target(hass, call.data["entity_id"])
        kwargs: dict[str, Any] = {}
        if call.data.get("quantity") is not None:
            kwargs["quantity"] = call.data["quantity"]
        if call.data.get("unit"):
            kwargs["unit"] = call.data["unit"]
        if call.data.get("category"):
            kwargs["category"] = call.data["category"]
        for api, family_id, list_id in apis:
            await api.add_shopping_item(
                family_id, list_id, call.data["name"], **kwargs
            )

    async def handle_update_shopping(call: ServiceCall) -> None:
        apis = _resolve_entity_target(hass, call.data["entity_id"])
        kwargs: dict[str, Any] = {}
        if call.data.get("checked") is not None:
            kwargs["checked"] = call.data["checked"]
        if call.data.get("name"):
            kwargs["name"] = call.data["name"]
        if call.data.get("quantity") is not None:
            kwargs["quantity"] = call.data["quantity"]
        if call.data.get("unit"):
            kwargs["unit"] = call.data["unit"]
        for api, family_id, list_id in apis:
            await api.update_shopping_item(
                family_id, list_id, call.data["item_id"], **kwargs
            )

    async def handle_delete_shopping(call: ServiceCall) -> None:
        apis = _resolve_entity_target(hass, call.data["entity_id"])
        for api, family_id, list_id in apis:
            await api.delete_shopping_item(
                family_id, list_id, call.data["item_id"]
            )

    async def handle_update_todo(call: ServiceCall) -> None:
        apis = _resolve_entity_target(hass, call.data["entity_id"])
        for api, family_id, list_id in apis:
            await api.update_todo_item(
                family_id,
                list_id,
                call.data["item_id"],
                completed=call.data.get("completed", True),
            )

    hass.services.async_register(
        DOMAIN,
        SERVICE_LOG_DONE,
        handle_log_done,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_ids,
            vol.Required("email"): str,
            vol.Required("item"): str,
            vol.Optional("details"): str,
        }),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_SHOPPING,
        handle_add_shopping,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_ids,
            vol.Required("name"): str,
            vol.Optional("quantity"): vol.Any(int, float),
            vol.Optional("unit"): str,
            vol.Optional("category"): str,
        }),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_SHOPPING,
        handle_update_shopping,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_ids,
            vol.Required("item_id"): str,
            vol.Optional("checked"): bool,
            vol.Optional("name"): str,
            vol.Optional("quantity"): vol.Any(int, float),
            vol.Optional("unit"): str,
        }),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE_SHOPPING,
        handle_delete_shopping,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_ids,
            vol.Required("item_id"): str,
        }),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_TODO,
        handle_update_todo,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_ids,
            vol.Required("item_id"): str,
            vol.Optional("completed", default=True): bool,
        }),
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    api = FamilieDosmerApi(session, entry.data["token"])

    family_id = entry.data[DATA_KEY_FAMILY_ID]

    coordinator_shopping = ShoppingCoordinator(hass, api, family_id)
    coordinator_todo = TodoCoordinator(hass, api, family_id)
    coordinator_mealplan = MealPlanCoordinator(hass, api, family_id)

    for coord in (coordinator_shopping, coordinator_todo, coordinator_mealplan):
        await coord.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        DATA_KEY_API: api,
        COORDINATOR_SHOPPING: coordinator_shopping,
        COORDINATOR_TODO: coordinator_todo,
        COORDINATOR_MEALPLAN: coordinator_mealplan,
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
