def format_money(value: float) -> str:
    value = float(value)

    abs_value = abs(value)

    if abs_value >= 1e7:
        return f"₹{value / 1e7:.2f} Cr"

    if abs_value >= 1e5:
        return f"₹{value / 1e5:.2f} L"

    if abs_value >= 1e3:
        return f"₹{value / 1e3:.2f} K"

    return f"₹{value:.2f}"