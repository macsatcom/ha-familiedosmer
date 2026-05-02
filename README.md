# FamilieDosmer for Home Assistant

Custom integration that brings FamilieDosmer's shopping lists, todo lists, and meal plan into Home Assistant.

## Features

- **Shopping lists** — Each shopping list becomes a `todo` entity with full create/update/delete support. Check items off directly from your dashboard.
- **Todo lists** — Chore lists synced with FamilieDosmer. Mark tasks complete/uncomplete.
- **Meal plan** — View your weekly dinner plan on a `calendar` entity.
- **Count sensors** — See how many unchecked shopping items or open todo items remain.

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations** → 3-dots menu → **Custom repositories**
3. Enter `https://github.com/macsatcom/ha-familiedosmer` as the repository URL, category **Integration**
4. Click **Add**, then find "FamilieDosmer" in the integration list and install it
5. Restart Home Assistant

### Manual

Copy the `custom_components/familiedosmer/` folder into your Home Assistant `custom_components/` directory and restart.

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **FamilieDosmer** and select it
3. Enter your FamilieDosmer host URL (e.g. `https://familiedosmer.example.com`)
4. Enter your Personal Access Token (PAT) — obtain it from **Min profil** → **API-adgangstokens** in FamilieDosmer
5. Select which families to integrate
6. Click **Submit**

## Required Token Scopes

| Scope | Needed for |
|---|---|
| `shopping:read` | Reading shopping lists and items |
| `shopping:write` | Checking/unchecking items, adding items |
| `todos:read` | Reading todo lists and items |
| `todos:write` | Marking todo items complete/uncomplete |
| `mealplan:read` | Reading the meal plan |

## Entities Created

| Entity | Type | Description |
|--------|------|-------------|
| *Shopping list name* | `todo` | Full shopping list with check/uncheck |
| *Todo list name* | `todo` | Chore/task list |
| *Family name* madplan | `calendar` | Meal plan calendar |
| *Shopping list name* unchecked | `sensor` | Count of unchecked items |
| *Todo list name* open | `sensor` | Count of open todo items |

## Polling Intervals

| Data | Interval |
|------|----------|
| Shopping lists | 30 seconds |
| Todo lists | 60 seconds |
| Meal plan | 60 minutes |

The integration is fully poll-based — there is no push/webhook mechanism.

## License

MIT
