# Locpost

Locpost is a Flutter project prepared for Android app development.

## Requirements

- Flutter SDK
- Android Studio or the Android SDK command line tools
- An Android emulator or a physical Android device with USB debugging enabled

## Setup

```sh
flutter doctor
flutter pub get
flutter devices
```

If Android Studio is installed, create or start an emulator from Device Manager.
For a phone, enable Developer Options and USB debugging, then connect it by USB.

## Run on Android

```sh
flutter run
```

To target a specific device:

```sh
flutter run -d <device-id>
```

## Development Commands

```sh
flutter analyze
flutter test
flutter build apk --debug
flutter build apk --release
```

The main app entry point is `lib/main.dart`. Android-specific configuration is
in `android/app/build.gradle.kts` and `android/app/src/main/AndroidManifest.xml`.
