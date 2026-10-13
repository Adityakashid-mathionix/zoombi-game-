# ==============================================================================
# Google Colab 1-Click APK Builder for Zombi Apploclips
# ==============================================================================
# Instructions:
# 1. Open Google Colab in your browser: https://colab.research.google.com/
# 2. Click "New Notebook"
# 3. Copy and run the following code blocks:

# --- Cell 1: Install Buildozer & System Dependencies ---
!sudo apt-get update -qq
!sudo apt-get install -y -qq git zip unzip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev build-essential ccache openjdk-17-jdk
!pip install --upgrade Cython==0.29.36 buildozer python-for-android

# --- Cell 2: Upload the Game Source Zip ---
# Upload "Zombi_Apploclips_Source_For_APK.zip" from your computer:
from google.colab import files
import os

if not os.path.exists("main.py"):
    uploaded = files.upload()
    for filename in uploaded.keys():
        if filename.endswith(".zip"):
            !unzip -o "$filename"

# --- Cell 3: Build the Android APK ---
!buildozer -v android debug

# --- Cell 4: Automatic Download of the Compiled APK ---
import glob
from google.colab import files

apk_files = glob.glob("bin/*.apk")
if apk_files:
    print(f"Build successful! Downloading APK: {apk_files[0]}")
    files.download(apk_files[0])
else:
    print("No APK found in bin/. Check the build logs above.")
