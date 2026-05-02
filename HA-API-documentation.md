# FamilieDosmer — Home Assistant API Documentation

This document describes the external integration API (`/api/v1/`), intended for Home Assistant and other third-party integrations.

---

## Authentication

All requests must include a **Personal Access Token (PAT)** as a Bearer token:

```
Authorization: Bearer <your-token>
```

### Obtaining a Token

1. Log in to FamilieDosmer
2. Go to **Min profil** → **API-adgangstokens**
3. Enter a name (e.g. "Home Assistant"), select the scopes you need, and click **Opret token**
4. Copy the token immediately — it is only shown once

### Scopes

Each token is limited to the scopes you select at creation:

| Scope | Description |
|---|---|
| `profile:read` | Read user profile and family memberships |
| `todos:read` | Read todo lists and items |
| `todos:write` | Mark todo items as completed/uncompleted |
| `shopping:read` | Read shopping lists and items |
| `shopping:write` | Add, update, and delete shopping items |
| `mealplan:read` | Read the meal plan |

### Error Responses

| HTTP | Meaning |
|---|---|
| `401` | Missing or invalid token |
| `403` | Token does not have the required scope |
| `404` | Resource not found |
| `400` | Invalid request body |

---

## Base URL

```
https://<your-domain>/api/v1
```

All endpoints return JSON. Dates are ISO 8601 strings.

---

## Profile

### GET `/api/v1/profile`

Returns the authenticated user's profile and their family memberships.

**Required scope:** `profile:read`

**Response:**
```json
{
  "id": "usr_abc123",
  "email": "user@example.com",
  "displayName": "Anders",
  "language": "da",
  "families": [
    {
      "id": "fam_xyz789",
      "name": "Familie Hansen",
      "role": "ADMIN",
      "joinedAt": "2026-01-15T10:00:00.000Z"
    }
  ]
}
```

---

## Todo Lists

### GET `/api/v1/families/:familyId/todos`

Returns all todo lists visible to the authenticated user in the given family.

**Required scope:** `todos:read`

**Response:**
```json
[
  {
    "id": "list_abc",
    "familyId": "fam_xyz789",
    "name": "Ugentlige opgaver",
    "order": 0,
    "sharedWithIds": [],
    "notifyDeadlines": false,
    "recurrenceType": "weekly",
    "recurrenceDayOfWeek": 1,
    "recurrenceTime": "08:00",
    "createdAt": "2026-01-20T08:00:00.000Z"
  }
]
```

**`recurrenceType` values:** `daily` | `weekly` | `monthly` | `yearly` | `null`

---

### GET `/api/v1/families/:familyId/todos/:listId/items`

Returns items in a todo list.

**Required scope:** `todos:read`

**Query parameters:**

| Parameter | Type | Default | Max | Description |
|---|---|---|---|---|
| `limit` | integer | `100` | `500` | Number of items to return |
| `offset` | integer | `0` | — | Number of items to skip |

**Response:**
```json
{
  "items": [
    {
      "id": "item_abc",
      "listId": "list_abc",
      "title": "Støvsug stuen",
      "order": 0,
      "description": null,
      "completed": false,
      "assignedToId": null,
      "assignedTo": null,
      "dueDate": null,
      "deadlineNotify": true,
      "recurrenceType": null,
      "deleteAfterDone": false,
      "createdAt": "2026-01-20T08:00:00.000Z"
    }
  ],
  "total": 12,
  "limit": 100,
  "offset": 0
}
```

---

### PATCH `/api/v1/families/:familyId/todos/:listId/items/:itemId`

Marks a todo item as completed or uncompleted.

**Required scope:** `todos:write`

**Request body:**
```json
{
  "completed": true
}
```

**Response:** Updated item object (same structure as items array above).

---

## Shopping Lists

### GET `/api/v1/families/:familyId/shopping`

Returns all shopping lists for the given family.

**Required scope:** `shopping:read`

**Response:**
```json
[
  {
    "id": "sl_abc",
    "familyId": "fam_xyz789",
    "name": "Uge 17",
    "sharedWithIds": [],
    "createdById": "usr_abc123",
    "createdAt": "2026-04-20T10:00:00.000Z"
  }
]
```

---

