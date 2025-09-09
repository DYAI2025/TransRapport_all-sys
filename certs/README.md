# Code Signing Certificate Management

This directory manages certificates and keys for cross-platform code signing.

## Directory Structure

```
certs/
├── windows/                    # Windows code signing
│   ├── azure-key-vault.json   # Azure Key Vault configuration
│   └── signing-config.json    # Windows signing configuration
├── macos/                      # macOS code signing  
│   ├── developer-cert.p12     # Apple Developer certificate (not committed)
│   └── signing-config.json    # macOS signing configuration
├── linux/                     # Linux GPG signing
│   ├── transrapport.asc       # Public GPG key
│   └── signing-config.json    # Linux signing configuration
└── README.md                   # This file
```

## Security Guidelines

### ⚠️ CRITICAL SECURITY RULES

1. **NEVER commit private keys or certificates to git**
2. **Use environment variables or secure key management**  
3. **Rotate certificates according to platform requirements**
4. **Use Hardware Security Modules (HSM) for production**

### Certificate Requirements by Platform

#### Windows (.msi, .exe)
- **Required**: Extended Validation (EV) code signing certificate
- **Storage**: Azure Key Vault (HSM-backed) or local HSM device
- **Algorithm**: SHA256 with RSA 2048-bit minimum
- **Timestamping**: Required (RFC 3161 server)
- **Validity**: Maximum 3 years, annual validation required

#### macOS (.dmg, .app)
- **Required**: Apple Developer certificate from Apple Developer Account
- **Storage**: Keychain or CI/CD environment variables
- **Types**: Developer ID Application + Developer ID Installer
- **Notarization**: Required for macOS 10.15+ compatibility
- **Validity**: 5 years maximum

#### Linux (.deb, .rpm, .AppImage)  
- **Required**: GPG key for package signing
- **Storage**: GPG keyring or environment variables
- **Algorithm**: RSA 4096-bit minimum
- **Validity**: No expiration recommended for continuous distribution

## Environment Variables

Configure these in your CI/CD environment:

### Windows (Azure Key Vault)
```bash
AZURE_CLIENT_ID=<application-id>
AZURE_CLIENT_SECRET=<client-secret>
AZURE_TENANT_ID=<tenant-id>
AZURE_KEY_VAULT_URL=<vault-url>
AZURE_CERTIFICATE_NAME=<cert-name>
```

### macOS (Apple Developer)
```bash
APPLE_CERTIFICATE=<base64-encoded-p12-file>
APPLE_CERTIFICATE_PASSWORD=<p12-password>
APPLE_SIGNING_IDENTITY=<developer-id>
APPLE_TEAM_ID=<team-id>
```

### Linux (GPG)
```bash
GPG_PRIVATE_KEY=<base64-encoded-private-key>
GPG_PASSPHRASE=<key-passphrase>
GPG_KEY_ID=<key-id>
```

## Local Development Setup

### 1. Windows Development
```bash
# Install Azure CLI and login
az login
az keyvault certificate show --vault-name <vault-name> --name <cert-name>

# Configure local signing
python -m src.cli.package_cli sign \
  --package-path "./dist/installer.msi" \
  --platform windows \
  --certificate-source azure_key_vault
```

### 2. macOS Development  
```bash
# Install certificate in Keychain
security import developer-cert.p12 -k ~/Library/Keychains/login.keychain-db

# Configure local signing
python -m src.cli.package_cli sign \
  --package-path "./dist/installer.dmg" \
  --platform macos \
  --certificate-source apple_developer
```

### 3. Linux Development
```bash  
# Import GPG key
gpg --import private-key.asc

# Configure local signing
python -m src.cli.package_cli sign \
  --package-path "./dist/installer.deb" \
  --platform linux \
  --certificate-source local_certificate
```

## Certificate Validation

Test certificates before deployment:

```bash
# Validate Windows certificate
python -m src.cli.package_cli validate \
  --package-path "./dist/installer.msi" \
  --validation-type security

# Validate macOS certificate  
python -m src.cli.package_cli validate \
  --package-path "./dist/installer.dmg" \
  --validation-type security

# Validate Linux signature
python -m src.cli.package_cli validate \
  --package-path "./dist/installer.deb" \
  --validation-type security
```

## Troubleshooting

### Common Issues

1. **Windows**: "Certificate not found in Azure Key Vault"
   - Verify AZURE_* environment variables
   - Check Key Vault permissions
   - Ensure certificate is not expired

2. **macOS**: "Developer ID not found in Keychain"
   - Import certificate: `security import cert.p12`
   - Check Keychain Access application
   - Verify Apple Developer Account status

3. **Linux**: "GPG key not found"
   - Import key: `gpg --import private-key.asc`
   - Check key status: `gpg --list-secret-keys`
   - Verify passphrase is correct

### Support Contacts

- **Windows Certificates**: Azure support or CA provider
- **macOS Certificates**: Apple Developer support
- **Linux GPG**: Community support or internal security team

## Compliance Notes

- All certificates meet current security standards (2025)
- HSM usage required for production Windows signing
- Certificate transparency logging enabled where supported
- Regular security audits recommended quarterly