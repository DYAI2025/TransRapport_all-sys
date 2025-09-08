#!/bin/bash
# TransRapport Doc Validator - Production Installation Script
# Author: TransRapport Team
# Version: 1.0.0

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
INSTALL_PREFIX="${INSTALL_PREFIX:-/usr/local}"
PYTHON_EXECUTABLE="${PYTHON_EXECUTABLE:-python3}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python version
    if ! command -v "$PYTHON_EXECUTABLE" &> /dev/null; then
        log_error "Python 3.11+ is required but not found at $PYTHON_EXECUTABLE"
    fi
    
    local python_version
    python_version=$("$PYTHON_EXECUTABLE" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    local major_version=${python_version%.*}
    local minor_version=${python_version#*.}
    
    if [[ $major_version -lt 3 ]] || [[ $major_version -eq 3 && $minor_version -lt 11 ]]; then
        log_error "Python 3.11+ is required, but found Python $python_version"
    fi
    
    log_info "Python $python_version found - compatible"
    
    # Check pip
    if ! "$PYTHON_EXECUTABLE" -m pip --version &> /dev/null; then
        log_error "pip is required but not found"
    fi
    
    log_info "Prerequisites check passed"
}

install_package() {
    log_info "Installing TransRapport Doc Validator..."
    
    # Create virtual environment if not exists
    local venv_dir="${INSTALL_PREFIX}/share/transrapport-doc-validator/venv"
    if [[ ! -d "$venv_dir" ]]; then
        log_info "Creating virtual environment at $venv_dir"
        sudo mkdir -p "$(dirname "$venv_dir")"
        sudo "$PYTHON_EXECUTABLE" -m venv "$venv_dir"
    fi
    
    # Install the package
    sudo "$venv_dir/bin/python" -m pip install --upgrade pip
    sudo "$venv_dir/bin/python" -m pip install -e "$SCRIPT_DIR"
    
    # Create executable wrapper
    local wrapper_script="${INSTALL_PREFIX}/bin/transrapport-docs"
    sudo tee "$wrapper_script" > /dev/null << EOF
#!/bin/bash
exec "$venv_dir/bin/python" -m doc_validator.cli.main "\$@"
EOF
    sudo chmod +x "$wrapper_script"
    
    log_info "Package installed successfully"
    log_info "Command available as: transrapport-docs"
}

verify_installation() {
    log_info "Verifying installation..."
    
    if ! command -v transrapport-docs &> /dev/null; then
        log_error "Installation verification failed - command not found"
    fi
    
    # Test basic command
    if ! transrapport-docs --version &> /dev/null; then
        log_error "Installation verification failed - command execution error"
    fi
    
    log_info "Installation verified successfully"
}

show_usage() {
    log_info "Installation complete!"
    echo ""
    echo "Usage examples:"
    echo "  transrapport-docs docs validate /path/to/docs/"
    echo "  transrapport-docs docs validate --strict --format json /path/to/docs/"
    echo ""
    echo "For more information, run: transrapport-docs --help"
}

main() {
    log_info "TransRapport Doc Validator - Production Installation"
    log_info "================================================="
    
    check_prerequisites
    install_package
    verify_installation
    show_usage
    
    log_info "Installation completed successfully!"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi