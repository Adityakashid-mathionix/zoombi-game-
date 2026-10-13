"""
Google Colab & Linux 1-Click APK Builder for Zombi Apploclips
=============================================================
This script builds the Android APK in Google Colab or on any Ubuntu/Debian system.

How to use in Google Colab (https://colab.research.google.com/):
  1. Open Google Colab and click "New Notebook".
  2. In the first code cell, simply paste:
         !git clone https://github.com/yashahire213-debug/zoombi-game-.git
         %cd zoombi-game-
         !python build_apk_colab.py
  3. Run the cell. The script will automatically install all prerequisites,
     compile the Android APK with Buildozer, and prompt you to download the file!
"""

import os
import sys
import glob
import subprocess


def run_command(cmd, description=""):
    """Execute a system shell command with live stdout/stderr streaming."""
    if description:
        print(f"\n[+] {description}...")
        print(f"    Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"[!] Warning: Command finished with exit code {result.returncode}: {cmd}")
    return result.returncode


def main():
    print("=" * 70)
    print("  ZOMBI APPLOCLIPS - ANDROID APK CLOUD COMPILER")
    print("=" * 70)

    # 1. Verify working directory
    repo_url = "https://github.com/yashahire213-debug/zoombi-game-.git"
    if not os.path.exists("buildozer.spec") and not os.path.exists("main.py"):
        print("\n[*] Game files not found in current folder.")
        print(f"[*] Cloning repository from: {repo_url}")
        run_command(f"git clone {repo_url} game_repo", "Cloning game repository")
        if os.path.exists("game_repo"):
            os.chdir("game_repo")
        else:
            print("[!] Clone failed. Checking if zip file is uploaded...")
            zips = glob.glob("*.zip")
            if zips:
                run_command(f"unzip -o {zips[0]}", f"Unpacking {zips[0]}")
            else:
                try:
                    from google.colab import files
                    print("[*] Please upload Zombi_Apploclips_Source_For_APK.zip:")
                    uploaded = files.upload()
                    for f in uploaded.keys():
                        if f.endswith(".zip"):
                            run_command(f"unzip -o '{f}'", f"Unpacking {f}")
                except ImportError:
                    print("[!] Not running in Colab and no files found. Exiting.")
                    sys.exit(1)

    # 2. Update system packages and install Linux Buildozer dependencies
    print("\n" + "=" * 70)
    print("  STEP 1: Installing Ubuntu dependencies & OpenJDK 17")
    print("=" * 70)
    run_command("sudo apt-get update -qq", "Updating apt package index")
    run_command(
        "sudo apt-get install -y -qq "
        "git zip unzip autoconf libtool pkg-config zlib1g-dev "
        "libncurses5-dev libncursesw5-dev libtinfo6 cmake libffi-dev "
        "libssl-dev build-essential ccache openjdk-17-jdk",
        "Installing build toolchains & Java SDK"
    )

    # 3. Install Buildozer & Cython
    print("\n" + "=" * 70)
    print("  STEP 2: Installing Buildozer & Cython")
    print("=" * 70)
    run_command(
        "pip install --upgrade Cython==0.29.36 buildozer python-for-android",
        "Installing Python packaging packages"
    )

    # 4. Ensure SDK license acceptance is set in buildozer.spec
    if os.path.exists("buildozer.spec"):
        with open("buildozer.spec", "r", encoding="utf-8") as f:
            spec_content = f.read()
        if "android.accept_sdk_license = True" not in spec_content:
            spec_content = spec_content.replace(
                "[app]",
                "[app]\nandroid.accept_sdk_license = True"
            )
            with open("buildozer.spec", "w", encoding="utf-8") as f:
                f.write(spec_content)

    # 5. Compile Android APK
    print("\n" + "=" * 70)
    print("  STEP 3: Compiling Android APK with Buildozer")
    print("=" * 70)
    exit_code = run_command("buildozer -v android debug", "Building APK")

    # 6. Locate and download the APK
    print("\n" + "=" * 70)
    print("  STEP 4: Locating Compiled APK")
    print("=" * 70)
    apk_files = glob.glob("bin/*.apk")
    if apk_files:
        compiled_apk = apk_files[0]
        size_mb = os.path.getsize(compiled_apk) / (1024 * 1024)
        print(f"\n[✓] SUCCESS! Compiled APK: {compiled_apk} ({size_mb:.2f} MB)")
        try:
            from google.colab import files
            print("[*] Initiating automatic browser download in Colab...")
            files.download(compiled_apk)
        except ImportError:
            print(f"[*] APK is ready in: {os.path.abspath(compiled_apk)}")
    else:
        print("[!] No .apk was found in the bin/ directory.")
        print("[!] Review the Buildozer logs above for build details.")
        sys.exit(exit_code or 1)


if __name__ == "__main__":
    main()
