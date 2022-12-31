import os

from params import *
from utils import *


class NotOneDevice(Exception):
    pass


class AppException(Exception):
    pass


def get_desired_caps(path_apk: str):
    """
    :param path_apk: str of path of the apk.
    :return: dict, desired_caps.
    """
    desired_caps = {
        "platformName": "Android",
        "platformVersion": None,
        "deviceName": None,
        "appPackage": None,
        "appActivity": None,
    }
    # Android platform version
    line_read = os.popen("adb shell getprop ro.build.version.release").readline()
    if line_read == "":
        raise NotOneDevice()
    desired_caps["platformVersion"] = line_read.split()[0]

    # device name
    lines_read = os.popen("adb devices").readlines()
    if len(lines_read) <= 1 or lines_read[1] == "":
        raise NotOneDevice()
    desired_caps["deviceName"] = lines_read[1].split()[0]

    # app info
    line_read = os.popen("aapt dump badging {} | findstr package:".format(path_apk)).readline()
    desired_caps["appPackage"] = line_read.split('\'')[1]
    line_read = os.popen("aapt dump badging {} | findstr launchable-activity:".format(path_apk)).readline()
    desired_caps["appActivity"] = line_read.split('\'')[1]

    return desired_caps


class App(object):
    def __init__(self, path_apk: str):
        self.path_apk = path_apk
        self.desired_caps = get_desired_caps(path_apk)
        # str_versionName = os.popen(
        #     "adb shell pm dump " + desired_caps["appPackage"] + " | findstr versionName").read()
        # self.versionName = str_versionName.split('=')[1]
        line_read = os.popen("aapt dump badging {} | findstr package:".format(path_apk)).readline()
        self.versionCode = line_read.split('\'')[3]
        self.versionName = line_read.split('\'')[5]

        self.is_installed = False
        # self.screenshots = []

        # print app info
        print("-" * 40)
        print("{:<20}{:<20}".format("path_apk: ", self.path_apk))
        print("{:<20}{:<20}".format("appPackage: ", self.desired_caps["appPackage"]))
        print("{:<20}{:<20}".format("appActivity: ", self.desired_caps["appActivity"]))
        print("{:<20}{:<20}".format("versionCode: ", self.versionCode))
        print("{:<20}{:<20}".format("versionName: ", self.versionName))

    def install(self):
        self.uninstall()
        self.is_installed = True
        command = "adb install -r " + self.path_apk
        cmd(command)

    def uninstall(self):
        self.is_installed = False
        command = "adb uninstall " + self.desired_caps["appPackage"]
        cmd(command)

    def capture_screenshots(self, running_minutes=5, throttle=300):
        # create and push fastbot files
        file_config = open("max.config", "w")
        file_config.write(
            "max.takeScreenshot = true\n" +
            "max.takeScreenshotForEveryStep = true"
        )
        file_config.close()
        cmd("adb push max.config /sdcard")
        cmd("adb push framework.jar /sdcard")
        cmd("adb push monkeyq.jar /sdcard")

        # start fastbot
        cmd("adb shell rm -r /sdcard/fastbot-output")
        command = "adb shell CLASSPATH=/sdcard/monkeyq.jar:/sdcard/framework.jar exec app_process /system/bin " + \
                  "com.android.commands.monkey.Monkey -p " + self.desired_caps["appPackage"] + \
                  " --agent robot --running-minutes " + str(running_minutes) + \
                  " --throttle " + str(throttle) + " -v -v --output-directory /sdcard/fastbot-output"
        # os.popen(command).read()
        os.system(command)

        # pull screenshots and arrange folders
        folder_app = os.path.join(folder_screenshots, self.desired_caps["appPackage"])
        if not os.path.exists(folder_app):
            os.mkdir(folder_app)
        cmd("adb pull /sdcard/fastbot-output {}".format(folder_app))
        # os.rename("{}/fastbot-output".format(self.desired_caps["appPackage"]),
        #           "{}/{}".format(self.desired_caps["appPackage"], self.versionCode))
        os.rename(os.path.join(folder_app, "fastbot-output"), os.path.join(folder_app, self.versionCode))


if __name__ == '__main__':
    # preparing
    paths_apk = traverse_files_with_ext(folder_apks, "apk")
    print("List of apk paths: {}".format(paths_apk))

    latest_versionCode = 0
    for i_path_apk in paths_apk:
        # collect app info
        app = App(i_path_apk)
        if int(app.versionCode) > latest_versionCode:
            latest_versionCode = int(app.versionCode)

        # start capturing
        app.install()
        app.capture_screenshots(running_minutes=running_minutes, throttle=throttle)
