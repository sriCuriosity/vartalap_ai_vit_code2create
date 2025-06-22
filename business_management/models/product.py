from dataclasses import dataclass, field

@dataclass(frozen=True)
class Product:
    id: int
    name: str
    cost_price: float = 0.0
    stock_quantity: int = 0
    reorder_threshold: int = 0
    supplier_lead_time: int = 0
    category: str = 'Uncategorized' 