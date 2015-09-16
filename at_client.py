'''
Project: Thinkbox Asset Transfer: Transfer framework for asset syncing.

Author: Allisa Schmidt

See README for detailed usage information.

WARNING: BETA SOFTWARE. Do not use in production without testing.

Copyright 2014 - Thinkbox Software

'''
import getopt
import os
import subprocess
import sys

from ConfigParser import ConfigParser

import api_objects

SERVICES = ['ftp', 'filecatalyst', 'robocopy', 'rsync', 'sftp']

class ClientConfigParser(ConfigParser):
    def __init__(self, conf_file):
        ConfigParser.__init__(self)
        self.server = {}
        self.user = {}

        self.read(conf_file)
        self.server = self._map_config('Server')
        self.user = self._map_config('User')
        self.client = self._map_config('Client')

    def _map_config(self, section):
        data = {}
        opts = self.options(section)

        for opt in opts:
            try:
                data[opt] = self.get(section, opt)
                if opt == 'flags':
                    data[opt] = data[opt].split(' ')
                    if len(data[opt]) > 0 and data[opt][0] == '':
                        data[opt] = []
            except Exception as e:
                print e
                data[opt] = None

        return data

def safe_mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def setup_dirs(ccp, cwd):
    log_path = os.path.join(cwd, 'log')
    log_file = os.path.join(log_path, ccp.client['log'])

    if ccp.client['service'].lower() == 'rsync':
        target_dir = ccp.client['target_dir']
    else:
        target_dir = os.path.join(cwd, ccp.client['target_dir'])

    safe_mkdir(log_path)
    safe_mkdir(target_dir)

    return log_file, target_dir

def parse(request_file):
    files = []

    with open(request_file) as f:
        for line in f:
            stripped_line = line.strip()
            files.append(stripped_line)

    return files

def service_error():
    print 'Please run the script with a valid service name.\n' \
            'SUPPORTED SERVICES: '
    for service in SERVICES:
        print '\t- ' + service

def usage():
    print 'Usage: python at_client.py --file=[path] --config=[path] <optional parameters> <flags>\n'
    print 'REQUIRED PARAMETERS:'
    print '\t--file=[path]\t\t-> path to the file which contains the list of files to either download, or to upload'
    print '\t--config=[path]\t\t-> path to the config file to use for this transfer\n'
    print 'OPTIONAL PARAMETERS:'
    print '\tNote: These should be specified in the INI config file but can instead be specified via command line.'
    print '\t--ip=[ip or hostname]\t-> server to connect to'
    print '\t--port=[port number]\t-> port to connect via'
    print '\t--service=[service]\t-> desired transfer protocol - available protocols are: ftp, filecatalyst, robocopy, rsync, sftp\n'
    print 'FLAGS:'
    print '\tNote: These should be specified in the INI config file but can instead be specified via command line'
    print '\t--upload\t\t-> upload files - service by default will download them'
    print '\t--overwrite\t\t-> force download of files even if local files exist and are identical'

def main(argv):
    ip = None
    port = None

    conf_file = None
    request_file = None

    api = None

    service = None
    do_upload = False
    overwrite = False

    try:
        opts, args = getopt.getopt(argv, 'hf:i:p:c:s:uko', ['help', 'file=', 'ip=',
            'port=', 'config=', 'service=', 'upload', 'overwrite'])
    except Exception as e:
        print e
        usage()
        sys.exit(2)

    # Handle cmd line args
    for opt, arg in opts:
        if opt == '--file':
            request_file = arg
        elif opt == '--ip':
            ip = arg
        elif opt == '--port':
            port = arg
        elif opt == '--config':
            conf_file = arg
        elif opt == '--service':
            service = arg
        elif opt == '--upload':
            do_upload = True
        elif opt == '--overwrite':
            overwrite = True
        elif opt == '--help':
            usage()
            sys.exit(2)

    if not request_file:
        usage()
        sys.exit(2)

    if not conf_file:
        usage()
        sys.exit(2)

    ccp = ClientConfigParser(conf_file)

    # Handle config file flags
    for flag in ccp.client['flags']:
        if flag == '--upload':
            do_upload = True
        elif flag == '--overwrite':
            overwrite = True

    log_file, target_dir = setup_dirs(ccp, os.getcwd())

    if not ip:
        ip = ccp.server['ip']
    if not port:
        try:
            port = ccp.server['port']
        except:
            pass
    if not service:
        service = ccp.client['service']

    req_files = parse(request_file)

    service = service.lower()
    if service not in SERVICES:
        service_error()
        sys.exit()

    # Dynamically gets the correct API object class name
    api_cls = getattr(api_objects, service.capitalize() + 'API')
    api = api_cls(ip, port, ccp.user['name'], ccp.user['pass'], overwrite,
            ccp.server['server_dir'])

    # Robocopy commands require additional setup and tear-down. Since robocopy
    # does not natively support copying with authentication-requiring network
    # drives, we have to set up an IPC connection.
    if service == 'robocopy':
        if not sys.platform.startswith('win'):
            print 'ERROR: robocopy command only supported on Windows.'
            sys.exit()
        server_str = '\\\\{0}\IPC$'.format(ip)
        user_str = '/u:server\\{0}'.format(ccp.user['name'])
        subprocess.call(['net', 'use', server_str, user_str, ccp.user['pass']])

    try:
        if do_upload:
            api.upload_files(req_files, ccp.client['source_dir'])
        else:
            api.download_files(req_files, target_dir)
        api.print_results()

        # Remove IPC connection
        if service == 'robocopy':
            subprocess.call(['net', 'use', server_str, '/d'])

    except Exception as e:
        print e
        sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[1:])