### GET `/api/v1/families/:familyId/shopping/:listId/items`

Returns all items in a shopping list.

**Required scope:** `shopping:read`

**Query parameters:**

| Parameter | Type | Default | Max | Description |
|---|---|---|---|---|
| `limit` | integer | `500` | `500` | Number of items to return |
| `offset` | integer | `0` | — | Number of items to skip |

**Response:**
```json
{
  "items": [
    {
      "id": "sli_abc",
      "familyId": "fam_xyz789",
      "listId": "sl_abc",
      "name": "Mælk",
      "category": "Mejeri",
      "quantity": 2,
      "unit": "L",
      "checked": false,
      "sourceType": "manual",
      "addedBy": "usr_abc123",
      "createdAt": "2026-04-20T10:00:00.000Z"
    }
  ],
  "total": 8,
  "limit": 500,
  "offset": 0
}
```

---

### POST `/api/v1/families/:familyId/shopping/:listId/items`

Adds an item to a shopping list.

**Required scope:** `shopping:write`

**Request body:**
```json
{
  "name": "Æbler",
  "category": "Frugt & Grønt",
  "quantity": 6,
  "unit": "stk"
}
```

All fields except `name` are optional.

**Response:** `201 Created` with the created item object.

---

### PATCH `/api/v1/families/:familyId/shopping/:listId/items/:itemId`

Updates a shopping item (e.g. check/uncheck, change quantity).

**Required scope:** `shopping:write`

**Request body** (all fields optional):
```json
{
  "checked": true,
  "name": "Æbler",
  "quantity": 8,
  "unit": "stk"
}
```

**Response:** Updated item object.

---

### DELETE `/api/v1/families/:familyId/shopping/:listId/items/:itemId`

Removes an item from a shopping list.

**Required scope:** `shopping:write`

**Response:** `204 No Content`

---

## Meal Plan

### GET `/api/v1/families/:familyId/mealplan`

Returns the meal plan for a date range.

**Required scope:** `mealplan:read`

**Query parameters:**

| Parameter | Type | Example | Description |
|---|---|---|---|
| `from` | date string | `2026-04-21` | Start date (inclusive). Defaults to start of current week |
| `to` | date string | `2026-04-27` | End date (inclusive). Defaults to end of current week |

**Response:**
```json
{
  "entries": [
    {
      "id": "mp_abc",
      "date": "2026-04-21T00:00:00.000Z",
      "mealType": "dinner",
      "customName": null,
      "recipe": {
        "id": "rec_abc",
        "title": "Spaghetti Bolognese",
        "servings": 4,
        "imageUrl": "https://...",
        "tags": ["pasta", "kød"]
      }
    },
    {
      "id": "mp_def",
      "date": "2026-04-22T00:00:00.000Z",
      "mealType": "dinner",
      "customName": "Rester fra i går",
      "recipe": null
    }
  ]
}
```

**`mealType` values:** `breakfast` | `lunch` | `dinner` | `snack`

---

## Writing a Custom Component (`custom_components/`)

This section contains everything needed to write a proper Python-based HA integration — not just YAML sensors.

---

### Integration Folder Structure

```
custom_components/familiedosmer/
├── __init__.py          # Entry point: setup_entry, unload_entry
├── manifest.json        # Integration metadata
├── config_flow.py       # UI setup wizard (2 steps)
├── api.py               # Thin async HTTP client around /api/v1/
├── coordinator.py       # DataUpdateCoordinators (one per resource type)
├── todo.py              # TodoListEntity for shopping and todo lists
├── calendar.py          # CalendarEntity for meal plan
├── sensor.py            # Sensor entities (uncompleted count, total items)
├── strings.json         # UI strings
└── translations/
    └── en.json
```

---

### `manifest.json`

```json
{
  "domain": "familiedosmer",
  "name": "FamilieDosmer",
  "version": "1.0.0",
  "documentation": "https://github.com/your-org/ha-familiedosmer",
  "requirements": [],
  "dependencies": [],
  "codeowners": [],
  "iot_class": "cloud_polling",
  "config_flow": true
}
```

`iot_class: cloud_polling` is correct — the integration polls a remote HTTP API with no push mechanism.

---

### Config Flow (2 steps)

**Step 1 — Credentials**

