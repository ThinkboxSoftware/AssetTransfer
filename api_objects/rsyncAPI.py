'''
Project: Thinkbox Asset Transfer: Transfer framework for asset syncing.

Author: Allisa Schmidt

See readme for detailed usage information.

WARNING: BETA SOFTWARE. Do not use in production without testing.

Copyright 2014 - Thinkbox Software

'''
import os
import platform
import subprocess

from copy import deepcopy

from AbstractAPI import AbstractAPI

class RsyncAPI(AbstractAPI):

    def __init__(self, ip, port, user, pw, forced_overwrite, server_cwd):
        self.forced_overwrite = forced_overwrite
        rsync_dir = 'api_objects/rsync'
        self.base_args = [rsync_dir + '/rsync', '-zcrv', '-t']
        if not self.forced_overwrite:
            self.base_args.append('--update')

        self.base_args.extend(['--delete', '--stats', '--rsh=\'' + rsync_dir + '/ssh',
            '-i', rsync_dir + '/rsync', '-o', 'StrictHostKeyChecking=no\''])
        self.user = user
        self.ip = ip
        self.server_cwd = server_cwd
        self.identity = rsync_dir + '/rsync'

    def download(self, fname, target_dir):
        args = deepcopy(self.base_args)
        remote = self.user + '@' + self.ip + ':' + self.server_cwd + '/' + fname

        args.append(remote)
        args.append(self._convert_to_rsync_path(target_dir))

        p = subprocess.call(args)
        if p > 0:
            self._update_failure(fname)

    def upload(self, fname, local_name):
        if os.path.isfile(local_name):
            # Create remote server directory if it doesn't exist
            remote = self.user + '@' + self.ip
            ssh_args = ['ssh', '-i', self.identity, remote, 'mkdir', '-p', self.server_cwd]
            p = subprocess.call(ssh_args)

            # Create cygwin path if we're running this on a windows machine
            path = local_name
            if self._is_windows():
                path = self._convert_to_rsync_path(local_name)

            args = deepcopy(self.base_args)
            remote = self.user + '@' + self.ip + ':' + self.server_cwd
            args.append(path)
            args.append(remote)

            p = subprocess.call(args)
            if p > 0:
                self._update_failure(fname)
        else:
            self._update_failure(fname)
            print 'Failed to find local file {0}. Skipping.'.format(local_name)

    def _is_windows(self):
        fn = platform.system().lower().startswith
        return fn('windows') or fn('cygwin')

    def _convert_to_rsync_path(self, local_name):
        rsync_path = '/cygdrive/c'
        folders = local_name.split('\\')[1:]
        for folder in folders:
            rsync_path = rsync_path + '/' + folder

        return rsync_path
