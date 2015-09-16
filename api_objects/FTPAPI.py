'''
Project: Thinkbox Asset Transfer: Transfer framework for asset syncing.

Author: Allisa Schmidt

See readme for detailed usage information.

WARNING: BETA SOFTWARE. Do not use in production without testing.

Copyright 2014 - Thinkbox Software

'''
import os

from ftplib import FTP
from AbstractAPI import AbstractAPI

class FtpAPI(AbstractAPI):

    def __init__(self, ip, port, user, pw, forced_overwrite, server_cwd):
        self.ftp = FTP()
        self.forced_overwrite = forced_overwrite
        self.ftp.connect(ip, port)
        self.ftp.login(user, pw)

        print 'Forced Overwrite Mode: {0}'.format(forced_overwrite)
        print self.ftp.getwelcome()

        # Switch server request type to passive
        print self.ftp.sendcmd('PASV')

        if server_cwd != '':
            if server_cwd not in self.ftp.nlst():
                print self.ftp.sendcmd('MKD %s' % server_cwd)
            self.ftp.sendcmd('CWD %s' % server_cwd)

        # Switch data transfer type to binary
        print self.ftp.sendcmd('TYPE I')

    def have_duplicate(self, fname, local_name):
        duplicate = False
        if os.path.isfile(local_name):
            size = float(self.ftp.size(fname))
            local_size = float(os.path.getsize(local_name))

            remote_lm = float(self.ftp.sendcmd('MDTM %s' % fname).split(' ')[1])
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

        def callback(data):
            with open(local_name, 'ab') as f:
                f.write(data)

        try:
            self.ftp.retrbinary('RETR %s' % fname, callback)
            print 'Copied remote {0} to {1}.\n'.format(fname, local_name)
        except Exception as e:
            self._update_failure(fname)
            print 'ERROR - server responded with response "{0}". ' \
                  'Could not retrieve file {1}'.format(e, fname)

    def upload(self, fname, local_name):
        if os.path.isfile(local_name):
            try:
                print 'Copying local file {0} to FTP server.'.format(fname)
                self.ftp.storbinary('STOR %s' %fname, open(local_name, 'rb'))
            except Exception as e:
                self._update_failure(fname)
                print 'ERROR - server responded with response "{0}". ' \
                      'Could not put file {1}'.format(e, fname)
        else:
            self._update_failure(fname)
            print 'Failed to find local file {0}. Skipping.'.format(fname)