Show a form with two fields:
- `host` (string) — base URL, e.g. `https://familiedosmer.example.com`
- `token` (string) — the PAT from the user's profile page

On submit: call `GET /api/v1/profile` to validate. If `401` → show error `"invalid_auth"`. If connection error → show `"cannot_connect"`.

On success: store profile in flow context. Proceed to step 2.

**Step 2 — Select families**

If the profile contains only one family, skip this step and select it automatically.

If multiple families: show a multi-select checkbox list populated from `profile.families[].name`. Store selected `family_ids` in config entry.

**Config entry `data` dict:**

```python
{
    "host": "https://familiedosmer.example.com",
    "token": "a3f9...",           # raw PAT, stored in HA credential store
    "family_ids": ["fam_xyz789"]  # list of selected family IDs
}
```

**Reauth flow:**

When the API returns `401`, raise `ConfigEntryAuthFailed`. HA will surface a reauth notification in the UI. The reauth flow shows Step 1 again (host pre-filled, token empty).

---

### Entity Mapping

| API resource | HA platform | HA class | Notes |
|---|---|---|---|
| Shopping list | `todo` | `TodoListEntity` | Each list = one entity |
| Todo list | `todo` | `TodoListEntity` | Each list = one entity |
| Meal plan (per family) | `calendar` | `CalendarEntity` | One calendar entity per family |
| Shopping list unchecked count | `sensor` | `SensorEntity` | `state_class: measurement` |
| Todo list open item count | `sensor` | `SensorEntity` | `state_class: measurement` |

All entities have `should_poll = False` — updates come from the coordinator.

---

### Unique IDs

All `id` fields in the API are UUIDs and are **stable** — they never change for the lifetime of the resource. Use them directly as `unique_id`.

| Entity | `unique_id` |
|---|---|
| Shopping list todo entity | `familiedosmer_{list_id}` |
| Todo list todo entity | `familiedosmer_{list_id}` |
| Meal plan calendar | `familiedosmer_mealplan_{family_id}` |
| Shopping list sensor | `familiedosmer_sensor_shopping_{list_id}` |
| Todo list sensor | `familiedosmer_sensor_todo_{list_id}` |

The `device_info` for all entities in the same family should share a `DeviceInfo` with `identifiers={(DOMAIN, family_id)}` and `name=family.name`.

---

### Polling Intervals (Coordinators)

Use **three separate `DataUpdateCoordinator` instances** per family, each with a different update interval:

| Coordinator | Interval | Fetches |
|---|---|---|
| `ShoppingCoordinator` | **30 seconds** | All shopping lists + items for the family |
| `TodoCoordinator` | **60 seconds** | All todo lists + items for the family |
| `MealPlanCoordinator` | **60 minutes** | Meal plan entries ±14 days from today |

The shopping interval is short because family members actively add and check items throughout the day. The meal plan changes at most once a day.

There is **no push/webhook mechanism** — the integration is purely poll-based.

---

### `api.py` — HTTP Client

