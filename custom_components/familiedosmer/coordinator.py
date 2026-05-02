"""DataUpdateCoordinators for the FamilieDosmer integration."""

from datetime import date, datetime, timedelta
import logging
from typing import Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import FamilieDosmerApi, FamilieDosmerAuthError

_LOGGER = logging.getLogger(__name__)


class ShoppingCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for shopping lists (30-second interval)."""

    def __init__(
        self, hass, api: FamilieDosmerApi, family_id: str
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"FamilieDosmer Shopping {family_id}",
            update_interval=timedelta(seconds=30),
        )
        self.api = api
        self.family_id = family_id

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            lists = await self.api.get_shopping_lists(self.family_id)
            result: dict[str, Any] = {}
            for lst in lists:
                items = await self.api.get_shopping_items(
                    self.family_id, lst["id"]
                )
                result[lst["id"]] = {"list": lst, "items": items}
            return result
        except FamilieDosmerAuthError as err:
            raise ConfigEntryAuthFailed from err
        except Exception as err:
            raise UpdateFailed(f"Error fetching shopping data: {err}") from err


class TodoCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for todo lists (60-second interval)."""

    def __init__(
        self, hass, api: FamilieDosmerApi, family_id: str
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"FamilieDosmer Todos {family_id}",
            update_interval=timedelta(seconds=60),
        )
        self.api = api
        self.family_id = family_id

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            lists = await self.api.get_todo_lists(self.family_id)
            result: dict[str, Any] = {}
            for lst in lists:
                items = await self.api.get_todo_items(
                    self.family_id, lst["id"]
                )
                result[lst["id"]] = {"list": lst, "items": items}
            return result
        except FamilieDosmerAuthError as err:
            raise ConfigEntryAuthFailed from err
        except Exception as err:
            raise UpdateFailed(f"Error fetching todo data: {err}") from err


class MealPlanCoordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    """Coordinator for meal plan (60-minute interval)."""

    def __init__(
        self, hass, api: FamilieDosmerApi, family_id: str
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"FamilieDosmer MealPlan {family_id}",
            update_interval=timedelta(hours=1),
        )
        self.api = api
        self.family_id = family_id

    async def _async_update_data(self) -> list[dict[str, Any]]:
        try:
            today = date.today()
            from_date = (today - timedelta(days=7)).isoformat()
            to_date = (today + timedelta(days=14)).isoformat()
            return await self.api.get_meal_plan(
                self.family_id, from_date, to_date
            )
        except FamilieDosmerAuthError as err:
            raise ConfigEntryAuthFailed from err
        except Exception as err:
            raise UpdateFailed(
                f"Error fetching meal plan data: {err}"
            ) from err
