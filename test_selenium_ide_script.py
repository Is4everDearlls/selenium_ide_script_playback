import os
import sys

import pytest


def test_selenium_ide_script(testcase):
    testcase.write()
    assert testcase.result


if __name__ == '__main__':
    host = sys.argv[1]
    pytest.main(['-s', '-v', '--host', host, '--alluredir', 'result', '--clean-alluredir'])
    os.system('allure generate --clean result --output result/html')
    sys.exit(0)
