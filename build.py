#!/usr/bin/env python3
"""
Immich Map Bilingual (Chinese + English) Style Generator
Features:
- Minimal patch on official Immich style.json (keeps official fonts & glyphs untouched)
- Chinese + English bilingual labels
- Generates style-light.json & style-dark.json
"""

import json
import os
import urllib.request

LIGHT_URL = "https://tiles.immich.cloud/v1/style/light.json"
DARK_URL = "https://tiles.immich.cloud/v1/style/dark.json"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..")) if os.path.basename(SCRIPT_DIR) == "scripts" else SCRIPT_DIR


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Immich-Map-Zhcn-Style-Builder/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def transform_bilingual_style(style_data: dict, theme: str) -> dict:
    style = json.loads(json.dumps(style_data))
    style["id"] = f"immich-map-{theme}-bilingual"
    style["name"] = f"Immich Map ({theme} - bilingual)"

    # Bilingual expression: Chinese + English if different, otherwise fallback to Chinese / English / local name
    zh_fallback = [
        "coalesce",
        ["get", "name:zh-Hans"],
        ["get", "name:zh"],
        ["get", "name:zh-Hant"],
        ["get", "name:en"],
        ["get", "name"],
    ]

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
        zh_fallback,
    ]

    for layer in style.get("layers", []):
        if layer.get("type") != "symbol":
            continue

        layer_id = layer.get("id", "")
        layout = layer.get("layout", {})
        if not layout or "text-field" not in layout:
            continue

        # Skip non-language layers
        if layer_id in ("address_label", "roads_oneway"):
            continue

        if layer_id == "places_region":
            layer["layout"]["text-field"] = [
                "step",
                ["zoom"],
                [
                    "coalesce",
                    ["get", "name:zh-Hans"],
                    ["get", "name:zh"],
                    ["get", "name:en"],
                    ["get", "name"],
                    ["get", "ref"],
                ],
                6,
                bilingual_expr,
            ]
        elif layer_id in ("water_waterway_label", "roads_labels_minor"):
            layer["layout"]["text-field"] = zh_fallback
        else:
            layer["layout"]["text-field"] = bilingual_expr

        # Remove uppercase transform for country layer
        if layer_id == "places_country" and "text-transform" in layer["layout"]:
            del layer["layout"]["text-transform"]

    return style


def main():
    print(f"Fetching official light theme from {LIGHT_URL}...")
    light_raw = fetch_json(LIGHT_URL)
    print(f"Fetching official dark theme from {DARK_URL}...")
    dark_raw = fetch_json(DARK_URL)

    targets = [
        ("style-light.json", transform_bilingual_style(light_raw, "light")),
        ("style-dark.json", transform_bilingual_style(dark_raw, "dark")),
    ]

    for filename, data in targets:
        dest = os.path.join(WORKSPACE_DIR, filename)
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved: {dest} ({os.path.getsize(dest)} bytes)")

    # Clean up old bilingual separate files if they exist
    for old_file in ("style-light-bilingual.json", "style-dark-bilingual.json"):
        old_path = os.path.join(WORKSPACE_DIR, old_file)
        if os.path.exists(old_path):
            os.remove(old_path)
            print(f"Removed legacy file: {old_file}")

    print("\nBilingual styles generated with minimal changes to official sources!")


if __name__ == "__main__":
    main()
