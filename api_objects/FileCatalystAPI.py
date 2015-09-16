'''
Project: Thinkbox Asset Transfer: Transfer framework for asset syncing.

Author: Allisa Schmidt

See readme for detailed usage information.

WARNING: BETA SOFTWARE. Do not use in production without testing.

Copyright 2014 - Thinkbox Software

'''
import os
import subprocess

from AbstractAPI import AbstractAPI

class FilecatalystAPI(AbstractAPI):

    def __init__(self, ip, port, user, pw, forced_overwrite, server_cwd):
        self.fc_jar = 'api_objects\\fc_cli\FileCatalystCL.jar'
        self.forced_overwrite = forced_overwrite
        self.base_args = ['java', '-jar', self.fc_jar,
                '-host', ip, '-user', user, '-passwd', pw,
                '-connecttimeoutsec', '3', '-maxretries', '1',
                '-waitretry', '2',
                '-bandwidth', '100000']

        if server_cwd != '':
            self.base_args.extend(['-remotedir', server_cwd])

    def download(self, fname, target_dir):
        base_name = os.path.basename(fname)
        local_name = os.path.join(target_dir, base_name)

        dl_args = ['-download', '-localdir', target_dir, '-file', base_name]
        args = self.base_args
        args.extend(dl_args)

        if not self.forced_overwrite:
            args.append('-incdelta')

        p = subprocess.call(args)
        if p > 0:
            self._update_failure(fname)

    def upload(self, fname, local_name):
        if os.path.isfile(local_name):
            dl_args = ['-file', local_name]
            args = self.base_args
            args.extend(dl_args)

            p = subprocess.call(args)
            if p > 0:
                self._update_failure(fname)
        else:
            self._update_failure(fname)
            print 'Failed to find local file {0}. Skipping.'.format(local_name)
