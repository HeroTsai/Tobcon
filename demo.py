from array import array
from bluepy.btle import Scanner,DefaultDelegate,Peripheral,UUID
import os, sys, time
import struct
import json
import click

# Dependencies:
# pip install click
# pip install bluepy

# port: 20001

class AutoPilot(DefaultDelegate):
        def __init__(self, verbose='', config=''):
                DefaultDelegate.__init__(self)

                self.config_json = None
                self.scanner = None
                self.peripheral = None
                self.device = None

                self.service = None
                self.service_uuid = None
                self.characteristic = None
                self.characteristic_uuid = None

                self.verbose = verbose
                self.bootstrap(click.format_filename(config))

        def bootstrap(self, config_file):
                click.echo('Config File: %s' % config_file)
                file_buffer = click.open_file(config_file, 'r')
                self.config_json = json.load(file_buffer)
                self.header = self.config_json['AutoPilot']['Header']
                self.service_uuid = UUID(self.config_json['AutoPilot']['ServiceUUID'])
                self.characteristic_uuid = UUID(self.config_json['AutoPilot']['CharacteristicUUID'])

                click.echo(self.service_uuid)

                self.echo_config()

                click.echo('Start scanning?')
                click.pause()

        def echo_config(self):
                click.echo('Current Config:')
                click.echo(json.dumps(self.config_json, indent=4, sort_keys=True))

        def scan(self): 
                click.clear() 
                click.echo('begin scanning...')

                scan_period = self.config_json['ScanPeriod']

                click.echo('please wait for %d second...' % scan_period)

                # set self as callbacks
                self.scanner = Scanner().withDelegate(self)
                # A list of ScanEntry
                devices = self.scanner.scan(scan_period)

                for dev in devices:
                        click.echo("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
                        for (ad_type, desc, value) in dev.getScanData():
                                click.echo("    %s (%s) = %s" % (desc, ad_type, value))

                        if click.confirm('Connect to this device?'):
                                self.connect(dev)
                                return

                if click.confirm('Rescan?'):
                        self.scan()
                        return

        def connect(self, device):
                os.popen("sudo hcitool lecc --random %s" % device.addr)

                self.device = device
                self.peripheral = Peripheral(self.device.addr, self.device.addrType)

                self.send_command()

        def send_command(self):
                if self.peripheral == None:
                        click.echo('No available peripheral, exiting...')
                        self.end()

                click.clear()
                vertical_mode = click.prompt('Vertical Mode(0,1,2,3)', default=0)
                vertical_cmd = click.prompt('Vertical Cmd(0 - 255)', default=0.0)
                laterial_mode = click.prompt('Laterial Mode(0,1,2,3)', default=0)
                laterial_cmd = click.prompt('Laterial Cmd(0 - 255)', default=0.0)
                longitudinal_mode = click.prompt('Longitudinal Mode(0,1,2)', default=0)
                longitudinal_cmd = click.prompt('Longitudinal Cmd(0 - 255)', default=0.0)

                packet = self.echo_packet((
                        vertical_cmd,
                        vertical_mode 
                ), ( 
                        laterial_cmd,
                        laterial_mode
                ), ( 
                        longitudinal_cmd,
                        longitudinal_mode
                ))

                click.echo('packet size: %d' % len(packet))
                click.echo('packet dump: ' + ":".join("{:02x}".format(ord(c)) for c in packet))

                if self.setup_service():
                        self.characteristic.write(packet)
                        click.echo('packet sent successfully')
                        if click.confirm('Continue?'):
                                self.send_command()

        def setup_service(self):
                # TODO: fix invalid uuid
                self.service = self.peripheral.getServiceByUUID(self.service_uuid)
                self.characteristic = self.service.getCharacteristics(self.characteristic_uuid)[0]

                # click.echo(self.service.uuid)
                # click.echo(self.characteristic.uuid)

                return True

        def echo_packet(self, vertical, laterial, longitudinal):
                header_bytes = struct.pack('B', self.header['Port'] * 16 + self.header['Link'] * 4 + self.header['Channel'])
                vertical_bytes = struct.pack('>f', vertical[0]) + struct.pack('B', vertical[1])
                laterial_bytes = struct.pack('>f', laterial[0]) + struct.pack('B', laterial[1])
                longitudinal_bytes = struct.pack('>f', longitudinal[0]) + struct.pack('B', longitudinal[1])

                return header_bytes + vertical_bytes + laterial_bytes + longitudinal_bytes

        def end(self):
                click.clear()
                sys.exis(0)
                
@click.command()
@click.option('--verbose', default=False)
@click.option('--config', default='demo.json', envvar='AP_DEMO_CONFIG')
@click.pass_context
def cli(ctx, verbose, config):
        click.clear()
        ctx.auto_pilot = AutoPilot(verbose, config)

        ctx.auto_pilot.scan()

if __name__ == '__main__':
        # ??
        cli({})