```python
import aiohttp
from dataclasses import dataclass

BASE = "/api/v1"

class FamilieDosmerApiError(Exception): pass
class FamilieDosmerAuthError(FamilieDosmerApiError): pass

class FamilieDosmerApi:
    def __init__(self, session: aiohttp.ClientSession, host: str, token: str):
        self._session = session
        self._base = host.rstrip("/") + BASE
        self._headers = {"Authorization": f"Bearer {token}"}

    async def _get(self, path: str, params: dict = None):
        async with self._session.get(
            self._base + path, headers=self._headers, params=params
        ) as resp:
            if resp.status == 401:
                raise FamilieDosmerAuthError("Invalid or expired token")
            resp.raise_for_status()
            return await resp.json()

    async def _patch(self, path: str, body: dict):
        async with self._session.patch(
            self._base + path, headers=self._headers, json=body
        ) as resp:
            if resp.status == 401:
                raise FamilieDosmerAuthError()
            resp.raise_for_status()
            return await resp.json()

    async def _post(self, path: str, body: dict):
        async with self._session.post(
            self._base + path, headers=self._headers, json=body
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _delete(self, path: str):
        async with self._session.delete(
            self._base + path, headers=self._headers
        ) as resp:
            resp.raise_for_status()

    async def get_profile(self):
        return await self._get("/profile")

    async def get_shopping_lists(self, family_id: str):
        return await self._get(f"/families/{family_id}/shopping")

    async def get_shopping_items(self, family_id: str, list_id: str):
        data = await self._get(
            f"/families/{family_id}/shopping/{list_id}/items",
            params={"limit": 500}
        )
        return data["items"]

    async def add_shopping_item(self, family_id: str, list_id: str, name: str, **kwargs):
        return await self._post(
            f"/families/{family_id}/shopping/{list_id}/items",
            {"name": name, **kwargs}
        )

    async def update_shopping_item(self, family_id: str, list_id: str, item_id: str, **kwargs):
        return await self._patch(
            f"/families/{family_id}/shopping/{list_id}/items/{item_id}", kwargs
        )

    async def delete_shopping_item(self, family_id: str, list_id: str, item_id: str):
        await self._delete(f"/families/{family_id}/shopping/{list_id}/items/{item_id}")

    async def get_todo_lists(self, family_id: str):
        return await self._get(f"/families/{family_id}/todos")

    async def get_todo_items(self, family_id: str, list_id: str):
        data = await self._get(
            f"/families/{family_id}/todos/{list_id}/items",
            params={"limit": 500}
        )
        return data["items"]

    async def update_todo_item(self, family_id: str, list_id: str, item_id: str, completed: bool):
        return await self._patch(
            f"/families/{family_id}/todos/{list_id}/items/{item_id}",
            {"completed": completed}
        )

    async def get_meal_plan(self, family_id: str, from_date: str, to_date: str):
        data = await self._get(
            f"/families/{family_id}/mealplan",
            params={"from": from_date, "to": to_date}
        )
        return data["entries"]
```

---

### `coordinator.py`

```python
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed
from .api import FamilieDosmerApi, FamilieDosmerAuthError

class ShoppingCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api: FamilieDosmerApi, family_id: str):
        super().__init__(hass, logger, name="FamilieDosmer Shopping",
                         update_interval=timedelta(seconds=30))
        self.api = api
        self.family_id = family_id

    async def _async_update_data(self):
        try:
            lists = await self.api.get_shopping_lists(self.family_id)
            result = {}
            for lst in lists:
                items = await self.api.get_shopping_items(self.family_id, lst["id"])
                result[lst["id"]] = {"list": lst, "items": items}
            return result
        except FamilieDosmerAuthError as err:
            raise ConfigEntryAuthFailed from err   # triggers reauth flow
        except Exception as err:
            raise UpdateFailed(f"Error fetching shopping data: {err}") from err

# TodoCoordinator: same pattern, update_interval=timedelta(seconds=60)
# MealPlanCoordinator: same pattern, update_interval=timedelta(hours=1)
#   fetches from today-7 days to today+14 days
```

---

### `todo.py` — Shopping List as `TodoListEntity`

```python
from homeassistant.components.todo import (
    TodoListEntity, TodoItem, TodoItemStatus, TodoListEntityFeature
)

class FamilieDosmerShoppingList(TodoListEntity):
    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
    )

    def __init__(self, coordinator, family_id, list_id, list_name):
        self._coordinator = coordinator
        self._family_id = family_id
        self._list_id = list_id
        self._attr_unique_id = f"familiedosmer_{list_id}"
        self._attr_name = list_name

    @property
    def todo_items(self) -> list[TodoItem]:
        data = self._coordinator.data.get(self._list_id, {})
        items = data.get("items", [])
        return [
            TodoItem(
                uid=item["id"],
                summary=_format_shopping_name(item),
                status=(
                    TodoItemStatus.COMPLETED if item["checked"]
                    else TodoItemStatus.NEEDS_ACTION
                ),
            )
            for item in items
        ]

    async def async_create_todo_item(self, item: TodoItem) -> None:
        name, qty, unit = _parse_shopping_name(item.summary)
        await self._coordinator.api.add_shopping_item(
            self._family_id, self._list_id, name,
            quantity=qty, unit=unit
        )
        await self._coordinator.async_request_refresh()

    async def async_update_todo_item(self, item: TodoItem) -> None:
        checked = item.status == TodoItemStatus.COMPLETED
        await self._coordinator.api.update_shopping_item(
            self._family_id, self._list_id, item.uid, checked=checked
        )
        await self._coordinator.async_request_refresh()

    async def async_delete_todo_items(self, uids: set[str]) -> None:
        for uid in uids:
            await self._coordinator.api.delete_shopping_item(
                self._family_id, self._list_id, uid
            )
        await self._coordinator.async_request_refresh()


def _format_shopping_name(item: dict) -> str:
    """Build display name: 'Mælk 2 L' or just 'Mælk'."""
    name = item["name"]
    qty = item.get("quantity")
    unit = item.get("unit") or ""
    if qty:
        qty_str = str(int(qty)) if qty == int(qty) else str(qty)
        return f"{name} {qty_str} {unit}".strip()
    return name

def _parse_shopping_name(summary: str) -> tuple[str, float | None, str | None]:
    """Try to parse 'Mælk 2 L' back into (name, qty, unit). Falls back to (summary, None, None)."""
    parts = summary.rsplit(" ", 2)
    if len(parts) == 3:
        try:
            return parts[0], float(parts[1]), parts[2]
        except ValueError:
            pass
    return summary, None, None
```

