def create_loading_bar(current, total, length=20):
    percentage = current / total
    filled_length = int(length * percentage)
    
    filled = '🟩' * filled_length
    empty = '⬜' * (length - filled_length)
    
    bar = f"{filled}{empty}"
    return f"[{bar}] {current}/{total}"