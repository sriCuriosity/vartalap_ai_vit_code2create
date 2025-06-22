from dataclasses import dataclass

@dataclass
class Expense:
    id: int
    date: str
    amount: float
    category: str
    description: str = "" 