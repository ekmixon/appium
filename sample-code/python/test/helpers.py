import os
import sys
from selenium.common.exceptions import InvalidSessionIdException
from datetime import datetime
from sauceclient import SauceClient


ANDROID_BASE_CAPS = {
    'app': os.path.abspath('../apps/ApiDemos-debug.apk'),
    'automationName': 'UIAutomator2',
    'platformName': 'Android',
    'platformVersion': os.getenv('ANDROID_PLATFORM_VERSION') or '8.0',
    'deviceName': os.getenv('ANDROID_DEVICE_VERSION') or 'Android Emulator',
}

IOS_BASE_CAPS = {
    'app': os.path.abspath('../apps/TestApp.app.zip'),
    'automationName': 'xcuitest',
    'platformName': 'iOS',
    'platformVersion': os.getenv('IOS_PLATFORM_VERSION') or '12.2',
    'deviceName': os.getenv('IOS_DEVICE_NAME') or 'iPhone 8 Simulator',
    # 'showIOSLog': False,
}

sauce = None
if os.getenv('SAUCE_LABS') and os.getenv('SAUCE_USERNAME') and os.getenv('SAUCE_ACCESS_KEY'):
    build_id = os.getenv('TRAVIS_BUILD_ID') or datetime.now().strftime('%B %d, %Y %H:%M:%S')
    build_name = f'Python Sample Code {build_id}'

    ANDROID_BASE_CAPS['build'] = build_name
    ANDROID_BASE_CAPS['tags'] = ['e2e', 'appium', 'sample-code', 'android', 'python']
    ANDROID_BASE_CAPS['app'] = 'http://appium.github.io/appium/assets/ApiDemos-debug.apk'

    IOS_BASE_CAPS['build'] = build_name
    IOS_BASE_CAPS['tags'] = ['e2e', 'appium', 'sample-code', 'ios', 'python']
    IOS_BASE_CAPS['app'] = 'http://appium.github.io/appium/assets/TestApp9.4.app.zip'

    EXECUTOR = f"http://{os.getenv('SAUCE_USERNAME')}:{os.getenv('SAUCE_ACCESS_KEY')}@ondemand.saucelabs.com:80/wd/hub"


    sauce = SauceClient(os.getenv('SAUCE_USERNAME'), os.getenv('SAUCE_ACCESS_KEY'))
else:
    EXECUTOR = 'http://127.0.0.1:4723/wd/hub'


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def take_screenshot_and_logcat(driver, device_logger, calling_request):
    __save_log_type(driver, device_logger, calling_request, 'logcat')


def take_screenshot_and_syslog(driver, device_logger, calling_request):
    __save_log_type(driver, device_logger, calling_request, 'syslog')


def __save_log_type(driver, device_logger, calling_request, type):
    logcat_dir = device_logger.logcat_dir
    screenshot_dir = device_logger.screenshot_dir

    try:
        driver.save_screenshot(os.path.join(screenshot_dir, f'{calling_request}.png'))
        logcat_data = driver.get_log(type)
    except InvalidSessionIdException:
        logcat_data = ''

    with open(os.path.join(logcat_dir, f'{calling_request}_{type}.log'), 'w') as logcat_file:
        for data in logcat_data:
            data_string = '%s:  %s\n' % (data['timestamp'], data['message'].encode('utf-8'))
            logcat_file.write(data_string)

def report_to_sauce(session_id):
    if sauce is not None:
        print(f"Link to your job: https://saucelabs.com/jobs/{session_id}")
        passed = str(sys.exc_info() == (None, None, None))
        sauce.jobs.update_job(session_id, passed=passed)
