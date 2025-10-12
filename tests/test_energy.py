import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime

from src.energy.DeviceSchedule import DeviceSchedule

try:
    from src.energy.EnergyManagementSystem import manage_energy
except Exception:
    from src.energy.EnergyManagementSystem import SmartEnergyManagementSystem
    def manage_energy(**kwargs):
        return SmartEnergyManagementSystem().manage_energy(**kwargs)

BASE_PRIORITIES = {
    "Security": 1,
    "Refrigerator": 1,
    "Heating": 1,
    "Lights": 2,
    "Washer": 3,
}

def t(h, m=0):
    return datetime(2025, 1, 1, h, m, 0)

class TestEnergyManagementSystem:
    def test_day_low_price_temp_ok_no_limit_all_on(self):
        res = manage_energy(
            current_price=0.10,
            price_threshold=0.20,
            current_time=t(12, 0),
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=100.0,
            total_energy_used_today=10.0,
            device_priorities=BASE_PRIORITIES,
            scheduled_devices=[],
        )
        assert res.energy_saving_mode is False
        assert res.temperature_regulation_active is False
        assert res.device_status.get("Security") is True
        assert res.device_status.get("Refrigerator") is True
        assert res.device_status.get("Heating") is False
        assert "Lights" in res.device_status
        assert "Washer" in res.device_status

    def test_high_price_economy_mode_cuts_low_priority(self):
        res = manage_energy(
            current_price=0.35,
            price_threshold=0.20,
            current_time=t(14, 0),
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=100.0,
            total_energy_used_today=10.0,
            device_priorities=BASE_PRIORITIES,
            scheduled_devices=[],
        )
        assert res.energy_saving_mode is True
        assert res.device_status.get("Security") is True
        assert res.device_status.get("Refrigerator") is True
        assert res.device_status.get("Heating") is False
        assert res.device_status.get("Lights") is False
        assert res.device_status.get("Washer") is False

    def test_night_mode_keeps_only_essentials(self):
        res = manage_energy(
            current_price=0.10,
            price_threshold=0.20,
            current_time=t(23, 30),
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=100.0,
            total_energy_used_today=10.0,
            device_priorities=BASE_PRIORITIES,
            scheduled_devices=[],
        )
        for dev, on in res.device_status.items():
            if dev in ("Security", "Refrigerator"):
                assert on is True
            else:
                assert on is False

    def test_temp_below_range_triggers_regulation(self):
        res = manage_energy(
            current_price=0.10,
            price_threshold=0.20,
            current_time=t(10, 0),
            current_temperature=18.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=100.0,
            total_energy_used_today=10.0,
            device_priorities=BASE_PRIORITIES,
            scheduled_devices=[],
        )
        assert res.temperature_regulation_active is True

    def test_temp_above_range_triggers_regulation(self):
        res = manage_energy(
            current_price=0.10,
            price_threshold=0.20,
            current_time=t(10, 0),
            current_temperature=26.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=100.0,
            total_energy_used_today=10.0,
            device_priorities=BASE_PRIORITIES,
            scheduled_devices=[],
        )
        assert res.temperature_regulation_active is True

    def test_near_or_over_daily_limit_progressively_cuts_low_priority(self):
        res = manage_energy(
            current_price=0.10,
            price_threshold=0.20,
            current_time=t(16, 0),
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=30.0,
            total_energy_used_today=30.0,
            device_priorities=BASE_PRIORITIES,
            scheduled_devices=[],
        )
        assert res.device_status.get("Lights") is False
        assert res.device_status.get("Security") is True
        assert res.device_status.get("Refrigerator") is True

    def test_schedule_overrides_economy_mode(self):
        res = manage_energy(
            current_price=0.40,
            price_threshold=0.20,
            current_time=t(19, 0),
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=100.0,
            total_energy_used_today=10.0,
            device_priorities=BASE_PRIORITIES,
            scheduled_devices=[DeviceSchedule(device_name="Washer", scheduled_time=t(19, 0))],
        )
        assert res.energy_saving_mode is True
        assert res.device_status.get("Washer") is True

    def test_schedule_overrides_night_mode(self):
        res = manage_energy(
            current_price=0.10,
            price_threshold=0.20,
            current_time=t(1, 0),
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=100.0,
            total_energy_used_today=10.0,
            device_priorities=BASE_PRIORITIES,
            scheduled_devices=[DeviceSchedule(device_name="Lights", scheduled_time=t(1, 0))],
        )
        assert res.device_status.get("Lights") is True

    def test_equal_thresholds_do_not_trigger_modes(self):
        r1 = manage_energy(
            current_price=0.20,
            price_threshold=0.20,
            current_time=t(12, 0),
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=100.0,
            total_energy_used_today=10.0,
            device_priorities=BASE_PRIORITIES,
            scheduled_devices=[],
        )
        assert r1.energy_saving_mode is False
        r2 = manage_energy(
            current_price=0.10,
            price_threshold=0.20,
            current_time=t(12, 0),
            current_temperature=20.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=100.0,
            total_energy_used_today=10.0,
            device_priorities=BASE_PRIORITIES,
            scheduled_devices=[],
        )
        r3 = manage_energy(
            current_price=0.10,
            price_threshold=0.20,
            current_time=t(12, 0),
            current_temperature=24.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=100.0,
            total_energy_used_today=10.0,
            device_priorities=BASE_PRIORITIES,
            scheduled_devices=[],
        )
        assert r2.temperature_regulation_active is False
        assert r3.temperature_regulation_active is False

    def test_daily_limit_with_only_essentials_does_not_turn_off_anything(self):
        only_essentials = {"Security": 1, "Refrigerator": 1}
        res = manage_energy(
            current_price=0.10,
            price_threshold=0.20,
            current_time=t(16, 0),
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=5.0,
            total_energy_used_today=5.0,
            device_priorities=only_essentials,
            scheduled_devices=[],
        )
        assert res.device_status.get("Security") is True
        assert res.device_status.get("Refrigerator") is True

    def test_schedule_does_not_match_time_keeps_states(self):
        res = manage_energy(
            current_price=0.40,
            price_threshold=0.20,
            current_time=t(19, 0),
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=100.0,
            total_energy_used_today=10.0,
            device_priorities=BASE_PRIORITIES,
            scheduled_devices=[DeviceSchedule(device_name="Lights", scheduled_time=t(20, 0))],
        )
        assert res.energy_saving_mode is True
        assert res.device_status.get("Lights") is False

    def test_daily_limit_needs_more_cuts_than_available_devices_no_break(self):
        res = manage_energy(
            current_price=0.10,
            price_threshold=0.20,
            current_time=t(16, 0),
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=10.0,
            total_energy_used_today=13.0,
            device_priorities=BASE_PRIORITIES,
            scheduled_devices=[],
        )
        assert res.device_status.get("Security") is True
        assert res.device_status.get("Refrigerator") is True
        assert res.device_status.get("Lights") is False
        assert res.device_status.get("Washer") is False
