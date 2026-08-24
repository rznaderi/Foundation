# Build the APK with GitHub Actions

1. Create a new GitHub repository.
2. Upload all files in this project to the repository.
3. Make sure `.github/workflows/build-apk.yml` is included.
4. Commit the files to the `main` branch.
5. Open **Actions** on GitHub.
6. Select **Build Android APK**.
7. Click **Run workflow**.
8. Wait for the build to finish.
9. Open the completed workflow run.
10. Under **Artifacts**, download `foundation-capacity-apk`.
11. Extract the artifact to get the `.apk` file.

This workflow builds a debug APK for testing/installation on Android. It is not a signed release build for Google Play.
