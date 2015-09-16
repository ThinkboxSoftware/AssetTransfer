import os


class AbstractAPI(object):
    error_str = 'This class should never be used directly.'
    success_list = []
    failure_list = []

    def have_duplicate(self, fname, local_name):
        raise NotImplementedError(self.error_str)

    def download(self, req_files, target_dir):
        raise NotImplementedError(self.error_str)

    def upload(self, req_files):
        raise NotImplementedError(self.error_str)

    def print_results(self):
        print '\nSuccessfully transfered:'
        for f in self.success_list:
            print '\t' + f

        if len(self.failure_list) > 0:
            print '\nFailed to transfer:'
            for f in self.failure_list:
                print '\t' + f

    def _update_failure(self, fname):
        if fname in self.success_list:
            self.success_list.remove(fname)
            self.failure_list.append(fname)

    def download_files(self, req_files, target_dir):
        total = len(req_files)

        for index, fname in enumerate(req_files):
            self.success_list.append(fname)

            print "Transfering: {0}/{1}".format(index + 1, total)
            self.download(fname, target_dir)

    def upload_files(self, req_files, local_dir):
        total = len(req_files)

        for index, fname in enumerate(req_files):
            self.success_list.append(fname)
            local_name = os.path.join(local_dir, fname)

            print "Transfering: {0}/{1}".format(index + 1, total)
            self.upload(fname, local_name)
