"""Constants for the FamilieDosmer integration."""

DOMAIN = "familiedosmer"

PLATFORMS = ["todo", "calendar", "sensor"]

COORDINATOR_SHOPPING = "shopping"
COORDINATOR_TODO = "todo"
COORDINATOR_MEALPLAN = "mealplan"

DATA_KEY_API = "api"
DATA_KEY_SESSION = "session"
DATA_KEY_COORDINATORS = "coordinators"

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
}
