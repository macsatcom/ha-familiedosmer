"""CalendarEntity for the FamilieDosmer meal plan."""

from datetime import date, datetime, timedelta
from typing import Any

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    COORDINATOR_MEALPLAN,
    DOMAIN,
    DATA_KEY_COORDINATORS,
    MEAL_TYPE_LABELS,
)
from .coordinator import MealPlanCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators = hass.data[DOMAIN][entry.entry_id][DATA_KEY_COORDINATORS]
    family_names = entry.data.get("family_names", {})

    entities: list[FamilieDosmerMealPlan] = []

    for family_id, family_coords in coordinators.items():
        family_name = family_names.get(family_id, family_id)
        entities.append(
            FamilieDosmerMealPlan(
                family_coords[COORDINATOR_MEALPLAN],
                family_id,
                family_name,
            )
        )

    async_add_entities(entities)


class FamilieDosmerMealPlan(
    CoordinatorEntity[MealPlanCoordinator], CalendarEntity
):
    """CalendarEntity showing the FamilieDosmer meal plan."""

    def __init__(
        self,
        coordinator: MealPlanCoordinator,
        family_id: str,
        family_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._family_id = family_id
        self._attr_unique_id = f"familiedosmer_mealplan_{family_id}"
        self._attr_name = f"{family_name} madplan"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, family_id)},
            name=family_name,
            manufacturer="FamilieDosmer",
        )

    @property
    def event(self) -> CalendarEvent | None:
        today = date.today()
        for entry in self.coordinator.data or []:
            try:
                entry_date = date.fromisoformat(entry["date"][:10])
            except (ValueError, KeyError):
                continue
            if entry_date == today and entry.get("mealType") == "dinner":
                return self._entry_to_event(entry)
        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        entries = await self.coordinator.api.get_meal_plan(
            self._family_id,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
        )
        return [self._entry_to_event(e) for e in entries]

    def _entry_to_event(self, entry: dict[str, Any]) -> CalendarEvent:
        d = date.fromisoformat(entry["date"][:10])
        recipe = entry.get("recipe")
        title = (
            recipe["title"]
            if recipe
            else entry.get("customName") or "Ukendt"
        )
        meal_label = MEAL_TYPE_LABELS.get(
            entry.get("mealType", ""), entry.get("mealType", "")
        )
        description = meal_label
        if recipe:
            description += f" · {recipe['servings']} pers."
            tags = recipe.get("tags")
            if tags:
                description += f" · {', '.join(tags)}"
        return CalendarEvent(
            summary=title,
            start=d,
            end=d + timedelta(days=1),
            description=description,
            uid=entry["id"],
        )
