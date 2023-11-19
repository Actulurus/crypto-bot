# Use this script to test the bot with different arguments (short & long window).

import multiprocessing
import subprocess
import sys
import time
import os

from colorama import init, Fore, Back, Style

powerplan_script_exists = os.path.isfile("powerplan.py")

if powerplan_script_exists:
    from powerplan import allowsleep, forbidsleep

TEST_DURATION = int(sys.argv[1]) if len(sys.argv) > 1 else 60 * 30

def run_script(script_path, args):
    command = ["python", script_path] + args
    subprocess.run(command)

if __name__ == "__main__":
    print(Fore.YELLOW + "Starting test mode with duration of " + str(TEST_DURATION) + " seconds.")
    print("Started on " + str(time.time()) + ".")
    print(Fore.WHITE + "---------------------------------")

    if powerplan_script_exists:
        forbidsleep()

    # clear output folder (all files except .gitkeep)
    for file in os.listdir("TestOutput"):
        if file != ".gitkeep":
            os.remove("TestOutput/" + file)

    script_to_run = "main.py"

    script_arguments_list = [
        ['8', '18'],
        ['12', '25'],
        ['15', '32'],
        ['30', '64'],
        ['60', '128'],
    ]

    for args in script_arguments_list:
        args.append("True")
        args.append(str(TEST_DURATION))

    with multiprocessing.Pool() as pool:
        pool.starmap(run_script, [(script_to_run, args) for args in script_arguments_list])

    print(Fore.GREEN + "Log files saved to /TestOutput/")
    print(Fore.WHITE + "---------------------------------")

    if powerplan_script_exists:
        allowsleep()