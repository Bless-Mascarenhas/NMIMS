"""
main.py - Entrypoint for the Smart Crops dashboard.

This file re-uses the Flask `app` defined in `crop_planner.py` and starts it.
Create this file so you have a clear "main" entrypoint to run the site:

    python main.py

The actual routes and API implementations live in `crop_planner.py`.
"""
from crop_planner import app


if __name__ == '__main__':
    # Start the Flask app from the crop_planner module
    # Bind to 127.0.0.1 and port 5000 (same as before)
    app.run(debug=True, host='127.0.0.1', port=5000)
