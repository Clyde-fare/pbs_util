"""pbs.py test suite."""

import pbs
import unittest
import os.path
import os

from submit_command import run_command_here


def file_contents(filename):
    file = open(filename)
    contents = file.read()
    file.close()
    return contents

def dump_to_file(filename, contents):
    file = open(filename, 'w')
    file.write(contents)
    file.close()

class HelloWorldCase(unittest.TestCase):
    """Set up a hello world script for testing with."""

    def setUp(self):
        temp_output_filename = self.temp_output_filename = '~/temp.out'

        self.pbs_script_filename = os.path.realpath('.') + '/test.pbs'

        dump_to_file(self.pbs_script_filename,
                     pbs.generic_script("""
echo "Hello, World!" > %(temp_output_filename)s
sleep 1
""" % locals()))

    def tearDown(self):  
        if os.path.exists(self.temp_output_filename):
            os.remove(self.temp_output_filename)
        os.remove(self.pbs_script_filename)

class Check_qstat(HelloWorldCase):
    """Check that pbs.qstat works."""

    def test_qstat_real(self):
        """pbs.qstat should return a non false result when given something actually submitted."""
        print(self.pbs_script_filename)
        assert pbs.qstat(job_id=pbs.qsub(self.pbs_script_filename))

    def test_qstat_not_present(self):
        """pbs.qstat should return None when given a pbs id that doesn't actuallye exist."""
        self.assertRaises(pbs.PBSUtilError, pbs.qstat, '12345.notreal')

class Check_qsub(HelloWorldCase):
    """Check that pbs.qsub works."""

    def test_qsub(self):
        """pbs.qsub runs without error"""
        pbs.qsub(self.pbs_script_filename)

    def test_qsub_submits(self):
        """check that qsub successfully submits a script."""
        pbs_id = pbs.qsub(self.pbs_script_filename)
        assert pbs.qstat(job_id=pbs_id), "failed to find stats for %s which was just submitted." % pbs_id

#this test isn't working yet but I think it's actually ok
class Check_wait(HelloWorldCase):
    """Check that pbs.qsub is capable of blocking while waiting for a pbs job to finish."""
    def rexists(self, sftp, path):
        """os.path.exists for paramiko's SCP object
        """
        try:
            sftp.stat(path)
        except IOError, e:
            if e[0] == 2:
                return False
            raise
        else:
            return True

    def test_wait(self):
        """pbs.qwait should wait for a pbs job to finish running."""
        ssh, sftp = pbs.connect_server(ssh=True,sftp=True)

        if self.rexists(sftp,self.temp_output_filename):
            ssh.exec_command('rm ' + self.temp_output_filename)

        pbs_id = pbs.qsub(self.pbs_script_filename)
        pbs.qwait(pbs_id)
        ssh.exec_command('ls > /dev/null') # This triggers the panfs file system to make the file appear.
        assert self.rexists(sftp, self.temp_output_filename), "pbs.qwait returned, but the expected output does not yet exist."
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    unittest.main()
