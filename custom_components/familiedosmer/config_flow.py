"""Config flow for the FamilieDosmer integration."""

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import FamilieDosmerApi, FamilieDosmerApiError, FamilieDosmerAuthError
from .const import DOMAIN


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class FamilieDosmerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for FamilieDosmer."""

    VERSION = 2

    def __init__(self) -> None:
        self._token: str = ""
        self._profile: dict[str, Any] = {}
        self._reauth_entry: ConfigEntry | None = None

    async def _validate_credentials(self, token: str) -> dict[str, Any]:
        session = async_get_clientsession(self.hass)
        api = FamilieDosmerApi(session, token)
        try:
            return await api.get_profile()
        except FamilieDosmerAuthError:
            raise InvalidAuth
        except FamilieDosmerApiError as err:
            raise CannotConnect(str(err))

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                self._profile = await self._validate_credentials(
                    user_input["token"]
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "unknown"

            if not errors:
                self._token = user_input["token"]
                families = self._profile.get("families", [])

                if len(families) == 1:
                    return self.async_create_entry(
                        title=families[0]["name"],
                        data={
                            "token": self._token,
                            "family_id": families[0]["id"],
                            "family_name": families[0]["name"],
                        },
                    )

                return await self.async_step_families()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("token"): str,
                }
            ),
            errors=errors,
        )

    async def async_step_families(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        families = self._profile.get("families", [])

        if user_input is not None:
            selected_id = user_input.get("family")
            if not selected_id:
                errors["family"] = "at_least_one_family"
            if not errors:
                selected = next(f for f in families if f["id"] == selected_id)
                return self.async_create_entry(
                    title=selected["name"],
                    data={
                        "token": self._token,
                        "family_id": selected["id"],
                        "family_name": selected["name"],
                    },
                )

        family_options = {
            f["id"]: f"{f['name']} ({f.get('role', '')})"
            for f in families
        }

        return self.async_show_form(
            step_id="families",
            data_schema=vol.Schema(
                {
                    vol.Required("family"): vol.In(family_options),
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await self._validate_credentials(user_input["token"])
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "unknown"

            if not errors and self._reauth_entry:
                new_data = {**self._reauth_entry.data}
                new_data["token"] = user_input["token"]
                self.hass.config_entries.async_update_entry(
                    self._reauth_entry, data=new_data
                )
                await self.hass.config_entries.async_reload(
                    self._reauth_entry.entry_id
                )
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required("token"): str,
                }
            ),
            errors=errors,
        )


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate config entry from version 1 (multi-family) to version 2 (single-family)."""
    if config_entry.version == 1:
        data = {**config_entry.data}
        family_ids: list[str] = data.pop("family_ids", [])
        family_names: dict[str, str] = data.pop("family_names", {})
        data.pop("families", None)
        data["family_id"] = family_ids[0] if family_ids else ""
        data["family_name"] = family_names.get(data["family_id"], data["family_id"])
        hass.config_entries.async_update_entry(config_entry, data=data, version=2)
    return True
