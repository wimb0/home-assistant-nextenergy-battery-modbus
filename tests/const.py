"""Constants and register seeds for NextEnergy Battery tests."""
import struct

from custom_components.nextenergy_battery.device import (
    BmsLive,
    BmsStatic,
    DeviceIdentity,
    Energy,
    InverterLive,
    InverterStatic,
    Meter,
    PowerFlow,
    Settings,
)

MOCK_SERIAL = "TEST_SN_12345"

MOCK_DATA = {"host": "1.2.3.4", "port": 502, "slave_id": 1}

MOCK_OPTIONS = {"polling_interval": 30, "prefix": "test_prefix"}

USER_INPUT = {**MOCK_DATA, **MOCK_OPTIONS}


def i32(value: int) -> list[int]:
    """Encode a signed 32-bit value as two big-endian registers."""
    return list(struct.unpack(">HH", struct.pack(">i", value)))


def u32(value: int) -> list[int]:
    """Encode an unsigned 32-bit value as two big-endian registers."""
    return list(struct.unpack(">HH", struct.pack(">I", value)))


def ascii_registers(text: str, length: int) -> list[int]:
    """Encode text as null-padded big-endian registers."""
    raw = text.encode("ascii")[: length * 2].ljust(length * 2, b"\x00")
    return list(struct.unpack(f">{length}H", raw))


def _expand(registers: dict[int, list[int]]) -> dict[int, int]:
    """Flatten block seeds to single-register values."""
    return {
        address + offset: word
        for address, words in registers.items()
        for offset, word in enumerate(words)
    }


def _zero_filled() -> dict[int, int]:
    """Zero every register the device model reads."""
    filled: dict[int, int] = {}
    for component in (
        DeviceIdentity,
        InverterStatic,
        BmsStatic,
        BmsLive,
        Meter,
        InverterLive,
        PowerFlow,
        Energy,
        Settings,
    ):
        for low, high in component.register_ranges:
            for address in range(low, high + 1):
                filled[address] = 0
    return filled


def _base_registers() -> dict[int, int]:
    """Registers shared by every scenario, keyed by address."""
    return _expand(
        {
            30000: ascii_registers("MQ2200-M-A", 16),
            30016: ascii_registers(MOCK_SERIAL, 16),
            36001: [0x123],
            37612: [85],
            39053: i32(2200),
            39055: i32(3000),
            39621: u32(94539),
            39623: u32(30),
            39625: u32(117613),
            39627: u32(4),
        }
    )


DISCHARGE_REGISTERS = {
    **_zero_filled(),
    **_base_registers(),
    **_expand(
        {
            39063: [4],
            39065: u32(0),
            39067: [0],
            39068: [4],
            39069: [0],
            39168: i32(200),
            39237: i32(-550),
            39423: [85],
            49203: [1],
        }
    ),
}

CHARGE_REGISTERS = {
    **_zero_filled(),
    **_base_registers(),
    **_expand(
        {
            37612: [50],
            39063: [4],
            39065: u32(0),
            39067: [0],
            39068: [0],
            39069: [0],
            39168: i32(-1500),
            39237: i32(750),
            39423: [50],
            49203: [6],
        }
    ),
}


def seed_discharge(unit) -> None:
    """Seed a discharging battery: SoC 85, -550 W battery, +200 W import."""
    for address, word in DISCHARGE_REGISTERS.items():
        unit.holding[address] = word


def seed_charge(unit) -> None:
    """Seed a charging battery: SoC 50, +750 W battery, -1500 W export."""
    for address, word in CHARGE_REGISTERS.items():
        unit.holding[address] = word
