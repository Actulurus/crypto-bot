# Use this script to test the bot with different arguments (short & long window).

import multiprocessing
import subprocess

TEST_DURATION = 15 #60 * 60 * 8 # In seconds

def run_script(script_path, args):
    command = ["python", script_path] + args
    subprocess.run(command)

if __name__ == "__main__":
    script_to_run = "main.py"

    script_arguments_list = [
        ['3', '6'],
        ['3', '12'],
        ['5', '10'],
        ['5', '20'],
        ['10', '20'],
        ['10', '40'],
        ['15', '30'],
        ['15', '60'],
    ]

    for args in script_arguments_list:
        args.append("True")
        args.append(str(TEST_DURATION))

    with multiprocessing.Pool() as pool:
        pool.starmap(run_script, [(script_to_run, args) for args in script_arguments_list])