def format_number(value, unit=None, is_percent=False, is_currency=False):

    if not isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (int, float)) and 1000 <= value <= 2100 and float(value).is_integer():
        return str(int(value))

    abs_val = abs(value)
    suffix = ""
    scaled_val = value

    special_units = {
        "watt": "w", "tons": "t", "bits": "b", "bytes": "B"
    }

    if abs_val >= 1_000_000_000:
        scaled_val = value / 1_000_000_000
        suffix = "B"
    elif abs_val >= 1_000_000:
        scaled_val = value / 1_000_000
        suffix = "M"
    elif abs_val >= 10_000:
        scaled_val = value / 1_000
        suffix = "K"

    if unit in special_units:
        suffix = suffix.replace("B", f"G{special_units[unit]}")
        suffix = suffix.replace("M", f"M{special_units[unit]}")
        suffix = suffix.replace("K", f"K{special_units[unit]}")
    elif unit:
        suffix = suffix + unit

    abs_scaled = abs(scaled_val)

    if isinstance(value, int) or float(value).is_integer():
        fmt = "{:.0f}"
    else:
        if abs_scaled < 1:
            fmt = "{:.2f}"
        elif abs_scaled < 100:
            fmt = "{:.1f}"
        else:
            fmt = "{:.0f}"

    number_str = fmt.format(scaled_val)

    if suffix == "" and abs_val >= 1000:
        number_str = "{:,.0f}".format(value)

    if is_currency:
        number_str = f"${number_str}"
    if is_percent:
        number_str = f"{number_str}%"

    return f"{number_str}{suffix}"
