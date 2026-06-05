[app]
title = Virtual Cloud Drive
package.name = virtualdrive
package.domain = org.zeeshan
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1
requirements = python3,kivy,google-api-python-client,google-auth-oauthlib,google-auth-httplib2,urllib3,requests
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk_api = 21
[buildozer]
log_level = 2
warn_on_root = 1
