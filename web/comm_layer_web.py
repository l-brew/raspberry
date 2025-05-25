from flask import Flask, render_template, request, jsonify, redirect, url_for
import threading
import time

# Assume comm_layer is available and initialized elsewhere
# from comm_layer import Comm_layer

def create_app(comm_layer):
    """
    Factory function to create and configure the Flask web application.
    
    This function creates a Flask app with routes for monitoring and controlling
    the brewing process through a web interface.
    
    :param comm_layer: An instance of Comm_layer that provides brewing control logic
                      and communication with the brewing hardware.
    :return: Configured Flask application instance.
    """
    app = Flask(__name__)

    @app.route('/')
    def index():
        """
        Render the main dashboard page with current brewing status.
        
        This route fetches the current status from the comm_layer and passes
        it to the dashboard template for display.
        
        :return: Rendered HTML template with current brewing status.
        """
        status = comm_layer.get_status_dict()
        return render_template('dashboard.html', status=status)

    @app.route('/status')
    def status():
        """
        API endpoint that returns the current brewing status as JSON.
        
        This route is designed for AJAX requests to periodically update
        the dashboard without refreshing the entire page.
        
        :return: JSON object containing current brewing status parameters.
        """
        status = comm_layer.get_status_dict()
        return jsonify(status)

    @app.route('/set', methods=['POST'])
    def set_param():
        """
        Set a brewing parameter via POST request.
        
        This endpoint accepts form data with 'param' and 'value' fields,
        validates the input, and sends the command to the brewing system.
        
        :return: JSON response indicating success or failure with appropriate message.
        :status 400: If parameter or value is missing.
        :status 500: If an error occurs while setting the parameter.
        """
        param = request.form.get('param')
        value = request.form.get('value')
        if not param or value is None:
            return jsonify({'success': False, 'message': 'Missing parameter or value'}), 400
        try:
            comm_layer.command({param: value})
            return jsonify({'success': True, 'message': f'Set {param} to {value}'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/rampup2', methods=['POST'])
    def rampup2():
        """
        Special command to gradually increase temperature over time.
        
        This endpoint accepts 'temp' (target temperature) and 'minutes' (duration)
        parameters and sends a rampup2 command to the brewing system to gradually
        increase the temperature to the target over the specified time period.
        
        :return: JSON response indicating success or failure with appropriate message.
        :status 500: If an error occurs during command execution.
        """
        temp = request.form.get('temp')
        minutes = request.form.get('minutes')
        try:
            comm_layer.command({"rampup2": {"temp": float(temp), "minutes": float(minutes)}})
            return jsonify({'success': True, 'message': f'Ramping up to {temp}°C in {minutes} minutes.'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    return app


# Example usage:
# To run the web server:
# from comm_layer import Comm_layer
# start = ... # your start or start_simulation instance
# comm_layer = Comm_layer(start)
# app = create_app(comm_layer)
# app.run(host='0.0.0.0', port=8080, debug=True)
#
# The web interface provides:
# - Dashboard view at the root URL (/)
# - JSON status endpoint (/status) for AJAX updates
# - Parameter setting endpoint (/set) for controlling brewing parameters
# - Temperature ramping endpoint (/rampup2) for gradual temperature changes
