import subprocess

try:
# Arm Installation Ref: https://askubuntu.com/questions/1243252/how-to-install-arm-none-eabi-gdb-on-ubuntu-20-04-lts-focal-fossa
    subprocess.check_call(["sudo", "apt", "remove", "gcc-arm-none-eabi"])
    subprocess.check_call(["sudo", "tar", "xjf","gcc-arm-none-eabi-10.3-2021.10-x86_64-linux.tar.bz2", "-C", "/usr/share/"])

    subprocess.check_call(["sudo", "ln", "-s", "/usr/share/gcc-arm-none-eabi-10.3-2021.10-x86_64-linux/bin/arm-none-eabi-gcc", "/usr/bin/arm-none-eabi-gcc"])
    subprocess.check_call(["sudo", "ln", "-s", "/usr/share/gcc-arm-none-eabi-10.3-2021.10-x86_64-linux/bin/arm-none-eabi-g++", "/usr/bin/arm-none-eabi-g++"])
    subprocess.check_call(["sudo", "ln", "-s", "/usr/share/gcc-arm-none-eabi-10.3-2021.10-x86_64-linux/bin/arm-none-eabi-size", "/usr/bin/arm-none-eabi-size"])
    subprocess.check_call(["sudo", "ln", "-s", "/usr/share/gcc-arm-none-eabi-10.3-2021.10-x86_64-linux/bin/arm-none-eabi-objcopy", "/usr/bin/arm-none-eabi-objcopy"])
    print("Successfuly installed Arm Compilation Tools...")
except subprocess.CalledProcessError as err:
    print("Arm Installation may have Failed...")
#Install Jsoncpp 
try:
    # Compiler Packages
    subprocess.check_call(["sudo", "apt", "install", "python3", "python-dev", "g++", "make"])
    # JsonCpp
    subprocess.check_call(["sudo", "apt", "install", "libtool", "flex", "bison", "pkg-config", "libjsoncpp-dev"])


except subprocess.CalledProcessError as err:
    print("Program Tools/Libraries/Dependencies have failed to install...")