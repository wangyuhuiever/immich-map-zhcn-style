#!/usr/bin/env python3
"""
Immich Map Chinese Style Generator
Fetches official light & dark style.json from Immich and generates:
- style-light.json (Simplified Chinese first)
- style-dark.json (Simplified Chinese first)
- style-light-bilingual.json (Chinese + English bilingual)
- style-dark-bilingual.json (Chinese + English bilingual)
"""

import json
import os
import urllib.request

LIGHT_URL = "https://tiles.immich.cloud/v1/style/light.json"
DARK_URL = "https://tiles.immich.cloud/v1/style/dark.json"
GLYPHS_URL = "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..")) if os.path.basename(SCRIPT_DIR) == "scripts" else SCRIPT_DIR


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Immich-Map-Zhcn-Style-Builder/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def transform_style(style_data: dict, mode: str, theme: str) -> dict:
    # Deep copy
    style = json.loads(json.dumps(style_data))
    
    style["id"] = f"immich-map-{theme}-{mode}"
    style["name"] = f"Immich Map ({theme} - {mode})"
    
    # Use MapLibre official glyphs server containing full CJK PBF font glyphs
    # (Fixes the issue where mobile MapLibre Native cannot render Chinese due to empty PBFs on Immich static server)
    style["glyphs"] = GLYPHS_URL

    for layer in style.get("layers", []):
        if layer.get("type") != "symbol":
            continue

        layer_id = layer.get("id", "")
        layout = layer.get("layout", {})
        if not layout:
            continue

        # Adjust text-font: demotiles has Noto Sans Regular, Noto Sans Bold, Noto Sans Italic
        if "text-font" in layout:
            font = layout["text-font"]
            if font == ["Noto Sans Medium"]:
                layout["text-font"] = ["Noto Sans Bold"]
            elif isinstance(font, list) and len(font) == 5 and font[0] == "case":
                # ["case", ["<=", ["get", "min_zoom"], 5], ["literal", ["Noto Sans Medium"]], ["literal", ["Noto Sans Regular"]]]
                layout["text-font"] = [
                    "case",
                    ["<=", ["get", "min_zoom"], 5],
                    ["literal", ["Noto Sans Bold"]],
                    ["literal", ["Noto Sans Regular"]],
                ]

        if "text-field" not in layout:
            continue

        # Skip non-language layers
        if layer_id in ("address_label", "roads_oneway"):
            continue

        if mode == "zh-cn":
            # Simplified Chinese first
            if layer_id == "places_region":
                layer["layout"]["text-field"] = [
                    "step",
                    ["zoom"],
                    [
                        "coalesce",
                        ["get", "name:zh-Hans"],
                        ["get", "name:zh"],
                        ["get", "name:zh-Hant"],
                        ["get", "name"],
                        ["get", "ref"],
                    ],
                    6,
                    [
                        "coalesce",
                        ["get", "name:zh-Hans"],
                        ["get", "name:zh"],
                        ["get", "name:zh-Hant"],
                        ["get", "name"],
                        ["get", "name:en"],
                    ],
                ]
            else:
                layer["layout"]["text-field"] = [
                    "coalesce",
                    ["get", "name:zh-Hans"],
                    ["get", "name:zh"],
                    ["get", "name:zh-Hant"],
                    ["get", "name"],
                    ["get", "name:en"],
                ]
        elif mode == "bilingual":
            # Bilingual (Chinese + English if available and different)
            bilingual_expr = [
                "case",
                [
                    "all",
                    ["has", "name:zh-Hans"],
                    ["has", "name:en"],
                    ["!=", ["get", "name:zh-Hans"], ["get", "name:en"]],
                ],
                [
                    "concat",
                    ["get", "name:zh-Hans"],
                    "\n",
                    ["get", "name:en"],
                ],
                [
                    "coalesce",
                    ["get", "name:zh-Hans"],
                    ["get", "name:zh"],
                    ["get", "name:zh-Hant"],
                    ["get", "name"],
                    ["get", "name:en"],
                ],
            ]

            if layer_id == "places_region":
                layer["layout"]["text-field"] = [
                    "step",
                    ["zoom"],
                    [
                        "coalesce",
                        ["get", "name:zh-Hans"],
                        ["get", "name:zh"],
                        ["get", "name"],
                        ["get", "ref"],
                    ],
                    6,
                    bilingual_expr,
                ]
            elif layer_id in ("water_waterway_label", "roads_labels_minor"):
                layer["layout"]["text-field"] = [
                    "coalesce",
                    ["get", "name:zh-Hans"],
                    ["get", "name:zh"],
                    ["get", "name:zh-Hant"],
                    ["get", "name"],
                    ["get", "name:en"],
                ]
            else:
                layer["layout"]["text-field"] = bilingual_expr

        # Remove uppercase transform for country layer so Chinese characters are unmodified
        if layer_id == "places_country" and "text-transform" in layer["layout"]:
            del layer["layout"]["text-transform"]

    return style


def main():
    print(f"Fetching official light theme from {LIGHT_URL}...")
    light_raw = fetch_json(LIGHT_URL)
    print(f"Fetching official dark theme from {DARK_URL}...")
    dark_raw = fetch_json(DARK_URL)

    targets = [
        ("style-light.json", transform_style(light_raw, "zh-cn", "light")),
        ("style-dark.json", transform_style(dark_raw, "zh-cn", "dark")),
        ("style-light-bilingual.json", transform_style(light_raw, "bilingual", "light")),
        ("style-dark-bilingual.json", transform_style(dark_raw, "bilingual", "dark")),
    ]

    for filename, data in targets:
        dest = os.path.join(WORKSPACE_DIR, filename)
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved: {dest} ({os.path.getsize(dest)} bytes)")

    print("\nAll styles successfully generated with CJK PBF font support!")


if __name__ == "__main__":
    main()
