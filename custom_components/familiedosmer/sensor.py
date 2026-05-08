"""Sensor entities for FamilieDosmer shopping and todo list counts."""

from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    COORDINATOR_SHOPPING,
    COORDINATOR_TODO,
    DATA_KEY_FAMILY_ID,
    DOMAIN,
)
from .coordinator import ShoppingCoordinator, TodoCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    family_id = entry.data[DATA_KEY_FAMILY_ID]
    family_name = entry.data.get("family_name", family_id)

    shop_coord: ShoppingCoordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR_SHOPPING]
    todo_coord: TodoCoordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR_TODO]

    entities: list[SensorEntity] = []

    for list_id, list_data in (shop_coord.data or {}).items():
        entities.append(
            FamilieDosmerShoppingSensor(
                shop_coord, family_id, list_id,
                f"{list_data['list']['name']} unchecked", family_name,
            )
        )

    for list_id, list_data in (todo_coord.data or {}).items():
        entities.append(
            FamilieDosmerTodoSensor(
                todo_coord, family_id, list_id,
                f"{list_data['list']['name']} open", family_name,
            )
        )

    async_add_entities(entities)


class FamilieDosmerShoppingSensor(
    CoordinatorEntity[ShoppingCoordinator], SensorEntity
):
    """Sensor counting unchecked items in a shopping list."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 0

    def __init__(
        self,
        coordinator: ShoppingCoordinator,
        family_id: str,
        list_id: str,
        name: str,
        family_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._family_id = family_id
        self._list_id = list_id
        self._attr_unique_id = f"familiedosmer_sensor_shopping_{list_id}"
        self._attr_name = name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, family_id)},
            name=family_name,
            manufacturer="FamilieDosmer",
        )

    @property
    def native_value(self) -> int:
        data = self.coordinator.data.get(self._list_id, {})
        items: list[dict[str, Any]] = data.get("items", [])
        return len([i for i in items if not i.get("checked")])

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success


class FamilieDosmerTodoSensor(
    CoordinatorEntity[TodoCoordinator], SensorEntity
):
    """Sensor counting open (uncompleted) items in a todo list."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 0

    def __init__(
        self,
        coordinator: TodoCoordinator,
        family_id: str,
        list_id: str,
        name: str,
        family_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._family_id = family_id
        self._list_id = list_id
        self._attr_unique_id = f"familiedosmer_sensor_todo_{list_id}"
        self._attr_name = name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, family_id)},
            name=family_name,
            manufacturer="FamilieDosmer",
        )

    @property
    def native_value(self) -> int:
        data = self.coordinator.data.get(self._list_id, {})
        items: list[dict[str, Any]] = data.get("items", [])
        return len([i for i in items if not i.get("completed")])

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success
