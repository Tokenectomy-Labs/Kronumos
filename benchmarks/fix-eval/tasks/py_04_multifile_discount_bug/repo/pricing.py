def apply_percent_discount(amount: float, percent: float) -> float:
    if percent < 0 or percent > 100:
        raise ValueError("percent must be between 0 and 100")
    return amount - (amount * percent)
