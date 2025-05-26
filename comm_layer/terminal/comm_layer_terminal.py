import socket
import threading
import traceback
from typing import Optional
from comm_layer.comm_layer import Comm_layer


# Help text displayed when user types 'help' command
HELP_TEXT = """
Brewing Control Terminal - Command Reference

General usage:
  set <parameter> <value>    Set a parameter (e.g., set set_point 65)
  get <parameter>            Get a parameter value (e.g., get temp)
  reg <on|off>               Enable or disable regulation
  heater <on|off|tgl>        Control heater relay
  cooler <on|off|tgl>        Control cooler relay
  stirrer <off|duty>         Stop stirrer or set duty cycle (0-100)
  ramp <value>               Set ramp rate (°C/min)
  period <seconds>           Set control period in seconds
  freeze <true|false>        Freeze or unfreeze PID
  i_err <value>              Set integral error
  setI <value>               Set integral error (scaled by K_i)
  rampup2 <temp> <minutes>   Ramp up to temp in minutes
  reset                      Reset integral error
  status                     Show all status values
  help                       Show this help message
  quit / exit                Disconnect

Parameters:
  set_point, soll, k_p, k_i, ramp, period, i_err, setI, freeze, reg, heater, cooler, stirrer, rampup2, reset

Examples:
  set set_point 65
  get temp
  reg on
  heater tgl
  stirrer 50
  ramp 1.5
  period 1800
  freeze true
  status

"""

class CommLayerTerminalServer:
    """
    Socket-based terminal server for interacting with the Comm_layer.
    Allows users to connect via telnet/netcat and issue commands to control and query the brewing system.
    """

    def __init__(self, comm_layer: Comm_layer, host: str = '0.0.0.0', port: int = 5555) -> None:
        """
        Initialize the terminal server.

        Args:
            comm_layer: An instance of Comm_layer to control/query.
            host: Host/IP to bind the server socket (default: all interfaces).
            port: TCP port to listen on (default: 5555).
        """
        self.comm_layer = comm_layer
        self.host = host
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.running: bool = False

    def start(self) -> None:
        """
        Start the terminal server and listen for incoming socket connections.
        Each client is handled in a separate thread.
        """
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow socket reuse to avoid "address already in use" errors
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)  # Queue up to 5 connection requests
        print(f"CommLayer Terminal Server listening on {self.host}:{self.port}")
        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()
                print(f"Connection from {addr}")
                # Handle each client in a separate thread
                threading.Thread(target=self.handle_client, args=(client_sock,), daemon=True).start()
            except Exception as e:
                print(f"Error accepting connection: {e}")

    def stop(self) -> None:
        """
        Stop the terminal server and close the socket.
        """
        self.running = False
        if self.server_socket:
            self.server_socket.close()

    def handle_client(self, client_sock: socket.socket) -> None:
        """
        Handle a single client connection: receive commands, process them, and send responses.
        (No up-arrow/down-arrow command history navigation.)

        Args:
            client_sock: The socket object for the connected client.
        """
        try:
            # Send welcome message
            client_sock.sendall(b"Welcome to Brewing Control Terminal!\nType 'help' for available commands.\n> ")
            buffer = ""
            history = []
            while True:
                data = client_sock.recv(1024)
                if not data:  # Connection closed by client
                    break
                chars = data.decode(errors="ignore")
                i = 0
                while i < len(chars):
                    c = chars[i]
                    if c == '\x7f':  # Backspace
                        if buffer:
                            buffer = buffer[:-1]
                            client_sock.sendall(b'\b \b')
                        i += 1
                        continue
                    elif c == '\r' or c == '\n':
                        # If this is \r and next is \n, skip the \n
                        if c == '\r' and i + 1 < len(chars) and chars[i + 1] == '\n':
                            i += 1  # Skip the \n
                        client_sock.sendall(b"\n")
                        line = buffer.strip()
                        buffer = ""
                        if line:
                            history.append(line)
                            if len(history) > 100:  # Limit history size
                                history = history[-100:]
                        response = self.process_command(line)
                        if response is not None:
                            client_sock.sendall(response.encode())
                            if not response.endswith('\n'):
                                client_sock.sendall(b"\n")
                        # Send prompt only once after processing the command and response
                        client_sock.sendall(b"> ")
                        i += 1
                        continue
                    else:
                        buffer += c
                        client_sock.sendall(c.encode())
                        i += 1
        except Exception as e:
            client_sock.sendall(f"Error: {e}\n".encode())
        finally:
            client_sock.close()

    def process_command(self, line: str) -> str:
        """
        Parse and execute a command line from the user.

        Args:
            line: The command string entered by the user.

        Returns:
            Response string to send back to the client.
        """
        if not line:
            return ""
        tokens = line.split()
        cmd = tokens[0].lower()  # Command is the first word, case-insensitive
        args = tokens[1:]  # Arguments are all remaining words

        try:
            # Command dispatch table
            if cmd in ("quit", "exit"):
                return "Goodbye!"
            elif cmd == "help":
                return HELP_TEXT
            elif cmd == "set" and len(args) >= 2:
                param = args[0]
                value = " ".join(args[1:])
                return self._set_param(param, value)
            elif cmd == "get" and len(args) == 1:
                return self._get_param(args[0])
            elif cmd == "reg" and len(args) == 1:
                return self._simple_command("reg", args[0])
            elif cmd == "heater" and len(args) == 1:
                return self._simple_command("heater", args[0])
            elif cmd == "cooler" and len(args) == 1:
                return self._simple_command("cooler", args[0])
            elif cmd == "stirrer":
                if len(args) == 1 and args[0] == "off":
                    return self._simple_command("stirrer", "off")
                elif len(args) == 1:
                    return self._simple_command("stirrer", args[0])
                else:
                    return "Usage: stirrer <off|duty>"
            elif cmd == "ramp" and len(args) == 1:
                return self._simple_command("ramp", args[0])
            elif cmd == "period" and len(args) == 1:
                return self._simple_command("period", args[0])
            elif cmd == "freeze" and len(args) == 1:
                return self._simple_command("freeze", args[0])
            elif cmd == "i_err" and len(args) == 1:
                return self._simple_command("i_err", args[0])
            elif cmd == "seti" and len(args) == 1:
                return self._simple_command("setI", args[0])
            elif cmd == "rampup2" and len(args) == 2:
                return self._rampup2(args[0], args[1])
            elif cmd == "reset":
                return self._simple_command("reset", "true")
            elif cmd == "status":
                return self._status()
            else:
                return "Unknown command. Type 'help' for available commands."
        except Exception as e:
            return f"Error: {e}\n{traceback.format_exc()}"

    def _set_param(self, param: str, value: str) -> str:
        """
        Set a parameter in the comm_layer.

        Args:
            param: Parameter name.
            value: Value to set.

        Returns:
            Status message.
        """
        try:
            cmd = {param: value}
            self.comm_layer.command(cmd)
            return f"Set {param} to {value}"
        except Exception as e:
            return f"Failed to set {param}: {e}"

    def _get_param(self, param: str) -> str:
        """
        Get a parameter value from the comm_layer status.

        Args:
            param: Parameter name.

        Returns:
            Value or error message.
        """
        try:
            status = self.comm_layer.get_status_dict()
            if param in status:
                return f"{param}: {status[param]}"
            else:
                return f"Unknown parameter: {param}"
        except Exception as e:
            return f"Failed to get {param}: {e}"

    def _simple_command(self, param: str, value: str) -> str:
        """
        Send a simple command (single key-value) to the comm_layer.

        Args:
            param: Command key.
            value: Command value.

        Returns:
            Status message.
        """
        try:
            cmd = {param: value}
            self.comm_layer.command(cmd)
            return f"Command {param} {value} sent."
        except Exception as e:
            return f"Failed to send command {param}: {e}"

    def _rampup2(self, temp: str, minutes: str) -> str:
        """
        Special command to ramp up to a temperature in a given time.

        Args:
            temp: Target temperature.
            minutes: Time in minutes.

        Returns:
            Status message.
        """
        try:
            cmd = {"rampup2": {"temp": float(temp), "minutes": float(minutes)}}
            self.comm_layer.command(cmd)
            return f"Ramping up to {temp}°C in {minutes} minutes."
        except Exception as e:
            return f"Failed to ramp up: {e}"

    def _status(self) -> str:
        """
        Get a full status report from the comm_layer.

        Returns:
            Multiline string with all status key-value pairs.
        """
        try:
            status = self.comm_layer.get_status_dict()
            lines = [f"{k}: {v}" for k, v in status.items()]
            return "\n".join(lines)
        except Exception as e:
            return f"Failed to get status: {e}"

# Example usage:
# from comm_layer import Comm_layer
# start = ... # your start or start_simulation instance
# comm_layer = Comm_layer(start)
# server = CommLayerTerminalServer(comm_layer)
# threading.Thread(target=server.start, daemon=True).start()  # Run in background
