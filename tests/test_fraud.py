import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta

from src.fraud.Transaction import Transaction
from src.fraud.FraudDetectionSystem import FraudDetectionSystem



AMOUNT_THRESHOLD = 10000
TIME_DIFF_THRESHOLD = 60
TIME_DIFF_THRESHOLD_FOR_LOCATION = 30
TRANSACTION_WITHIN_AMOUNT = Transaction(
    amount=AMOUNT_THRESHOLD,
    timestamp=datetime.now(),
    location="SP"
)
TRANSACTION_OUTSIDE_AMOUNT = Transaction(
    amount=AMOUNT_THRESHOLD + 1,
    timestamp=datetime.now(),
    location="SP"
)
TRANSACTION_MORE_THAN_ONE_HOUR_AGO = Transaction(
    amount=AMOUNT_THRESHOLD,
    timestamp=datetime.now() - timedelta(minutes=TIME_DIFF_THRESHOLD + 1),
    location="SP"
)
TRANSACTION_LESS_THAN_HALF_AN_HOUR_AGO = Transaction(
    amount=AMOUNT_THRESHOLD,
    timestamp=datetime.now() - timedelta(minutes=TIME_DIFF_THRESHOLD_FOR_LOCATION - 1),
    location="SP"
)
TRANSACTION_LESS_THAN_HALF_AN_HOUR_AGO_DIFFERENT_LOCATION = Transaction(
    amount=AMOUNT_THRESHOLD,
    timestamp=datetime.now() - timedelta(minutes=TIME_DIFF_THRESHOLD_FOR_LOCATION - 1),
    location="RJ"
)

class TestFraudDetectionSystem:
    def test_case_1_curr_transaction_amount_below_threshold(self):
        result = FraudDetectionSystem().check_for_fraud(
            current_transaction=TRANSACTION_WITHIN_AMOUNT,
            previous_transactions=[],
            blacklisted_locations=[]
        )
        assert result.is_blocked == False
        assert result.is_fraudulent == False
        assert result.verification_required == False
        assert result.risk_score == 0

    def test_case_2_curr_transaction_amount_above_threshold(self):
        result = FraudDetectionSystem().check_for_fraud(
            current_transaction=TRANSACTION_OUTSIDE_AMOUNT,
            previous_transactions=[],
            blacklisted_locations=[]
        )
        assert result.is_blocked == False
        assert result.is_fraudulent == True
        assert result.verification_required == True
        assert result.risk_score == 50

    def test_case_3_previous_transaction_more_than_1h_ago(self):
        result = FraudDetectionSystem().check_for_fraud(
            current_transaction=TRANSACTION_WITHIN_AMOUNT,
            previous_transactions=[TRANSACTION_MORE_THAN_ONE_HOUR_AGO],
            blacklisted_locations=[]
        )
        assert result.is_blocked == False
        assert result.is_fraudulent == False
        assert result.verification_required == False
        assert result.risk_score == 0

    def test_case_4_previous_transaction_within_1h(self):
        result = FraudDetectionSystem().check_for_fraud(
            current_transaction=TRANSACTION_WITHIN_AMOUNT,
            previous_transactions=[TRANSACTION_LESS_THAN_HALF_AN_HOUR_AGO],
            blacklisted_locations=[]
        )
        assert result.is_blocked == False
        assert result.is_fraudulent == False
        assert result.verification_required == False
        assert result.risk_score == 0

    def test_case_6_11_previous_transactions_within_1h(self):
        result = FraudDetectionSystem().check_for_fraud(
            current_transaction=TRANSACTION_WITHIN_AMOUNT,
            previous_transactions=[TRANSACTION_LESS_THAN_HALF_AN_HOUR_AGO] * 11,
            blacklisted_locations=[]
        )
        assert result.is_blocked == True
        assert result.is_fraudulent == False
        assert result.verification_required == False
        assert result.risk_score == 30

    def test_case_12_location_change_less_than_30_minutes(self):
        result = FraudDetectionSystem().check_for_fraud(
            current_transaction=TRANSACTION_WITHIN_AMOUNT,
            previous_transactions=[TRANSACTION_LESS_THAN_HALF_AN_HOUR_AGO_DIFFERENT_LOCATION],
            blacklisted_locations=[]
        )
        assert result.is_blocked == False
        assert result.is_fraudulent == True
        assert result.verification_required == True
        assert result.risk_score == 20
    
    def test_case_14_blacklisted_location(self):
        result = FraudDetectionSystem().check_for_fraud(
            current_transaction=TRANSACTION_WITHIN_AMOUNT,
            previous_transactions=[],
            blacklisted_locations=["SP"]
        )
        assert result.is_blocked == True
        assert result.is_fraudulent == False
        assert result.verification_required == False
        assert result.risk_score == 100