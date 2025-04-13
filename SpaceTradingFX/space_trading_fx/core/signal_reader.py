import os

def read_signals(file_name="signals.txt"):
    """
    Reads trading signals from a file.
    Looks in the /data folder next to the project root.
    """
    # Get the path of the current file (signal_reader.py)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(base_dir, "data", file_name)

    signals = []

    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                if len(parts) == 3:
                    action, symbol, price = parts
                    signals.append({
                        "action": action.strip().upper(),
                        "symbol": symbol.strip().upper(),
                        "price": float(price.strip())
                    })
    except FileNotFoundError:
        print(f"[ERROR] Signal file not found: {file_path}")

    return signals
