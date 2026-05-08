"""Constants for the FamilieDosmer integration."""

DOMAIN = "familiedosmer"

PLATFORMS = ["todo", "calendar", "sensor"]

COORDINATOR_SHOPPING = "coordinator_shopping"
COORDINATOR_TODO = "coordinator_todo"
COORDINATOR_MEALPLAN = "coordinator_mealplan"

DATA_KEY_API = "api"
DATA_KEY_FAMILY_ID = "family_id"

SERVICE_LOG_DONE = "log_done"
SERVICE_ADD_SHOPPING = "add_shopping_item"
SERVICE_UPDATE_SHOPPING = "update_shopping_item"
SERVICE_DELETE_SHOPPING = "delete_shopping_item"
SERVICE_UPDATE_TODO = "update_todo_item"

MEAL_TYPE_LABELS = {
    "breakfast": "Morgenmad",
    "lunch": "Frokost",
    "dinner": "Aftensmad",
    "snack": "Snack",
}

SCOPE_NAMES = {
    "profile:read": "Profile read",
    "todos:read": "Todo lists read",
    "todos:write": "Todo lists write",
    "shopping:read": "Shopping lists read",
    "shopping:write": "Shopping lists write",
    "mealplan:read": "Meal plan read",
    "done:write": "Done entries write",
}
