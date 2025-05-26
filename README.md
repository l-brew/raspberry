# Brewing Control System 

## Table of Contents
- [Brewing Control System](#brewing-control-system)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Architecture](#architecture)
  - [Module Descriptions](#module-descriptions)
    - [Core Control \& Communication](#core-control--communication)
      - [`terminal/comm_layer_terminal.py`](#terminalcomm_layer_terminalpy)
      - [`http_comm.py`](#http_commpy)
      - [`socket_comm.py`](#socket_commpy)
      - [`start.py`](#startpy)
    - [Sensors \& Actuators](#sensors--actuators)
      - [`pt100.py`, `pt100_2.py`](#pt100py-pt100_2py)
      - [`ntc.py`](#ntcpy)
      - [`sensor.py`](#sensorpy)
      - [`dummySensor.py`](#dummysensorpy)
      - [`relay_ctrl.py`](#relay_ctrlpy)
      - [`stirrer.py`](#stirrerpy)
    - [Controllers](#controllers)
      - [`pid.py`](#pidpy)
      - [`two_point_control.py`](#two_point_controlpy)
    - [Utilities \& Support](#utilities--support)
      - [`timer.py`](#timerpy)
      - [`sysinfo.py`](#sysinfopy)
      - [`ScanUtility.py`](#scanutilitypy)
    - [Tilt Hydrometer Integration](#tilt-hydrometer-integration)
      - [`tilt2_client.py`](#tilt2_clientpy)
      - [`tilt2_server.py`](#tilt2_serverpy)
      - [`tilt2_bleak.py`](#tilt2_bleakpy)
      - [`tilt2_test.py`](#tilt2_testpy)
    - [Data Logging](#data-logging)
      - [`dataLogger.py`](#dataloggerpy)
      - [`testDataLogger.py`](#testdataloggerpy)
    - [Testing \& Debugging](#testing--debugging)
      - [`dbg.py`](#dbgpy)
    - [Web Interface](#web-interface)
      - [`web/comm_layer_web.py`](#webcomm_layer_webpy)
      - [`web/templates/dashboard.html`](#webtemplatesdashboardhtml)
      - [`web/static/css/bootstrap.min.css`](#webstaticcssbootstrapmincss)
      - [`web/README.md`](#webreadmemd)
  - [Extending the System](#extending-the-system)
  - [Running the System](#running-the-system)
  - [Configuration](#configuration)
  - [UML](#uml)


## Overview

This project is a modular, extensible brewing control system that runs on a raspberry pi. It supports real-time monitoring and control of brewing hardware, secure communication with remote servers, and integration with various sensors and actuators. The system is designed for robustness, thread safety, and easy extensibility.

---

## Architecture

The system is organized into the following layers:

- **Core Control & Communication:** Handles the main control logic, server communication, and socket interfaces.
- **Controllers:** Implements PID and two-point control algorithms for temperature regulation.
- **Sensors & Actuators:** Provides drivers and interfaces for temperature sensors, relays, stirrers, and other hardware.
- **Utilities & Support:** Includes system information, timers, and scanning utilities.
- **Testing & Debugging:** Contains modules for debugging, testing, and data logging.
- **Web Interface:** Provides a Flask-based web dashboard for real-time monitoring and control via browser.

<!-- Rest of your overview content -->
---

## Module Descriptions

### Core Control & Communication

#### `terminal/comm_layer_terminal.py`
- **Class: CommLayerTerminal**
  - Provides a terminal-based interface for interacting with the brewing control system.
  - **Attributes:** `start` (hardware/control logic reference)
  - **Methods:**
    - `__init__(start)`
    - `run()`
    - `handle_command(command: str)`
    - `get_status()`
  - **Description:**  
    Allows users to monitor and control the brewing system directly from the terminal, useful for headless setups or debugging without a web interface.

#### `http_comm.py`
- **Class: http_comm**
  - Handles HTTPS communication with the remote server.
  - **Attributes:** `server_config`, `comm`, `ssl_context`, `lock`
  - **Methods:**
    - `__init__(server_config, comm)`
    - `run()`
    - `update()`
    - `listenToServer()`
    - `fullStatus()`
    - `escape(s)`

#### `socket_comm.py`
- **Class: socket_comm**
  - Manages local socket-based communication for real-time control or monitoring.
  - **Attributes:** `host`, `port`, `comm_layer`
  - **Methods:**
    - `__init__(host, port, comm_layer)`
    - `run()`
    - `send(data)`
    - `receive()`

#### `start.py`
- **Functionality:** Entry point for initializing and starting the brewing control system.
  - Initializes hardware, communication layers, and starts main loops.

---

### Sensors & Actuators

#### `pt100.py`, `pt100_2.py`
- **Class: PT100 / PT100_2**
  - Driver for PT100 temperature sensors.
  - **Attributes:** `channel`, `calibration`
  - **Methods:**
    - `__init__(channel, calibration)`
    - `read_temperature()`

#### `ntc.py`
- **Class: NTC**
  - Driver for NTC thermistors.
  - **Attributes:** `pin`, `beta`, `r0`
  - **Methods:**
    - `__init__(pin, beta, r0)`
    - `read_temperature()`

#### `sensor.py`
- **Class: Sensor**
  - Abstract base class/interface for all sensors.
  - **Methods:**
    - `read()`

#### `dummySensor.py`
- **Class: DummySensor**
  - Simulated sensor for testing.
  - **Methods:**
    - `read()`

#### `relay_ctrl.py`
- **Class: RelayCtrl**
  - Controls relay switches for actuators (heaters, pumps, etc.).
  - **Attributes:** `relay_pins`
  - **Methods:**
    - `__init__(relay_pins)`
    - `set_state(relay, state)`
    - `get_state(relay)`

#### `stirrer.py`
- **Class: Stirrer**
  - Controls a motorized stirrer.
  - **Attributes:** `pin`, `speed`
  - **Methods:**
    - `__init__(pin)`
    - `set_speed(speed)`
    - `start()`
    - `stop()`

---

### Controllers

#### `pid.py`
- **Class: PID**
  - Implements a PID controller for temperature or process control.
  - **Attributes:** `kp`, `ki`, `kd`, `setpoint`, `output_limits`
  - **Methods:**
    - `__init__(kp, ki, kd, setpoint, output_limits)`
    - `compute(measurement)`
    - `reset()`

#### `two_point_control.py`
- **Class: TwoPointControl**
  - Implements a simple on/off (bang-bang) controller.
  - **Attributes:** `setpoint`, `hysteresis`
  - **Methods:**
    - `__init__(setpoint, hysteresis)`
    - `compute(measurement)`

### Utilities & Support

#### `timer.py`
- **Class: Timer**
  - Provides timing utilities for scheduling and delays.
  - **Methods:**
    - `start()`
    - `stop()`
    - `elapsed()`

#### `sysinfo.py`
- **Functionality:** Gathers system information (CPU, memory, uptime) for diagnostics and status reporting.

#### `ScanUtility.py`
- **Class: ScanUtility**
  - Provides device or network scanning utilities.
  - **Methods:**
    - `scan_devices()`
    - `scan_network()`

---

### Tilt Hydrometer Integration

#### `tilt2_client.py`
- **Class: Tilt2Client**
  - Communicates with Tilt hydrometers via BLE.
  - **Methods:**
    - `scan()`
    - `get_reading()`

#### `tilt2_server.py`
- **Class: Tilt2Server**
  - Provides a server interface for Tilt hydrometer data.
  - **Methods:**
    - `start_server()`
    - `handle_request()`

#### `tilt2_bleak.py`
- **Functionality:** BLE communication utilities for Tilt hydrometers.

#### `tilt2_test.py`
- **Functionality:** Test suite or script for Tilt hydrometer integration.

---

### Data Logging

#### `dataLogger.py`
- **Class: DataLogger**
  - Logs sensor and process data to file or database.
  - **Attributes:** `filename`, `buffer`
  - **Methods:**
    - `__init__(filename)`
    - `log(data)`
    - `flush()`

#### `testDataLogger.py`
- **Functionality:** Test suite or script for data logging functionality.

---

### Testing & Debugging

#### `dbg.py`
- **Functionality:** Debugging utilities, logging, or interactive debugging tools.

---

### Web Interface

#### `web/comm_layer_web.py`
- **Functionality:** Flask web server providing a dashboard for real-time monitoring and control.
  - **Endpoints:**
    - `/` : Main dashboard (HTML)
    - `/status` : JSON status (for AJAX updates)
    - `/set` : POST endpoint to set a parameter
    - `/rampup2` : POST endpoint for ramp-up command
  - **Integration:** Uses `Comm_layer` for backend logic.

#### `web/templates/dashboard.html`
- **Functionality:** Jinja2 HTML template for the dashboard UI.

#### `web/static/css/bootstrap.min.css`
- **Functionality:** Local Bootstrap CSS for styling the web interface.

#### `web/README.md`
- **Functionality:** Documentation for the web interface module.

---

## Extending the System

- **Add new sensors:** Implement a new class in `sensor.py` and register it in the appropriate communication layer.
- **Add new actuators:** Extend `relay_ctrl.py` or create a new actuator module.
- **Add new control logic:** Implement new controllers in `pid.py` or `two_point_control.py`.
- **Integrate new communication protocols:** Add modules similar to `http_comm.py` or `socket_comm.py`.
- **Add web features:** Extend `web/comm_layer_web.py` and `dashboard.html` for new controls or visualizations.

---

## Running the System

The system automatically detects whether it's running on a Raspberry Pi or a PC:

- On a **PC**: The system will use simulation modules for sensors and actuators
- On a **Raspberry Pi**: The system will use hardware modules to interface with real sensors and actuators

Start the application with:
```sh
python3 start.py
```

Make sure to adjust the configuration in `config/temp_reg.config` as needed for your environment before starting the system.

---

## Configuration

The system uses a configuration file located at `config/temp_reg.config` to set controller parameters and server settings.

Example configuration:
```ini
[Controller]
type = pid
setpoint = 10.0
hysteresis = 0.5
ramp = 0
k_p = 20.0
k_i = 0.02
ctlperiod = 30
dead_time = 600

[Server]
server_address = server_url
```

- **Controller** section: Sets the controller type (pid or two-point), setpoint temperature, PID parameters, and timing settings.
- **Server** section: Configures the remote server address for communication.


## UML

![UML](docs/brewing_control_system_uml.svg)