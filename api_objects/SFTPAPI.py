'''
Project: Thinkbox Asset Transfer: Transfer framework for asset syncing.

Author: Allisa Schmidt

See readme for detailed usage information.

WARNING: BETA SOFTWARE. Do not use in production without testing.

Copyright 2014 - Thinkbox Software

'''
import os
import sys

from AbstractAPI import AbstractAPI

# TODO: if system is windows
win_libs = os.path.join(os.getcwd(), 'api_objects', 'sftp_libs', 'windows')
sys.path.insert(0, win_libs)

# TODO: else mac or linux
import sftp_libs.windows.paramiko as paramiko
import sftp_libs.windows.paramiko.util as util


class SftpAPI(AbstractAPI):

    def __init__(self, ip, port, user, pw, forced_overwrite, server_cwd):
        util.log_to_file('sftp.log')
        transport = paramiko.Transport((ip, int(port)))
        transport.connect(username=user, password=pw)
        self.ftp = paramiko.SFTPClient.from_transport(transport)

        self.forced_overwrite = forced_overwrite

        print 'Forced Overwrite Mode: {0}'.format(forced_overwrite)

        if server_cwd != '':
            if server_cwd not in self.ftp.listdir():
                print self.ftp.mkdir(server_cwd)
            self.ftp.chdir(server_cwd)

    def have_duplicate(self, fname, local_name):
        duplicate = False
        if os.path.isfile(local_name):
            size = float(self.ftp.stat(fname).st_size)
            local_size = float(os.path.getsize(local_name))

            remote_lm = float(self.ftp.stat(fname).st_mtime)
            local_lm = float(os.stat(local_name).st_mtime)

            if size == local_size and local_lm > remote_lm:
                duplicate = True

        return duplicate

    def download(self, fname, target_dir):
        base_name = os.path.basename(fname)
        local_name = os.path.join(target_dir, base_name)

        if self.have_duplicate(fname, local_name) and not self.forced_overwrite:
            print 'Skipping copy of {0} because a duplicate exists locally.'.format(fname)
            return
        elif os.path.exists(local_name):
            print 'Removing outdated {0} before copy.'.format(local_name)
            os.remove(local_name)

        try:
            self.ftp.get(fname, local_name)
            print 'Copied remote {0} to {1}.\n'.format(fname, local_name)
        except Exception as e:
            self._update_failure(fname)
            print 'ERROR - server responded with response "{0}". ' \
                  'Could not retrieve file {1}'.format(e, fname)

    def upload(self, fname, local_name):
        if os.path.isfile(local_name):
            try:
                print 'Copying local file {0} to FTP server.'.format(fname)
                self.ftp.storbinary(local_name, fname)
            except Exception as e:
                self._update_failure(fname)
                print 'ERROR - server responded with response "{0}". ' \
                      'Could not put file {1}'.format(e, fname)
        else:
            self._update_failure(fname)
            print 'Failed to find local file {0}. Skipping.'.format(fname)
