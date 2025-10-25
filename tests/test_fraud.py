import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta

from src.fraud.Transaction import Transaction
from src.fraud.FraudDetectionSystem import FraudDetectionSystem


NOW = datetime.now() # Kill mutant 86
AMOUNT_THRESHOLD = 10000
TIME_DIFF_THRESHOLD = 60
TIME_DIFF_THRESHOLD_FOR_LOCATION = 30
TRANSACTION_WITHIN_AMOUNT = Transaction(
    amount=AMOUNT_THRESHOLD,
    timestamp=NOW,
    location="SP"
)
TRANSACTION_OUTSIDE_AMOUNT = Transaction(
    amount=AMOUNT_THRESHOLD + 1,
    timestamp=NOW,
    location="SP"
)
TRANSACTION_MORE_THAN_1H_AGO = Transaction( # Para que a mudanca no mutante 89 seja detectada
    amount=AMOUNT_THRESHOLD,
    timestamp=NOW - timedelta(minutes=TIME_DIFF_THRESHOLD + 1),
    location="SP"
)
TRANSACTION_EXACTLY_1H_AGO = Transaction( # Para que a mudanca no mutante 88 seja detectada
    amount=AMOUNT_THRESHOLD,
    timestamp=NOW - timedelta(minutes=TIME_DIFF_THRESHOLD),
    location="SP"
)
TRANSACTION_EXACTLY_30MIN_AGO_DIFF_LOCATION = Transaction(
    amount=AMOUNT_THRESHOLD,
    timestamp=NOW - timedelta(minutes=TIME_DIFF_THRESHOLD_FOR_LOCATION),
    location="RJ"
)
TRANSACTION_LESS_THAN_30MIN_AGO = Transaction(
    amount=AMOUNT_THRESHOLD,
    timestamp=NOW - timedelta(minutes=TIME_DIFF_THRESHOLD_FOR_LOCATION - 1),
    location="SP"
)
TRANSACTION_LESS_THAN_30MIN_AGO_DIFF_LOCATION = Transaction(
    amount=AMOUNT_THRESHOLD,
    timestamp=NOW - timedelta(minutes=TIME_DIFF_THRESHOLD_FOR_LOCATION - 1),
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
            previous_transactions=[TRANSACTION_MORE_THAN_1H_AGO],
            blacklisted_locations=[]
        )
        assert result.is_blocked == False
        assert result.is_fraudulent == False
        assert result.verification_required == False
        assert result.risk_score == 0

    def test_case_4_previous_transaction_within_1h(self):
        result = FraudDetectionSystem().check_for_fraud(
            current_transaction=TRANSACTION_WITHIN_AMOUNT,
            previous_transactions=[TRANSACTION_LESS_THAN_30MIN_AGO],
            blacklisted_locations=[]
        )
        assert result.is_blocked == False
        assert result.is_fraudulent == False
        assert result.verification_required == False
        assert result.risk_score == 0

    def test_case_6_11_previous_transactions_within_1h(self):
        result = FraudDetectionSystem().check_for_fraud(
            current_transaction=TRANSACTION_WITHIN_AMOUNT,
            previous_transactions=[TRANSACTION_LESS_THAN_30MIN_AGO] * 11,
            blacklisted_locations=[]
        )
        assert result.is_blocked == True
        assert result.is_fraudulent == False
        assert result.verification_required == False
        assert result.risk_score == 30

    def test_case_12_location_change_less_than_30min(self):
        result = FraudDetectionSystem().check_for_fraud(
            current_transaction=TRANSACTION_WITHIN_AMOUNT,
            previous_transactions=[TRANSACTION_LESS_THAN_30MIN_AGO_DIFF_LOCATION],
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
    
    def test_killmut_81_92_and_93_transactions_bellow_sus_transactions_count(self):
        result = FraudDetectionSystem().check_for_fraud(
            current_transaction=TRANSACTION_WITHIN_AMOUNT,
            previous_transactions=[TRANSACTION_LESS_THAN_30MIN_AGO] * 10, # para que a mudanca nos mutantes seja detectada
            blacklisted_locations=[]
        )
        assert result.is_blocked == False
        assert result.is_fraudulent == False
        assert result.verification_required == False
        assert result.risk_score == 0
    
    def test_killmut_86_and_89_count_prev_transactions_more_than_1h_ago_above_sus_count(self):
        result = FraudDetectionSystem().check_for_fraud(
            current_transaction=TRANSACTION_WITHIN_AMOUNT,
            previous_transactions=[TRANSACTION_MORE_THAN_1H_AGO] * 11, # para que a mudanca no mut seja detectada
            blacklisted_locations=[]
        )
        assert result.is_blocked == False
        assert result.is_fraudulent == False
        assert result.verification_required == False
        assert result.risk_score == 0
    
    def test_killmut_88_count_prev_transactions_exactly_1h_ago_above_sus_count(self):
        result = FraudDetectionSystem().check_for_fraud(
            current_transaction=TRANSACTION_WITHIN_AMOUNT,
            previous_transactions=[TRANSACTION_EXACTLY_1H_AGO] * 11, # para que a mudanca no mut seja detectada
            blacklisted_locations=[]
        )
        assert result.is_blocked == True
        assert result.is_fraudulent == False
        assert result.verification_required == False
        assert result.risk_score == 30

    def test_killmut_97_and_116_curr_transaction_outside_amount_prev_above_sus_count_and_diff_location(self):
        result = FraudDetectionSystem().check_for_fraud(
            current_transaction=TRANSACTION_OUTSIDE_AMOUNT,
            previous_transactions=[TRANSACTION_LESS_THAN_30MIN_AGO_DIFF_LOCATION] * 11,
            blacklisted_locations=[]
        )
        assert result.is_blocked == True
        assert result.is_fraudulent == True
        assert result.verification_required == True
        assert result.risk_score == 100

    def test_killmut_106_108_and_109_transaction_exactly_30min_ago_diff_location(self):
        result = FraudDetectionSystem().check_for_fraud(
            current_transaction=TRANSACTION_WITHIN_AMOUNT,
            previous_transactions=[TRANSACTION_EXACTLY_30MIN_AGO_DIFF_LOCATION],
            blacklisted_locations=[]
        )
        assert result.is_blocked == False
        assert result.is_fraudulent == False
        assert result.verification_required == False
        assert result.risk_score == 0