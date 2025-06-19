from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Bill:
    bill_number: int
    customer_key: str
    date: str
    items: List[Dict[str, Any]]
    total_amount: float
    transaction_type: str
    remarks: str = ""
