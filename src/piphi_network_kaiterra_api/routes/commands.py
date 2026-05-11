from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from piphi_runtime_kit_python import build_event_ingest_response

from ..state import append_runtime_event, commands, refresh_all_entries, refresh_entry, registry

router = APIRouter(tags=["commands"])


@router.post("/command")
async def command(payload: dict[str, Any]):
    command_name = str(payload.get("command") or payload.get("capability_id") or "").strip()
    if not command_name:
        raise HTTPException(status_code=400, detail="Missing command")
    if command_name not in commands:
        raise HTTPException(status_code=400, detail=f"Unsupported command: {command_name}")

    device_id = str(payload.get("device_id") or "demo-device")
    config_id = str(payload.get("config_id") or device_id)
    entry = registry.get(config_id) or {
        "device_id": device_id,
        "config_id": config_id,
    }
    refresh_result = None
    if command_name in {"refresh", "sync_cloud"}:
        if registry.get(config_id) is not None:
            refresh_result = await refresh_entry(registry.get(config_id))
        elif command_name == "sync_cloud":
            refresh_result = await refresh_all_entries()

    event = append_runtime_event(
        "runtime.command.received",
        entry,
        {
            "command": command_name,
            "device_id": device_id,
            "entity_id": payload.get("entity_id"),
            "args": payload.get("args") or {},
            "refresh_result": refresh_result,
        },
    )
    response = build_event_ingest_response(event)
    response_payload = response.model_dump() if hasattr(response, "model_dump") else dict(response)
    return {
        **response_payload,
        "ok": True,
        "command": command_name,
        "device_id": device_id,
    }
