# ==============================================================================
# Google Colab 1-Click APK Builder for Zombie Quarantine FPS Mobile Engine
# ==============================================================================
# 1. Open Google Colab: https://colab.research.google.com/
# 2. Select: Runtime -> Change runtime type -> Python 3
# 3. Create a code cell and paste the following commands:

# Step 1: Install buildozer dependencies & JDK
!sudo apt-get update -qq
!sudo apt-get install -y -qq git zip unzip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev build-essential ccache openjdk-17-jdk

# Step 2: Install buildozer & cython
!pip install --upgrade Cython==0.29.36 buildozer python-for-android

# Step 3: Clone or upload your game repository
# !git clone <YOUR_GITHUB_REPO_URL> game
# %cd game

# Step 4: Build Android APK
!buildozer -v android debug

# Step 5: Download the generated APK directly from Google Colab
from google.colab import files
import glob

apk_files = glob.glob("bin/*.apk")
if apk_files:
    print(f"Generated APK: {apk_files[0]}")
    files.download(apk_files[0])
else:
    print("Build did not produce an APK file. Check the log output above.")
