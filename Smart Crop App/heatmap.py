"""Minimal heatmap data provider used by the dashboard backend.

This module intentionally does NOT create a Flask app. It only exposes a
function `get_heatmap_data()` which returns mock heatmap entries. This keeps
imports safe (no side-effects) when other modules import `heatmap`.
"""

def get_heatmap_data():
    """Return a small list of mock heatmap items."""
    return [
        {"region": "Punjab", "level": "high", "description": "High Risk - Leaf Blight"},
        {"region": "Uttar Pradesh", "level": "medium", "description": "Medium Risk - Rust"},
        {"region": "Maharashtra", "level": "low", "description": "Low Risk - All Clear"}
    ]


if __name__ == '__main__':
    # Allow running this module directly for a quick smoke-test.
    # Prints JSON to stdout and exits with code 0.
    import json
    print(json.dumps(get_heatmap_data(), indent=2))
