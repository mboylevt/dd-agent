import mock
import unittest

from tests.common import get_check

class ZfsTestCase(unittest.TestCase):

    def setUp(self):
        self.config = """
    init_config:

    instances:
        - name: test
    """
        

    def test_get_zfs_stats(self):
        zfs_get_data = """used	9110244945920
available	4529883320320
compressratio	2.70x"""
        expected = {
            'used': '9110244945920',
            'available': '4529883320320',
            'compressratio': '2.70'
        }
        check, instances = get_check('zfs', self.config)
        check.subprocess.Popen = mock.Mock()
        check.subprocess.Popen.return_value = mock.Mock()
        check.subprocess.Popen.return_value.communicate.return_value = (zfs_get_data, None)
        zfs_name = 'tank'
        actual = check._get_zfs_stats(zfs_name)
        assert check.subprocess.Popen.call_count == 1
        assert check.subprocess.Popen.call_args == mock.call(
            'sudo zfs get -o property,value -p available,used,compressratio -H tank'.split(),
            stdout=check.subprocess.PIPE
        )
        for result in actual.keys():
            assert actual[result] == expected[result]

    def test_get_zpool_stats(self):
        zpool_get_data = """NAME  PROPERTY    VALUE  SOURCE
tank  capacity    64%    -
tank  size        14.5T  -
tank  dedupratio  1.00x  -
tank  free        5.08T  -
tank  allocated   9.42T  -"""

        expected = {
            'capacity': '64',
            'size': '15942918602752',
            'dedupratio': '1.00',
            'free': '5585519069102',
            'allocated': '10357399533649'

        }
        check, instances = get_check('zfs', self.config)
        check.subprocess.Popen = mock.Mock()
        check.subprocess.Popen.return_value = mock.Mock()
        check.subprocess.Popen.return_value.communicate.return_value = (zpool_get_data, None)
        zpool_name = 'tank'
        actual = check._get_zpool_stats(zpool_name)
        assert check.subprocess.Popen.call_count == 1
        assert check.subprocess.Popen.call_args == mock.call(
            'sudo zpool get capacity,size,dedupratio,free,allocated tank'.split(),
            stdout=check.subprocess.PIPE
        )
        for result in actual.keys():
            assert actual[result] == expected[result]

    def test_get_zpool_checks(self):
        zpool_get_data = """NAME  PROPERTY    VALUE  SOURCE
tank  health    ONLINE    -"""
        expected = {
            'health': 'ONLINE'
        }
        check, instances = get_check('zfs', self.config)
        check.subprocess.Popen = mock.Mock()
        check.subprocess.Popen.return_value = mock.Mock()
        check.subprocess.Popen.return_value.communicate.return_value = (zpool_get_data, None)
        zpool_name = 'tank'
        actual = check._get_zpool_checks(zpool_name)
        assert check.subprocess.Popen.call_count == 1
        assert check.subprocess.Popen.call_args == mock.call(
            'sudo zpool get health tank'.split(),
            stdout=check.subprocess.PIPE
        )
        for result in actual.keys():
            assert actual[result] == expected[result]

    def test_convert_human_to_bytes(self):
        check, instances = get_check('zfs', self.config)

        # Test bytes
        result = check._convert_human_to_bytes('300')
        assert result == 300

        # Test kilobytes
        result = check._convert_human_to_bytes('300K')
        assert result == 307200

        # Test megabytes
        result = check._convert_human_to_bytes('300M')
        assert result == 314572800

        # Test gigabytes
        result = check._convert_human_to_bytes('300G')
        assert result == 322122547200

        # Test terabytes
        result = check._convert_human_to_bytes('300T')
        assert result == 329853488332800

        # Test invalid input
        with self.assertRaises(ValueError):
            check._convert_human_to_bytes('Pfffffft')

        # Test non-implemented units
        with self.assertRaises(NotImplementedError):
            check._convert_human_to_bytes('300J')

