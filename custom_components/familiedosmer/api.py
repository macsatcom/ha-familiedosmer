"""Async HTTP client for the FamilieDosmer API."""

from typing import Any

import aiohttp

BASE_URL = "https://www.familiedosmer.dk/api/v1"


class FamilieDosmerApiError(Exception):
    """General API error."""


class FamilieDosmerAuthError(FamilieDosmerApiError):
    """Authentication error (401)."""


class FamilieDosmerApi:
    """Thin async client around the FamilieDosmer /api/v1/ endpoints."""

    def __init__(self, session: aiohttp.ClientSession, token: str) -> None:
        self._session = session
        self._base = BASE_URL
        self._headers = {"Authorization": f"Bearer {token}"}

    async def _get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> Any:
        async with self._session.get(
            self._base + path, headers=self._headers, params=params
        ) as resp:
            if resp.status == 401:
                raise FamilieDosmerAuthError("Invalid or expired token")
            resp.raise_for_status()
            return await resp.json()

    async def _patch(self, path: str, body: dict[str, Any]) -> Any:
        async with self._session.patch(
            self._base + path, headers=self._headers, json=body
        ) as resp:
            if resp.status == 401:
                raise FamilieDosmerAuthError()
            resp.raise_for_status()
            return await resp.json()

    async def _post(self, path: str, body: dict[str, Any]) -> Any:
        async with self._session.post(
            self._base + path, headers=self._headers, json=body
        ) as resp:
            if resp.status == 401:
                raise FamilieDosmerAuthError()
            resp.raise_for_status()
            return await resp.json()

    async def _delete(self, path: str) -> None:
        async with self._session.delete(
            self._base + path, headers=self._headers
        ) as resp:
            if resp.status == 401:
                raise FamilieDosmerAuthError()
            resp.raise_for_status()

    async def get_profile(self) -> dict[str, Any]:
        """GET /api/v1/profile"""
        return await self._get("/profile")

    async def get_shopping_lists(self, family_id: str) -> list[dict[str, Any]]:
        """GET /api/v1/families/:familyId/shopping"""
        return await self._get(f"/families/{family_id}/shopping")

    async def get_shopping_items(
        self, family_id: str, list_id: str
    ) -> list[dict[str, Any]]:
        """GET /api/v1/families/:familyId/shopping/:listId/items"""
        data = await self._get(
            f"/families/{family_id}/shopping/{list_id}/items",
            params={"limit": 500},
        )
        return data["items"]

    async def add_shopping_item(
        self, family_id: str, list_id: str, name: str, **kwargs: Any
    ) -> dict[str, Any]:
        """POST /api/v1/families/:familyId/shopping/:listId/items"""
        return await self._post(
            f"/families/{family_id}/shopping/{list_id}/items",
            {"name": name, **kwargs},
        )

    async def update_shopping_item(
        self, family_id: str, list_id: str, item_id: str, **kwargs: Any
    ) -> dict[str, Any]:
        """PATCH /api/v1/families/:familyId/shopping/:listId/items/:itemId"""
        return await self._patch(
            f"/families/{family_id}/shopping/{list_id}/items/{item_id}",
            kwargs,
        )

    async def delete_shopping_item(
        self, family_id: str, list_id: str, item_id: str
    ) -> None:
        """DELETE /api/v1/families/:familyId/shopping/:listId/items/:itemId"""
        await self._delete(
            f"/families/{family_id}/shopping/{list_id}/items/{item_id}"
        )

    async def get_todo_lists(self, family_id: str) -> list[dict[str, Any]]:
        """GET /api/v1/families/:familyId/todos"""
        return await self._get(f"/families/{family_id}/todos")

    async def get_todo_items(
        self, family_id: str, list_id: str
    ) -> list[dict[str, Any]]:
        """GET /api/v1/families/:familyId/todos/:listId/items"""
        data = await self._get(
            f"/families/{family_id}/todos/{list_id}/items",
            params={"limit": 500},
        )
        return data["items"]

    async def update_todo_item(
        self, family_id: str, list_id: str, item_id: str, completed: bool
    ) -> dict[str, Any]:
        """PATCH /api/v1/families/:familyId/todos/:listId/items/:itemId"""
        return await self._patch(
            f"/families/{family_id}/todos/{list_id}/items/{item_id}",
            {"completed": completed},
        )

    async def get_meal_plan(
        self, family_id: str, from_date: str, to_date: str
    ) -> list[dict[str, Any]]:
        """GET /api/v1/families/:familyId/mealplan"""
        data = await self._get(
            f"/families/{family_id}/mealplan",
            params={"from": from_date, "to": to_date},
        )
        return data["entries"]
