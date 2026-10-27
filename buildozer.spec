[app]

# (str) Title of your application
title = Zombi Apploclips

# (str) Package name
package.name = zombi_apploclips

# (str) Package domain (needed for android/ios packaging)
package.domain = org.zombiapploclips

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,wav,mp3,ogg,m4a,webp,json,txt,spec,ttf,otf

# (list) List of directory to include
source.include_dirs = assets,backend,engine,ui

# (list) List of exclusions using pattern matching
source.exclude_patterns = reference_doom/*,.git/*,__pycache__/*,*.zip,*.tar.gz,scratch/*

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,hostpython3,sdl2,pygame-ce

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/assets/ui/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/ui/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = landscape

# (list) List of services to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# Android specific
#

# (bool) Fullscreen mode
fullscreen = 1

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,VIBRATE

# (bool) Automatically accept Android SDK license
android.accept_sdk_license = True

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK / AAB will support.
android.minapi = 24

# (int) Android SDK version to use
# android.sdk = 34

# (str) Android NDK version to use
# android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) python-for-android git clone url
p4a.url = https://github.com/AnGlonchas/python-for-android.git

# (str) python-for-android branch to use, defaults to master
p4a.branch = develop

# (str) The directory in which python-for-android should look for your own build recipes
p4a.local_recipes = ./recipes

# (str) Bootstrap to use for android
p4a.bootstrap = sdl2

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
#p4a.port =

# (list) List of Java classes to add to the android manifest
#android.add_javaclass =

# (list) Android additionnal libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so
#android.add_libs_armeabi_v7a = libs/android-v7/*.so
#android.add_libs_arm64_v8a = libs/android-v8/*.so
#android.add_libs_x86 = libs/android-x86/*.so
#android.add_libs_mips = libs/android-mips/*.so

# (bool) Indicate whether the screen should stay on
# Don't forget to add the WAKE_LOCK permission if you set this to True
#android.wakelock = False

# (list) Android application meta-data to set (key=value format)
#android.meta_data =

# (list) Android library project to add (will be added in the project.properties)
#android.library_references =

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libdir and softlink
#android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# In past, was `android.arch` as string, now `android.archs` as list.

# (list) The Android add-manifest properties to set
#android.add_manifest =

# (list) Android additional manifest arguments
#android.extra_manifest_args =

# (list) Android whitelist of filenames or relative paths
#android.whitelist =

#
# Buildozer
#

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug with command output)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, default to (parent of this file)/.buildozer
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin
