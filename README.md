# pyvpnmap
NordVPN google map interface for connection management.

# Configuration Options:
* auto_connect: 0/1  -- connect to last_connected node on startup
* config_path: str -- Absolute path to location containing *.ovpn files
* last_connected: str -- Name of openvpn config used last
* password: str -- Password for accout
* sock_path: str -- Location to save openvpn management sock to
* tcp: 0/1 -- Use tcp port 443 when connecting or standard udp
* user: str -- E-mail login for NordVPN account
