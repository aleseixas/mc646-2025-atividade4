import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta

import pytest

from src.flight.BookingResult import BookingResult
from src.flight.FlightBookingSystem import FlightBookingSystem


class TestFlightBookingSystem:
    now = datetime(2025, 10, 11, 21, 0, 0)

    def test_case_1_reserva_normal(self):
        result = FlightBookingSystem().book_flight(
            passengers=2,
            available_seats=10,
            reward_points_available=0,
            previous_sales=1000,
            current_price=500.0,
            booking_time=self.now,
            departure_time=self.now + timedelta(hours=30),
            is_cancellation=False,
        )
        assert result.confirmation is True
        assert result.points_used is False
        assert result.refund_amount == pytest.approx(0.0)
        # Checar essa saida
        assert result.total_price == pytest.approx(8000.0)

    def test_case_2_desconto_por_grupo(self):
        result = FlightBookingSystem().book_flight(
            passengers=5,
            available_seats=8,
            reward_points_available=0,
            previous_sales=500,
            current_price=400.0,
            booking_time=self.now,
            departure_time=self.now + timedelta(hours=50),
            is_cancellation=False,
        )
        assert result.confirmation is True
        assert result.points_used is False
        assert result.refund_amount == pytest.approx(0.0)
        # Checar essa saida
        assert result.total_price == pytest.approx(7600.0)

    def test_case_3_taxa_urgencia(self):
        result = FlightBookingSystem().book_flight(
            passengers=1,
            available_seats=3,
            reward_points_available=0,
            previous_sales=200,
            current_price=300.0,
            booking_time=self.now,
            departure_time=self.now + timedelta(hours=10),
            is_cancellation=False,
        )
        assert result.confirmation is True
        assert result.points_used is False
        assert result.refund_amount == pytest.approx(0.0)
        # Checar essa saida
        assert result.total_price == pytest.approx(580.0)

    def test_case_4_usa_pontos(self):
        result = FlightBookingSystem().book_flight(
            passengers=3,
            available_seats=5,
            reward_points_available=10000,
            previous_sales=800,
            current_price=200.0,
            booking_time=self.now,
            departure_time=self.now + timedelta(hours=25),
            is_cancellation=False,
        )
        assert result.confirmation is True
        assert result.points_used is True
        assert result.refund_amount == pytest.approx(0.0)
        # Checar essa saida
        assert result.total_price == pytest.approx(3740.0)

    def test_case_5_preco_negativo_ajustado(self):
        result = FlightBookingSystem().book_flight(
            passengers=3,
            available_seats=5,
            reward_points_available=999999,
            previous_sales=800,
            current_price=200.0,
            booking_time=self.now,
            departure_time=self.now + timedelta(hours=25),
            is_cancellation=False,
        )
        assert result.confirmation is True
        assert result.points_used is True
        assert result.refund_amount == pytest.approx(0.0)
        assert result.total_price == pytest.approx(0.0)

    def test_case_6_sem_assentos(self):
        result = FlightBookingSystem().book_flight(
            passengers=5,
            available_seats=3,
            reward_points_available=0,
            previous_sales=600,
            current_price=400.0,
            booking_time=self.now,
            departure_time=self.now + timedelta(hours=40),
            is_cancellation=False,
        )
        assert result.confirmation is False
        assert result.points_used is False
        assert result.refund_amount == pytest.approx(0.0)
        assert result.total_price == pytest.approx(0.0)

    def test_case_7_cancelamento_reembolso_total(self):
        result = FlightBookingSystem().book_flight(
            passengers=2,
            available_seats=10,
            reward_points_available=0,
            previous_sales=500,
            current_price=400.0,
            booking_time=self.now,
            departure_time=self.now + timedelta(hours=100),
            is_cancellation=True,
        )
        assert result.confirmation is False
        assert result.points_used is False
        # Checar essa saida
        assert result.refund_amount == pytest.approx(3200.0)
        assert result.total_price == pytest.approx(0.0)

    def test_case_8_cancelamento_reembolso_parcial(self):
        result = FlightBookingSystem().book_flight(
            passengers=2,
            available_seats=10,
            reward_points_available=0,
            previous_sales=500,
            current_price=400.0,
            booking_time=self.now,
            departure_time=self.now + timedelta(hours=30),
            is_cancellation=True,
        )
        assert result.confirmation is False
        assert result.points_used is False
        # Checar essa saida
        assert result.refund_amount == pytest.approx(1600.0)
        assert result.total_price == pytest.approx(0.0)