**Todo list** uses the same pattern — map `item["title"]` to `summary`, `item["completed"]` to status, `item["dueDate"]` to `due` (parse ISO string to `datetime.date`).

For `async_create_todo_item` on todo lists: the API does not yet expose a create endpoint under `/api/v1/`. Only `PATCH` (complete/uncomplete) is supported. Set `supported_features` accordingly — omit `CREATE_TODO_ITEM` and `DELETE_TODO_ITEM` until the API is extended.

---

### `calendar.py` — Meal Plan as `CalendarEntity`

```python
from datetime import date, timedelta
from homeassistant.components.calendar import CalendarEntity, CalendarEvent

MEAL_TYPE_LABELS = {
    "breakfast": "Morgenmad",
    "lunch": "Frokost",
    "dinner": "Aftensmad",
    "snack": "Snack",
}

class FamilieDosmerMealPlan(CalendarEntity):
    def __init__(self, coordinator, family_id, family_name):
        self._coordinator = coordinator
        self._family_id = family_id
        self._attr_unique_id = f"familiedosmer_mealplan_{family_id}"
        self._attr_name = f"{family_name} madplan"

    @property
    def event(self) -> CalendarEvent | None:
        """Return today's dinner as the 'current' event, or None."""
        today = date.today().isoformat()
        for entry in (self._coordinator.data or []):
            if entry["date"][:10] == today and entry["mealType"] == "dinner":
                return self._entry_to_event(entry)
        return None

    async def async_get_events(self, hass, start_date, end_date) -> list[CalendarEvent]:
        entries = await self._coordinator.api.get_meal_plan(
            self._family_id,
            start_date.date().isoformat(),
            end_date.date().isoformat(),
        )
        return [self._entry_to_event(e) for e in entries]

    def _entry_to_event(self, entry: dict) -> CalendarEvent:
        d = date.fromisoformat(entry["date"][:10])
        recipe = entry.get("recipe")
        title = recipe["title"] if recipe else entry.get("customName") or "Ukendt"
        meal_label = MEAL_TYPE_LABELS.get(entry["mealType"], entry["mealType"])
        description = meal_label
        if recipe:
            description += f" · {recipe['servings']} pers."
            if recipe.get("tags"):
                description += f" · {', '.join(recipe['tags'])}"
        return CalendarEvent(
            summary=title,
            start=d,
            end=d + timedelta(days=1),
            description=description,
            uid=entry["id"],
        )
```

---

### `__init__.py` — Entry Setup

```python
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import aiohttp

PLATFORMS = ["todo", "calendar", "sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = aiohttp.ClientSession()
    api = FamilieDosmerApi(session, entry.data["host"], entry.data["token"])

    coordinators = {}
    for family_id in entry.data["family_ids"]:
        coordinators[family_id] = {
            "shopping": ShoppingCoordinator(hass, api, family_id),
            "todo": TodoCoordinator(hass, api, family_id),
            "mealplan": MealPlanCoordinator(hass, api, family_id),
        }
        for coord in coordinators[family_id].values():
            await coord.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "api": api,
        "session": session,
        "coordinators": coordinators,
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        await data["session"].close()
    return unload_ok
```

