import os
import sys

REQUIRED_VARS = [
    "API_KEY", "API_SECRET", "SYMBOL", "TRADE_AMOUNT"
]

def validate_env():
    missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
    if missing:
        print(f"Missing required env vars: {', '.join(missing)}")
        sys.exit(1)
    else:
        print("All required env vars are set.")

if __name__ == "__main__":
    validate_env()