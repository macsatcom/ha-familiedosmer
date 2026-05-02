"""TodoListEntity implementations for shopping and todo lists."""

from datetime import date
from typing import Any

from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
    TodoListEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COORDINATOR_SHOPPING, COORDINATOR_TODO, DOMAIN, DATA_KEY_COORDINATORS
from .coordinator import ShoppingCoordinator, TodoCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators = hass.data[DOMAIN][entry.entry_id][DATA_KEY_COORDINATORS]
    family_names = entry.data.get("family_names", {})

    entities: list[TodoListEntity] = []

    for family_id, family_coords in coordinators.items():
        family_name = family_names.get(family_id, family_id)

        shop_coord: ShoppingCoordinator = family_coords[COORDINATOR_SHOPPING]
        shop_data = shop_coord.data or {}
        for list_id, list_data in shop_data.items():
            list_name = list_data["list"]["name"]
            entities.append(
                FamilieDosmerShoppingList(
                    shop_coord, family_id, list_id, list_name, family_name
                )
            )

        todo_coord: TodoCoordinator = family_coords[COORDINATOR_TODO]
        todo_data = todo_coord.data or {}
        for list_id, list_data in todo_data.items():
            list_name = list_data["list"]["name"]
            entities.append(
                FamilieDosmerTodoList(
                    todo_coord, family_id, list_id, list_name, family_name
                )
            )

    async_add_entities(entities)


def _format_shopping_name(item: dict[str, Any]) -> str:
    """Build display name: 'Mælk 2 L' or just 'Mælk'."""
    name = item["name"]
    qty = item.get("quantity")
    unit = item.get("unit") or ""
    if qty is not None:
        qty_num = float(qty)
        qty_str = str(int(qty)) if qty_num == int(qty_num) else str(qty_num)
        return f"{name} {qty_str} {unit}".strip()
    return name


def _parse_shopping_name(
    summary: str,
) -> tuple[str, float | None, str | None]:
    """Parse summary back into (name, qty, unit). Fallback to (summary, None, None)."""
    parts = summary.rsplit(" ", 2)
    if len(parts) == 3:
        try:
            qty = float(parts[1])
            return parts[0], qty, parts[2]
        except ValueError:
            pass
    return summary, None, None


def _qty_kwargs(qty: float | None, unit: str | None) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if qty is not None:
        kwargs["quantity"] = int(qty) if qty == int(qty) else qty
    if unit is not None:
        kwargs["unit"] = unit
    return kwargs


class FamilieDosmerShoppingList(CoordinatorEntity[ShoppingCoordinator], TodoListEntity):
    """TodoListEntity for a FamilieDosmer shopping list."""

    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
    )

    def __init__(
        self,
        coordinator: ShoppingCoordinator,
        family_id: str,
        list_id: str,
        list_name: str,
        family_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._family_id = family_id
        self._list_id = list_id
        self._attr_unique_id = f"familiedosmer_{list_id}"
        self._attr_name = list_name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, family_id)},
            name=family_name,
            manufacturer="FamilieDosmer",
        )

    @property
    def todo_items(self) -> list[TodoItem]:
        data = self.coordinator.data.get(self._list_id, {})
        items = data.get("items", [])
        return [
            TodoItem(
                uid=item["id"],
                summary=_format_shopping_name(item),
                status=(
                    TodoItemStatus.COMPLETED
                    if item.get("checked")
                    else TodoItemStatus.NEEDS_ACTION
                ),
            )
            for item in items
        ]

    async def async_create_todo_item(self, item: TodoItem) -> None:
        name, qty, unit = _parse_shopping_name(item.summary)
        await self.coordinator.api.add_shopping_item(
            self._family_id,
            self._list_id,
            name,
            **_qty_kwargs(qty, unit),
        )
        await self.coordinator.async_request_refresh()

    async def async_update_todo_item(self, item: TodoItem) -> None:
        name, qty, unit = _parse_shopping_name(item.summary)
        await self.coordinator.api.update_shopping_item(
            self._family_id,
            self._list_id,
            item.uid,
            checked=(item.status == TodoItemStatus.COMPLETED),
            name=name,
            **_qty_kwargs(qty, unit),
        )
        await self.coordinator.async_request_refresh()

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        for uid in uids:
            await self.coordinator.api.delete_shopping_item(
                self._family_id, self._list_id, uid
            )
        await self.coordinator.async_request_refresh()


class FamilieDosmerTodoList(CoordinatorEntity[TodoCoordinator], TodoListEntity):
    """TodoListEntity for a FamilieDosmer todo list."""

    _attr_supported_features = (
        TodoListEntityFeature.UPDATE_TODO_ITEM
    )

    def __init__(
        self,
        coordinator: TodoCoordinator,
        family_id: str,
        list_id: str,
        list_name: str,
        family_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._family_id = family_id
        self._list_id = list_id
        self._attr_unique_id = f"familiedosmer_{list_id}"
        self._attr_name = list_name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, family_id)},
            name=family_name,
            manufacturer="FamilieDosmer",
        )

    @property
    def todo_items(self) -> list[TodoItem]:
        data = self.coordinator.data.get(self._list_id, {})
        items = data.get("items", [])
        result: list[TodoItem] = []
        for item in items:
            due: date | None = None
            if item.get("dueDate"):
                try:
                    due = date.fromisoformat(item["dueDate"][:10])
                except (ValueError, TypeError):
                    pass
            result.append(
                TodoItem(
                    uid=item["id"],
                    summary=item["title"],
                    status=(
                        TodoItemStatus.COMPLETED
                        if item.get("completed")
                        else TodoItemStatus.NEEDS_ACTION
                    ),
                    due=due,
                    description=item.get("description") or None,
                )
            )
        return result

    async def async_update_todo_item(self, item: TodoItem) -> None:
        await self.coordinator.api.update_todo_item(
            self._family_id,
            self._list_id,
            item.uid,
            completed=(item.status == TodoItemStatus.COMPLETED),
        )
        await self.coordinator.async_request_refresh()
