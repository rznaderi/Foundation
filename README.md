# Foundation Bearing Capacity Android App

This project converts the uploaded Python calculation into a Kivy Android application.

## Files
- main.py: Android/Kivy application
- buildozer.spec: Buildozer configuration

## Build on Linux/WSL
1. Install Python, Java and Buildozer.
2. Open a terminal in this folder.
3. Run:
   buildozer android debug
4. The APK will be created in `bin/`.

The calculation equations are based on the uploaded Python program. The desktop `input()` prompts were replaced by Android form controls and the Matplotlib plots are displayed inside the app.
