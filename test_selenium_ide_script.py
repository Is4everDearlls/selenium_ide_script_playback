import os
import sys

import pytest


def test_selenium_ide_script(result):
    result.write()
    assert result.result


if __name__ == '__main__':
    pytest.main(['-s', '-v', '--alluredir', 'result', '--clean-alluredir'])
    os.system('allure generate --clean result --output result/html')
    sys.exit(0)