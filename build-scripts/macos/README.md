# macOS Build Scripts

This directory contains scripts for building pylibssh wheels on macOS.

## Architecture

To optimize CI performance, we use **pre-built libssh artifacts** instead of building from source on every CI run:

1. **Pre-built artifacts** are stored on GitHub Releases
2. **Download script** (`download-libssh-macos.sh`) fetches these artifacts
3. **Fallback to source build** if download fails

This mirrors the manylinux approach which uses pre-built container images.

## Scripts

### `cibuildwheel-before-build.sh`
Main entry point called by cibuildwheel before building wheels.
- Determines target architecture (arm64, x86_64, or universal2)
- Downloads or builds libssh for each architecture
- Merges into universal2 if needed
- Writes static deps path for the build backend

### `download-libssh-macos.sh`
Downloads pre-built libssh+OpenSSL artifacts from GitHub Releases.

**Usage:**
```bash
./download-libssh-macos.sh <libssh_version> <arch>
```

**Example:**
```bash
./download-libssh-macos.sh 0.12.0 arm64
```

### `build-libssh-macos.sh`
Builds libssh and OpenSSL from source for a specific architecture.

**Usage:**
```bash
./build-libssh-macos.sh <libssh_version> <arch>
```

**Outputs:**
- Static libraries in `build-scripts/macos/build/<arch>/`
- Tarball: `libssh-<version>-openssl-<version>-macos-<arch>.tar.gz`
- SHA256 checksum: `<tarball>.sha256`

### `merge-universal2.sh`
Merges arm64 and x86_64 libraries into universal2 binaries using `lipo`.

**Usage:**
```bash
./merge-universal2.sh <arm64_dir> <x86_64_dir> <output_dir>
```

### `config.sh`
Version configuration file defining:
- `LIBSSH_VERSION`
- `OPENSSL_VERSION`
- `OPENSSL_SHA256`

## Publishing Pre-built Artifacts

### Building Artifacts

To create pre-built artifacts for a new version:

```bash
# Update versions in config.sh first
./build-libssh-macos.sh 0.12.0 arm64
./build-libssh-macos.sh 0.12.0 x86_64
```

This produces tarballs in `build-scripts/macos/build/<arch>/`:
- `libssh-0.12.0-openssl-3.5.0-macos-arm64.tar.gz`
- `libssh-0.12.0-openssl-3.5.0-macos-arm64.tar.gz.sha256`
- `libssh-0.12.0-openssl-3.5.0-macos-x86_64.tar.gz`
- `libssh-0.12.0-openssl-3.5.0-macos-x86_64.tar.gz.sha256`

### Publishing to GitHub Releases

1. **Create a GitHub Release:**
   ```bash
   # Tag format: libssh-v<VERSION>-openssl-<VERSION>
   gh release create libssh-v0.12.0-openssl-3.5.0 \
     --title "libssh 0.12.0 + OpenSSL 3.5.0 for macOS" \
     --notes "Pre-built static libraries for macOS wheel builds"
   ```

2. **Upload artifacts:**
   ```bash
   gh release upload libssh-v0.12.0-openssl-3.5.0 \
     build-scripts/macos/build/arm64/libssh-*.tar.gz \
     build-scripts/macos/build/arm64/libssh-*.tar.gz.sha256 \
     build-scripts/macos/build/x86_64/libssh-*.tar.gz \
     build-scripts/macos/build/x86_64/libssh-*.tar.gz.sha256
   ```

3. **Verify artifacts are downloadable:**
   ```bash
   # Test download
   ./download-libssh-macos.sh 0.12.0 arm64
   ```

## CI Workflow

In CI (via cibuildwheel):

```
cibuildwheel
  ↓
before-build: cibuildwheel-before-build.sh
  ↓
For each architecture:
  ├─→ Try download-libssh-macos.sh
  │   └─→ ✓ Success → Use pre-built artifact
  └─→ ✗ Failed → build-libssh-macos.sh (fallback)
  ↓
If universal2: merge-universal2.sh
  ↓
Write .macos-static-deps-path
  ↓
Build wheel (uses CFLAGS/LDFLAGS from pyproject.toml)
```

## Benefits

- **Faster CI:** No expensive rebuilds on every run
- **Consistent builds:** Same binaries used across all wheel builds
- **Bandwidth efficient:** Download ~5MB instead of building
- **Fallback safety:** Builds from source if download fails
- **Version control:** Explicit artifact versioning via releases

## Updating Dependencies

When updating libssh or OpenSSL versions:

1. Update `config.sh` with new versions and SHA256
2. Build new artifacts locally
3. Test the build locally
4. Create GitHub release with new tag
5. Upload artifacts
6. CI will automatically use new artifacts on next run
