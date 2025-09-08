#!/bin/bash
# TransRapport Doc Validator - Uninstallation Script
# Author: TransRapport Team
# Version: 1.0.0

set -euo pipefail

INSTALL_PREFIX="${INSTALL_PREFIX:-/usr/local}"

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
}

uninstall_package() {
    log_info "Uninstalling TransRapport Doc Validator..."
    
    # Remove executable wrapper
    local wrapper_script="${INSTALL_PREFIX}/bin/transrapport-docs"
    if [[ -f "$wrapper_script" ]]; then
        sudo rm -f "$wrapper_script"
        log_info "Removed command wrapper: $wrapper_script"
    fi
    
    # Remove virtual environment and data
    local venv_dir="${INSTALL_PREFIX}/share/transrapport-doc-validator"
    if [[ -d "$venv_dir" ]]; then
        sudo rm -rf "$venv_dir"
        log_info "Removed installation directory: $venv_dir"
    fi
    
    log_info "Uninstallation completed successfully"
}

verify_uninstall() {
    log_info "Verifying uninstallation..."
    
    if command -v transrapport-docs &> /dev/null; then
        log_warn "Command still found in PATH - may be installed elsewhere"
    else
        log_info "Command successfully removed from system"
    fi
}

main() {
    log_info "TransRapport Doc Validator - Uninstallation"
    log_info "=========================================="
    
    read -p "Are you sure you want to uninstall TransRapport Doc Validator? [y/N]: " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Uninstallation cancelled"
        exit 0
    fi
    
    uninstall_package
    verify_uninstall
    
    log_info "Thank you for using TransRapport Doc Validator!"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi