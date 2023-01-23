"""Scanner example"""

import config as cfg
from eodhd import ScannerClient


def main() -> None:
    """Main"""

    scanner = ScannerClient(cfg.API_KEY)
    df_data = scanner.scan_markets("CC", "1d", "USD", 5000)
    print(df_data)


if __name__ == "__main__":
    main()
