from datetime import datetime

class Transaction:
    """Representa uma unica transacao financeira."""
    def __init__(self, amount: float, timestamp: datetime, location: str):
        self.amount = amount
        self.timestamp = timestamp
        self.location = location

    def __repr__(self) -> str:
        """Retorna uma representacao legivel do objeto."""
        return f"Transaction(amount={self.amount}, timestamp='{self.timestamp}', location='{self.location}')"