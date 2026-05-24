from __future__ import annotations

import httpx
import pytest

from piphi_network_kaiterra_api.main import app


@pytest.mark.anyio
async def test_command_accepts_automation_runtime_contract() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/command",
            json={
                "contract_version": "automation.runtime.command.v1",
                "command": "refresh_readings",
                "target": {
                    "config_id": "kaiterra-device",
                    "device_id": "kaiterra-device",
                },
                "params": {"force": True},
                "capability": "device.refresh",
                "capability_requirements": ["device.refresh"],
            },
        )

    body = response.json()
    assert response.status_code == 200
    assert body["ok"] is True
    assert body["command"] == "refresh"
    assert body["contract_version"] == "automation.runtime.command.v1"
    assert body["config_id"] == "kaiterra-device"
    assert body["params"] == {"force": True}


@pytest.mark.anyio
async def test_command_rejects_unsupported_capability() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/command",
            json={
                "command": "refresh",
                "target": {"device_id": "kaiterra-device"},
                "capability": "switch.power",
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "unsupported_capability"
