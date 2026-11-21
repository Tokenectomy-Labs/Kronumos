from pricing import apply_percent_discount


def checkout_total(items: list[tuple[float, int]], discount_pct: float = 0.0, tax_pct: float = 0.0) -> float:
    subtotal = sum(price * qty for price, qty in items)
    discounted = apply_percent_discount(subtotal, discount_pct)
    tax = discounted * (tax_pct / 100.0)
    return round(discounted + tax, 2)
