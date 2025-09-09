#!/bin/bash
set -e

# TransRapport v0.1.0-pilot Linux Bundle Builder
# Creates AppImage, deb, and rpm packages

VERSION="0.1.0-pilot"
ARTIFACT_DIR="artifacts/linux"
BUILD_DIR="build/linux"

echo "🚀 Building TransRapport v${VERSION} Linux Bundles"
echo "================================================="

# Create directories
mkdir -p "${ARTIFACT_DIR}"
mkdir -p "${BUILD_DIR}"

# Build desktop UI first
echo "📦 Building desktop UI..."
cd desktop
npm install
npm run build
cd ..

# Create source archive
echo "📦 Creating source archive..."
tar --exclude='.git' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='.venv*' \
    --exclude='artifacts' \
    --exclude='build' \
    -czf "${ARTIFACT_DIR}/transrapport-${VERSION}-src.tar.gz" .

# Create minimal CLI bundle (Python + built UI)
echo "📦 Creating CLI bundle..."
CLI_BUNDLE_DIR="${BUILD_DIR}/transrapport-cli"
mkdir -p "${CLI_BUNDLE_DIR}"

# Copy core files
cp -r src/ "${CLI_BUNDLE_DIR}/"
cp me.py "${CLI_BUNDLE_DIR}/"
cp desktop/dist "${CLI_BUNDLE_DIR}/desktop-ui" -r
cp test-ui-wiring.js "${CLI_BUNDLE_DIR}/"

# Create launcher script
cat > "${CLI_BUNDLE_DIR}/transrapport" << 'EOF'
#!/bin/bash
# TransRapport v0.1.0-pilot Launcher
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"
python3 me.py "$@"
EOF
chmod +x "${CLI_BUNDLE_DIR}/transrapport"

# Create desktop entry
cat > "${CLI_BUNDLE_DIR}/transrapport.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=TransRapport
Comment=Offline Constitutional Analysis Tool
Exec=transrapport
Icon=transrapport
Terminal=false
Categories=Office;AudioVideo;
Keywords=transcription;analysis;constitutional;LD-3.4;
StartupWMClass=TransRapport
EOF

# Create CLI archive
cd "${BUILD_DIR}"
tar -czf "../${ARTIFACT_DIR}/transrapport-cli-${VERSION}-linux.tar.gz" transrapport-cli/
cd - > /dev/null

# Create AppImage structure (mock - requires appimagetool)
echo "📦 Creating AppImage structure..."
APPIMAGE_DIR="${BUILD_DIR}/TransRapport.AppDir"
mkdir -p "${APPIMAGE_DIR}/usr/bin"
mkdir -p "${APPIMAGE_DIR}/usr/share/applications"
mkdir -p "${APPIMAGE_DIR}/usr/share/icons/hicolor/256x256/apps"

# Copy files to AppImage structure
cp -r "${CLI_BUNDLE_DIR}"/* "${APPIMAGE_DIR}/usr/bin/"
cp "${CLI_BUNDLE_DIR}/transrapport.desktop" "${APPIMAGE_DIR}/"
ln -sf usr/bin/transrapport "${APPIMAGE_DIR}/AppRun"

# Create AppImage info (would need appimagetool to finalize)
echo "AppImage structure created. Use appimagetool to build final AppImage:"
echo "  appimagetool ${APPIMAGE_DIR} ${ARTIFACT_DIR}/TransRapport-${VERSION}-x86_64.AppImage"

# Create deb package structure
echo "📦 Creating deb package structure..."
DEB_DIR="${BUILD_DIR}/transrapport-deb"
mkdir -p "${DEB_DIR}/DEBIAN"
mkdir -p "${DEB_DIR}/usr/bin"
mkdir -p "${DEB_DIR}/usr/share/applications"
mkdir -p "${DEB_DIR}/usr/share/doc/transrapport"

# Copy files
cp -r "${CLI_BUNDLE_DIR}"/* "${DEB_DIR}/usr/bin/"
cp "${CLI_BUNDLE_DIR}/transrapport.desktop" "${DEB_DIR}/usr/share/applications/"

# Create control file
cat > "${DEB_DIR}/DEBIAN/control" << EOF
Package: transrapport
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: all
Depends: python3, python3-numpy, python3-scipy, nodejs
Maintainer: TransRapport Team <noreply@transrapport.com>
Description: Offline Constitutional Analysis Tool v${VERSION}
 Privacy-first offline desktop application for recording, transcribing,
 and analyzing professional conversations with LD-3.4 constitutional 
 framework and rapport indicators.
EOF

# Create deb package (would need dpkg-deb)
echo "deb package structure created. Use dpkg-deb to build:"
echo "  dpkg-deb --build ${DEB_DIR} ${ARTIFACT_DIR}/transrapport_${VERSION}_all.deb"

# Create RPM spec structure
echo "📦 Creating RPM spec structure..."
RPM_DIR="${BUILD_DIR}/rpm"
mkdir -p "${RPM_DIR}/SPECS"
mkdir -p "${RPM_DIR}/SOURCES"
mkdir -p "${RPM_DIR}/BUILD"
mkdir -p "${RPM_DIR}/RPMS"
mkdir -p "${RPM_DIR}/SRPMS"

# Create spec file
cat > "${RPM_DIR}/SPECS/transrapport.spec" << EOF
Name:           transrapport
Version:        ${VERSION//-/.}
Release:        1%{?dist}
Summary:        Offline Constitutional Analysis Tool

License:        Proprietary
URL:            https://github.com/transrapport/transrapport
Source0:        transrapport-%{version}-src.tar.gz

BuildArch:      noarch
Requires:       python3, python3-numpy, python3-scipy, nodejs

%description
Privacy-first offline desktop application for recording, transcribing,
and analyzing professional conversations with LD-3.4 constitutional 
framework and rapport indicators.

%prep
%setup -q

%build
# No build needed for Python application

%install
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/applications
cp -r src/ %{buildroot}/usr/bin/
cp me.py %{buildroot}/usr/bin/
cp desktop/dist %{buildroot}/usr/bin/desktop-ui -r
install -m 755 transrapport %{buildroot}/usr/bin/transrapport
install -m 644 transrapport.desktop %{buildroot}/usr/share/applications/

%files
/usr/bin/*
/usr/share/applications/transrapport.desktop

%changelog
* $(date '+%a %b %d %Y') TransRapport Team <noreply@transrapport.com> - ${VERSION//-/.}-1
- Initial release of v${VERSION}
EOF

cp "${ARTIFACT_DIR}/transrapport-${VERSION}-src.tar.gz" "${RPM_DIR}/SOURCES/"

echo "RPM spec created. Use rpmbuild to build:"
echo "  rpmbuild --define '_topdir ${PWD}/${RPM_DIR}' -ba ${RPM_DIR}/SPECS/transrapport.spec"

echo ""
echo "✅ Linux bundle structures created successfully!"
echo "📁 Artifacts directory: ${ARTIFACT_DIR}"
echo ""
echo "📦 Available bundles:"
ls -lah "${ARTIFACT_DIR}/"
echo ""
echo "🔧 To complete the builds, install the respective tools:"
echo "   - AppImage: appimagetool"  
echo "   - deb: dpkg-deb (usually pre-installed)"
echo "   - rpm: rpmbuild (part of rpm-build package)"