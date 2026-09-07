[app]
p4a.local_recipes = ./p4a-recipes

title = Foundation Bearing Capacity
package.name = foundationcapacity
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas
source.exclude_dirs = bin, .git, __pycache__

version = 1.0.0

requirements = python3,kivy,numpy,matplotlib

orientation = portrait
fullscreen = 0
android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 1
