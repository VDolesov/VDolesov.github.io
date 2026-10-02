import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
SRC = os.path.join(SITE, "v1", "assets", "products")
OUT = os.path.join(SITE, "assets", "products")
SERIES = "v9"

PIES = {"736": "v10", "737": "v10", "738": "v10", "739": "v10", "741": "v10", "772": "v10",
        "773": "v10", "774": "v10", "775": "v10", "776": "v10", "801": "v9", "802": "v9", "803": "v9"}


def main():
    for pid, series in PIES.items():
        for size in ("", "-640", "-2048"):
            src = os.path.join(SRC, f"pies-{pid}-{series}{size}.webp")
            if os.path.exists(src):
                shutil.copyfile(src, os.path.join(OUT, f"{pid}-{SERIES}{size}.webp"))
        print(f"  {pid}: from v1")


if __name__ == "__main__":
    main()
