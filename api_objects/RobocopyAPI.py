'''
Project: Thinkbox Asset Transfer: Transfer framework for asset syncing.

Author: Allisa Schmidt

See readme for detailed usage information.

WARNING: BETA SOFTWARE. Do not use in production without testing.

Copyright 2014 - Thinkbox Software

Refer to http://ss64.com/nt/robocopy-exit.html for robocopy return codes.

'''
import os
import platform
import re
import subprocess

from copy import deepcopy

from AbstractAPI import AbstractAPI

fail_re = r'Files :\s*0'

class RobocopyAPI(AbstractAPI):

    def __init__(self, ip, port, user, pw, forced_overwrite, server_cwd):
        self.remote_dir = '\\\\{0}\\{1}'.format(ip, server_cwd)
        if ip == '127.0.0.1':
            self.remote_dir = server_cwd
        self.forced_overwrite = forced_overwrite

        # Robocopy defaults to a MILLION retries if the command fails.
        # Obviously that takes a while. This sets it to 2 retries with a
        # timeout of 3 seconds.
        self.end_args = ['/r:2', '/w:3']

    def download(self, fname, target_dir):
        args = ['robocopy', self.remote_dir, target_dir, fname]

        if not self.forced_overwrite:
            args.append('/xo')
        else:
            args.append('/is')
        args.extend(self.end_args)

        p = subprocess.Popen(args, stdout=subprocess.PIPE)
        p.wait()
        output = p.communicate()[0]
        ret = p.returncode

        if ret == 0:
            if re.findall(fail_re, output):
                print 'Failed to download file {0} because it does not exist remotely'.format(fname)
                self._update_failure(fname)
            else:
                print 'Skipping copy of {0} because either a duplicate exists locally.'.format(fname)
        if ret != 0 and ret != 1:
            print 'Failed to download file {0}.'.format(fname)
            self._update_failure(fname)

    def upload(self, fname, local_name):
        if os.path.isfile(local_name):
            local_dir = os.path.dirname(local_name)
            args = ['robocopy', local_dir, self.remote_dir, fname]
            args.extend(self.end_args)

            p = subprocess.Popen(args, stdout=subprocess.PIPE)
            p.wait()
            output = p.communicate()[0]
            ret = p.returncode
            print output

            if ret == 0:
                print 'Skipping copy of {0} because a duplicate exists remotely.'.format(fname)
            if ret != 1 and ret != 0:
                print 'Failed to upload file {0}.'.format(fname)
                self._update_failure(fname)

        else:
            self._update_failure(fname)
            print 'Failed to find local file {0}. Skipping.'.format(local_name)
