#!/usr/bin/env python3
import subprocess

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def check_github():
    success, stdout, stderr = run_command("git remote -v")
    print("GitHub check result:", success)
    print("Output:", stdout)
    print("Error:", stderr)
    return "github.com" in stdout.lower()

if __name__ == "__main__":
    check_github()
