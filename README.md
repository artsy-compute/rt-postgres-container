
# PostgreSQL Docker Manager for Odoo

This script helps manage PostgreSQL Docker containers specifically for use with Odoo. It supports starting, stopping, and managing containers with various configurations.

## Prerequisites

- Python 3.x
- Docker
- `docker` Python library
- `PyYAML` Python library


## Configuration

Create a YAML configuration file with the necessary parameters. Below is an example configuration (`config.yaml`):

```yaml
dbname: odoodb
user: odoo
password: odoo
port: 7777
network-mode: host
network-name: rt_example_network
container-name: rt_example_postgres
postgres-version: 15
volume-path: /rt/data
```

## Usage

### Start the PostgreSQL Docker Container

Quick and easy to start the PostgreSQL Docker container:

```bash
./rt-postgres-container.py config.example.yaml up
```

Start container along with parameter adjustment on top of configuration file:

```bash
./rt-postgres-container.py config.example.yaml up --port 5433 --container-name my_custom_postgres
```

### Stop and Remove the PostgreSQL Docker Container

To stop and remove the PostgreSQL Docker container:

```bash
./rt-postgres-container.py config.example.yaml
```

### Command Line Arguments

- `config_file`: Path to the YAML configuration file (required).
- `command`: Command to perform (`up`, `down`).
- `--dbname`: Database name (default: `odoodb`).
- `--user`: Database user name (default: `odoo`).
- `--password`: Database password (must be set in config file only).
- `--port`: PostgreSQL port (default: `5432`).
- `--network-mode`: Network mode (`host` or `bridge`, default: `bridge`).
- `--network-name`: Network name (if not in host mode).
- `--container-name`: Container name.
- `--postgres-version`: PostgreSQL version (default: `12`).
- `--volume-path`: Volume path (e.g., `/data:/var/lib/postgresql/data`, just need the host path).
- `-d`, `--detach`: Run containers in detached mode.
- `--debug`: Print debug messages.

## License

This project is licensed under the MIT License.

