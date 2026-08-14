#!/usr/bin/env python3
"""Regression checks for MQTT state retention and configuration refreshes."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOMFY = (ROOT / "Somfy.cpp").read_text()


def function_body(name: str) -> str:
    match = re.search(
        rf"(?:float|bool) SomfyShade(?:::[A-Za-z]+)?::{name}\([^{{]*\)\s*\{{(?P<body>.*?)\n\}}",
        SOMFY,
        re.DOTALL,
    )
    if not match:
        raise AssertionError(f"could not find {name} implementation")
    return match.group("body")


def test_position_updates_are_retained() -> None:
    position = function_body("p_currentPos")
    tilt_position = function_body("p_currentTiltPos")

    assert re.search(
        r'this->publish\("position",\s*this->transformPosition\([^;]+,\s*true\)',
        position,
    )
    assert re.search(
        r'this->publish\("tiltPosition",\s*this->transformPosition\([^;]+,\s*true\)',
        tilt_position,
    )


def test_loaded_configuration_refreshes_mqtt_state() -> None:
    assert re.search(
        r"bool SomfyShadeController::loadShadesFile\([^)]*\)\s*\{"
        r"(?P<body>.*?)\n\}",
        SOMFY,
        re.DOTALL,
    ).group("body").find("this->publish()") >= 0


if __name__ == "__main__":
    test_position_updates_are_retained()
    test_loaded_configuration_refreshes_mqtt_state()
    print("MQTT state regression checks passed")
