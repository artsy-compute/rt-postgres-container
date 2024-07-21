#!/usr/bin/env python3

import argparse
import docker
import yaml
import sys
import signal

container = None


def load_config(file_path):
    """ Load configuration from a YAML file. """
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def print_example_usage():
    """ Print example usage information. """
    example_usage = """
    Example Usage:

    1. Start the PostgreSQL Docker container:
       python manage_postgres.py up config.yaml --port 5433 --container-name my_custom_postgres

    2. Stop and remove the PostgreSQL Docker container:
       python manage_postgres.py down config.yaml --container-name my_custom_postgres
    """
    print(example_usage)


def parse_args():
    """ Parse command line arguments. """
    parser = argparse.ArgumentParser(description='Manage PostgreSQL Docker containers for Odoo.')

    # Required config file
    parser.add_argument('config_file', type=str, help='Path to the YAML configuration file.')

    # Positional argument for command
    parser.add_argument('command', choices=['up', 'down', 'help'], help='Command to perform.')

    # Docker arguments
    parser.add_argument('--dbname', type=str, default='odoodb', help='Database name.')
    parser.add_argument('--user', type=str, default='odoo', help='Database user name.')
    parser.add_argument('--password', type=str, help='Database password. Must be set in config file only.')
    parser.add_argument('--port', type=int, default=5432, help='PostgreSQL port.')
    parser.add_argument('--network-mode', type=str, default='bridge', help='Network mode (host or bridge).')
    parser.add_argument('--network-name', type=str, help='Network name (if not in host mode).')
    parser.add_argument('--container-name', type=str, help='Container name.')
    parser.add_argument('--postgres-version', type=str, default='12', help='PostgreSQL version.')
    parser.add_argument('--volume-path', type=str,
                        help='Volume Path(e.g., /data:/var/lib/postgresql/data). Just need the host path')
    parser.add_argument('-d', '--detach', action='store_true', default=False, help="Run containers in detached mode")
    parser.add_argument('--debug', action='store_true', default=False, help="Print Debug Message")

    args = parser.parse_args()

    # Check for command-line password argument
    if args.password:
        print("Error: Password must be set in the configuration file and cannot be provided via command line.")
        sys.exit(1)

    # Display example usage if no command is given
    if args.command not in ['up', 'down']:
        print_example_usage()
        sys.exit()

    # Load config from file
    file_config = load_config(args.config_file)
    for key, value in file_config.items():
        key = key.replace('-', '_')
        if hasattr(args, key):
            setattr(args, key, value)

    return args


def handle_signal(sig, frame):
    global container
    if container and not container.attrs['State']['Paused']:
        print('')
        print(f"Stopping the container {container.attrs['Name']} due to signal interruption...")
        container.stop()
        container.remove()
        sys.exit(0)


def ensure_network_exists(client, network_name):
    networks = client.networks.list(names=[network_name])
    if not networks:
        print(f"Network '{network_name}' not found. Creating it...")
        client.networks.create(network_name, driver="bridge")
    else:
        print(f"Network '{network_name}' is in place.")


def manage_container(command, args):
    global container
    """ Manage PostgreSQL Docker container based on the command. """
    client = docker.from_env()

    if command == 'up':
        ports_binding = {'5432/tcp': args.port} if args.network_mode == 'bridge' else {}

        if args.network_mode == 'bridge' and args.network_name:
            ensure_network_exists(client, args.network_name)

        try:
            container = client.containers.run(
                f'postgres:{args.postgres_version}',
                name=args.container_name,
                environment={
                    'POSTGRES_DB': args.dbname,
                    'POSTGRES_USER': args.user,
                    'POSTGRES_PASSWORD': args.password,
                },
                ports=ports_binding,
                volumes={args.volume_path: {'bind': '/var/lib/postgresql/data', 'mode': 'rw'}},
                network_mode=args.network_mode if args.network_mode == 'host' else args.network_name,
                detach=True,
            )

            print(f'Container {args.container_name} is started')
            if not args.detach:
                print("Container started. Streaming logs:")
                signal.signal(signal.SIGINT, handle_signal)
                for line in container.logs(stream=True):
                    print(line.decode('utf-8').strip())
        except Exception as e:
            print(f"Failed to start container {args.container_name}: {e}")
    elif command == 'down':
        try:
            container = client.containers.get(args.container_name)
            container.stop()
            container.remove()
            print(f'Container {args.container_name} is stopped')
        except docker.errors.NotFound:
            print(f'{args.container_name} not found.')


def main():
    args = parse_args()
    if args.debug:
        print(args)
    manage_container(args.command, args)


if __name__ == '__main__':
    main()