---

### Error Handling

| API response | Python exception | HA behaviour |
|---|---|---|
| `401 Unauthorized` | `FamilieDosmerAuthError` | Raise `ConfigEntryAuthFailed` → HA shows reauth banner |
| `403 Forbidden` | `aiohttp.ClientResponseError` | Raise `UpdateFailed` — logs error, retries next interval |
| `429 Too Many Requests` | `aiohttp.ClientResponseError` | Raise `UpdateFailed` — coordinator backs off automatically |
| Network/timeout | `aiohttp.ClientError` | Raise `UpdateFailed` — entities become `unavailable` |

Never raise bare exceptions from `_async_update_data` — always wrap in `UpdateFailed` or `ConfigEntryAuthFailed`.

---

## Home Assistant Integration Guide (YAML)

### Recommended Setup

1. Create a token with these scopes: `profile:read`, `shopping:read`, `shopping:write`, `todos:read`, `todos:write`, `mealplan:read`
2. Store the token in your HA `secrets.yaml`:
   ```yaml
   familiedosmer_token: "your-64-char-hex-token"
   ```

### REST Sensor — Shopping List

Add to `configuration.yaml`:

```yaml
rest:
  - resource: "https://your-domain/api/v1/families/YOUR_FAMILY_ID/shopping/YOUR_LIST_ID/items"
    method: GET
    headers:
      Authorization: "Bearer !secret familiedosmer_token"
    scan_interval: 60
    sensor:
      - name: "Indkøbsliste varer"
        value_template: "{{ value_json.total }}"
        json_attributes_path: "$.items"
        json_attributes:
          - "id"
          - "name"
          - "quantity"
          - "unit"
          - "checked"
          - "category"
```

### REST Sensor — Madplan i dag

```yaml
rest:
  - resource: "https://your-domain/api/v1/families/YOUR_FAMILY_ID/mealplan"
    method: GET
    headers:
      Authorization: "Bearer !secret familiedosmer_token"
    params:
      from: "{{ now().strftime('%Y-%m-%d') }}"
      to: "{{ now().strftime('%Y-%m-%d') }}"
    scan_interval: 3600
    sensor:
      - name: "Aftensmad i dag"
        value_template: >
          {% set dinner = value_json.entries | selectattr('mealType', 'eq', 'dinner') | list %}
          {% if dinner %}
            {{ dinner[0].recipe.title if dinner[0].recipe else dinner[0].customName }}
          {% else %}
            Ikke planlagt
          {% endif %}
```

### REST Command — Afkrydse indkøbsvare

```yaml
rest_command:
  check_shopping_item:
    url: "https://your-domain/api/v1/families/{{ family_id }}/shopping/{{ list_id }}/items/{{ item_id }}"
    method: PATCH
    headers:
      Authorization: "Bearer !secret familiedosmer_token"
      Content-Type: "application/json"
    payload: '{"checked": {{ checked }}}'
```

### REST Command — Tilføj indkøbsvare

```yaml
rest_command:
  add_shopping_item:
    url: "https://your-domain/api/v1/families/{{ family_id }}/shopping/{{ list_id }}/items"
    method: POST
    headers:
      Authorization: "Bearer !secret familiedosmer_token"
      Content-Type: "application/json"
    payload: '{"name": "{{ name }}", "quantity": {{ quantity | default(1) }}, "unit": "{{ unit | default("") }}"}'
```

### Finde familyId og listId

Kald `/api/v1/profile` for at se dine families:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" https://your-domain/api/v1/profile
```

Kald derefter `/api/v1/families/YOUR_FAMILY_ID/shopping` for at se shopping-lister med deres ID'er.

---

## API Versioning

This API is versioned at `/api/v1/`. The contract for `/api/v1/` endpoints is kept stable. Breaking changes will be introduced under `/api/v2/` with advance notice.

Non-breaking additions (new optional fields, new endpoints) may be added to `/api/v1/` at any time.

---

## Rate Limiting

The API enforces a global rate limit of **300 requests per minute** per token. Exceeding this limit returns `429 Too Many Requests`.
