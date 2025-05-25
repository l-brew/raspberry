# Brewing Control Web Interface

This module provides a Flask-based web interface for monitoring and controlling your brewing process.

## Features

- **Live Dashboard:** View all brewing parameters in real time.
- **Parameter Control:** Set any parameter directly from the web UI.
- **Special Commands:** Use forms for advanced actions like ramping up temperature.
- **Responsive Design:** Clean, modern look using Bootstrap (served locally).

## Setup

1. **Install dependencies:**
   ```
   pip install flask
   ```

2. **Place Bootstrap CSS:**
   - Download `bootstrap.min.css` (e.g., from [getbootstrap.com](https://getbootstrap.com/)) and place it in `web/static/css/bootstrap.min.css`.

3. **Templates and Static Files:**
   - Ensure `dashboard.html` is in `web/templates/`.
   - Ensure the CSS file is in `web/static/css/`.

4. **Integration:**
   - In your `start_simulation.py` (or main script), add:
     ```python
     from web.comm_layer_web import create_app
     from comm_layer import Comm_layer
     # ... your simulation setup ...
     comm_layer = Comm_layer(start)
     app = create_app(comm_layer)
     app.run(host='0.0.0.0', port=8080)
     ```

   - Or, to run the web server in a background thread:
     ```python
     import threading
     def run_web():
         app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
     threading.Thread(target=run_web, daemon=True).start()
     ```

## Usage

- Open your browser and go to [http://localhost:8080](http://localhost:8080)
- The dashboard will display all current parameters.
- Use the input fields to set new values.
- Use the special command form for ramping up temperature.

## Endpoints

- `/` : Main dashboard (HTML)
- `/status` : JSON status (for AJAX updates)
- `/set` : POST endpoint to set a parameter
- `/rampup2` : POST endpoint for ramp-up command

## Notes

- The web interface requires a running `Comm_layer` instance.
- All parameter changes are immediately sent to the backend.