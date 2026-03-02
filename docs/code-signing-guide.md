# Code Signing & Notarization Guide (macOS)

This guide documents the production release workflow for signing and notarizing `VoidBreaker.app`.

For v1.0 local distribution, signing and notarization are not required.

## Prerequisites

- Apple Developer Program membership (paid)
- A `Developer ID Application` certificate installed in Keychain Access
- Xcode command-line tools (`xcrun`, `codesign`, `notarytool`)
- Built app at `dist/VoidBreaker.app`

## 1) Verify signing identity

```bash
security find-identity -v -p codesigning
```

Choose the `Developer ID Application: <TEAM_NAME> (<TEAM_ID>)` identity.

## 2) Sign the app bundle

Create or use an entitlements file (for hardened runtime-enabled app signing), then run:

```bash
codesign --force --deep \
  --sign "Developer ID Application: <TEAM_NAME> (<TEAM_ID>)" \
  --options runtime \
  --entitlements entitlements.plist \
  dist/VoidBreaker.app
```

Validate signature:

```bash
codesign --verify --deep --strict --verbose=2 dist/VoidBreaker.app
spctl --assess --type execute --verbose dist/VoidBreaker.app
```

## 3) Notarize with Apple

Create zip payload and submit:

```bash
ditto -c -k --keepParent dist/VoidBreaker.app dist/VoidBreaker.zip

xcrun notarytool submit dist/VoidBreaker.zip \
  --apple-id "<APPLE_ID>" \
  --team-id "<TEAM_ID>" \
  --password "<APP_SPECIFIC_PASSWORD>" \
  --wait
```

`--wait` blocks until Apple completes the scan (usually 5–15 minutes).

## 4) Staple notarization ticket

```bash
xcrun stapler staple dist/VoidBreaker.app
xcrun stapler validate dist/VoidBreaker.app
```

## 5) Optional: notarize/sign DMG artifact

If distributing `dist/VoidBreaker.dmg`, sign and optionally notarize the DMG too:

```bash
codesign --force --sign "Developer ID Application: <TEAM_NAME> (<TEAM_ID>)" dist/VoidBreaker.dmg
spctl --assess --type open --verbose dist/VoidBreaker.dmg
```

## Unsigned v1.0 distribution workaround

When the app is unsigned/not-notarized, users may see a Gatekeeper warning.

Users can launch by either:

1. Right-click `VoidBreaker.app` -> `Open` -> confirm `Open`, or
2. Attempt to open once, then go to `System Settings -> Privacy & Security` and click `Open Anyway`.

## Notes

- Keep certificate names and Team IDs out of source control.
- Prefer storing notarization credentials in a keychain profile:

```bash
xcrun notarytool store-credentials "voidbreaker-notary" \
  --apple-id "<APPLE_ID>" \
  --team-id "<TEAM_ID>" \
  --password "<APP_SPECIFIC_PASSWORD>"
```

Then submit with:

```bash
xcrun notarytool submit dist/VoidBreaker.zip --keychain-profile "voidbreaker-notary" --wait
```