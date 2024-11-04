import argparse
from netmiko import ConnectHandler
from nmfilesparser import SSHTEL_CONNECTION, COM_CONNECTION, TFTP_CONNECTION, read_nmconn

def read_config(connection: str, output_file: str | None, show_config: bool | None):
    connection = read_nmconn(connection)

    if connection.METHOD != "TFTP":
        connection_data = connection.getNetmikoConnDict()

        net_connect = ConnectHandler(**connection_data)

        if (connection_data['device_type'].startswith('cisco_') or
            connection_data['device_type'].startswith('juniper_') or
            connection_data['device_type'].startswith('fortinet_')) and \
                connection_data['secret']:
            net_connect.enable()

        if connection_data['device_type'].startswith('cisco_'):
            command = 'show running-config'
        elif connection_data['device_type'].startswith('juniper_'):
            command = 'show configuration'
        elif connection_data['device_type'].startswith('hp_'):
            command = 'display current-configuration'
        elif connection_data['device_type'].startswith('fortinet_'):
            command = 'show'
        elif connection_data['device_type'].startswith('ubiquiti_'):
            command = 'show configuration'
        elif connection_data['device_type'].startswith('mikrotik_'):
            command = '/export'
        elif connection_data['device_type'].startswith('paloalto_'):
            command = 'show config running'
        else:
            raise ValueError("Unsupported device type")

        output = net_connect.send_command(command)
        if show_config:
            print(output)

        if output is not None:
            with open(output_file, 'w+') as f:
                f.write(output)

        net_connect.disconnect()


def main():
    parser = argparse.ArgumentParser(description='NetManage')
    subparsers = parser.add_subparsers(dest='command')

    # Read conf
    parser_read_config = subparsers.add_parser('read-config', help='Read config file')
    parser_read_config.add_argument('-c', '--connection', type=str, required=True, help='Path to .nmconn file')
    parser_read_config.add_argument('-o', '--output', type=str, required=False, help='Path to output .txt file')
    parser_read_config.add_argument('-s', '--show-config', type=bool, required=False, help='Show output in console')

    args = parser.parse_args()

    if args.command == "read-config":
        print(
            args.connection, args.output, args.show_config
        )

        read_config(args.connection, args.output, args.show_config)

    else:
        parser.print_help()

if __name__ == '__main__':
    main()
