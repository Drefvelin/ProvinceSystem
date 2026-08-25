from ..util.dirs import defines_file, validate_map
import os


def load_province_metadata(map_name: str) -> dict[int, dict]:
    """
    Loads province metadata keyed by province_id.
    Supports formats like:
      1 = 255,0,0;plains;42
      2 = 0,255,0;mountain;fertility=15
    """
    validate_map(map_name)

    province_file_path = defines_file(map_name, "provinces.txt")
    metadata: dict[int, dict] = {}

    if not os.path.exists(province_file_path):
        raise FileNotFoundError(
            f"provinces.txt not found for map '{map_name}'"
        )

    with open(province_file_path, "r", encoding="utf-8") as file:
        for line_num, line in enumerate(file, start=1):
            line = line.strip()

            if not line or line.startswith("##"):
                continue

            try:
                pid_str, rest = line.split("=", 1)
                pid = int(pid_str.strip())

                parts = [p.strip() for p in rest.split(";")]

                # parts[0] is RGB, ignore
                meta: dict = {}

                # Remaining parts: terrain, fertility, or key=value
                for part in parts[1:]:
                    if not part:
                        continue

                    # Explicit key=value
                    if "=" in part:
                        k, v = part.split("=", 1)
                        meta[k] = int(v) if v.isdigit() else v
                        continue

                    # Bare numeric → fertility
                    if part.isdigit():
                        meta["fertility"] = int(part)
                        continue

                    # Otherwise assume terrain
                    meta["terrain"] = part

                metadata[pid] = meta

            except Exception as e:
                raise ValueError(
                    f"Invalid line in {province_file_path} "
                    f"(line {line_num}): {line}"
                ) from e

    return metadata