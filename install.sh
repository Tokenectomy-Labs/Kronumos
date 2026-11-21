#!/usr/bin/env bash
# Kronumos CLI Installer (v1.3.0)
# Installs the Kronumos Autonomous Engineering Agent

set -e

VERSION="1.3.0"

if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
    BOLD='\033[1;37m'
    DIM='\033[2;37m'
    ERR='\033[1;31m'
    RST='\033[0m'
else
    BOLD=''
    DIM=''
    ERR=''
    RST=''
fi

printf "\n"
printf "  ${BOLD}┌─ KRONUMOS CORE · INSTALLER v%s${RST}\n" "$VERSION"
printf "  ${DIM}│  Autonomous Software Engineering CLI (Native Rust)${RST}\n"
printf "  ${DIM}└───────────────────────────────────────────────────${RST}\n\n"

INSTALL_DIR="${CARGO_HOME:-$HOME/.cargo}/bin"
mkdir -p "$INSTALL_DIR"

printf "  ${BOLD}◆${RST} Detecting platform & architecture...\n"
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
BIN_EXT=""
case "$OS" in
    linux*) OS="linux" ;;
    darwin*) OS="darwin" ;;
    mingw*|msys*|cygwin*|windows*)
        OS="windows"
        BIN_EXT=".exe"
        ;;
esac
ARCH="$(uname -m)"
case "$ARCH" in
    x86_64|amd64) ARCH="amd64" ;;
    aarch64|arm64) ARCH="arm64" ;;
    *) printf "  ${ERR}▲${RST} Unsupported architecture: %s\n" "$ARCH"; exit 1 ;;
esac
printf "    ${DIM}↳ Target: %s-%s${RST}\n" "$OS" "$ARCH"

if [ "${OS}-${ARCH}" != "linux-amd64" ] && [ "${OS}-${ARCH}" != "windows-amd64" ]; then
    printf "  ${ERR}▲${RST} Pre-compiled native binaries are currently published for linux-amd64 and windows-amd64 (detected: %s-%s).\n" "$OS" "$ARCH"
    printf "    ${DIM}↳ macOS & Linux ARM64 builds are in active release staging — track status at https://kronumos.com/changelog${RST}\n"
    exit 1
fi

printf "  ${BOLD}◆${RST} Downloading Kronumos CLI v%s (%s-%s)...\n" "$VERSION" "$OS" "$ARCH"
DIRECT_PAGES_URL="https://kronumos.com/kronumos-${OS}-${ARCH}${BIN_EXT}"
CDN_URL="https://dl.kronumos.com/kronumos-${OS}-${ARCH}${BIN_EXT}"
PAGES_URL="https://kronumos.com/releases/kronumos-${OS}-${ARCH}${BIN_EXT}"
TEMP_FILE="$(mktemp)"
TEMP_SHA="$(mktemp)"

DOWNLOADED_FROM=""
if command -v curl >/dev/null 2>&1; then
    if curl -fsSL "$DIRECT_PAGES_URL" -o "$TEMP_FILE" 2>/dev/null; then
        DOWNLOADED_FROM="$DIRECT_PAGES_URL"
    elif curl -fsSL "$CDN_URL" -o "$TEMP_FILE" 2>/dev/null; then
        DOWNLOADED_FROM="$CDN_URL"
    elif curl -fsSL "$PAGES_URL" -o "$TEMP_FILE" 2>/dev/null; then
        DOWNLOADED_FROM="$PAGES_URL"
    fi
else
    printf "    ${DIM}↳ curl not found; skipping prebuilt binary download.${RST}\n"
fi

if [ -n "$DOWNLOADED_FROM" ]; then
    SHA_URL="${DOWNLOADED_FROM}.sha256"
    FALLBACK_SHA_URL="${DIRECT_PAGES_URL}.sha256"
    CDN_SHA_URL="${CDN_URL}.sha256"
    EXPECTED_SHA=""
    for CANDIDATE_URL in "$SHA_URL" "$FALLBACK_SHA_URL" "$CDN_SHA_URL"; do
        if curl -fsSL "$CANDIDATE_URL" -o "$TEMP_SHA" 2>/dev/null; then
            CANDIDATE_SHA="$(awk '{print $1}' "$TEMP_SHA" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"
            if printf '%s' "$CANDIDATE_SHA" | grep -Eq '^[0-9a-f]{64}$'; then
                EXPECTED_SHA="$CANDIDATE_SHA"
                break
            fi
        fi
    done
    rm -f "$TEMP_SHA"

    if [ -z "$EXPECTED_SHA" ]; then
        printf "  ${ERR}▲${RST} Could not download a valid 64-character SHA-256 checksum manifest from %s (fail-closed verification).\n" "$SHA_URL"
        rm -f "$TEMP_FILE"
        exit 1
    fi

    ACTUAL_SHA=""
    if command -v sha256sum >/dev/null 2>&1; then
        ACTUAL_SHA="$(sha256sum "$TEMP_FILE" | awk '{print $1}' | tr '[:upper:]' '[:lower:]')"
    elif command -v shasum >/dev/null 2>&1; then
        ACTUAL_SHA="$(shasum -a 256 "$TEMP_FILE" | awk '{print $1}' | tr '[:upper:]' '[:lower:]')"
    else
        printf "  ${ERR}▲${RST} SHA-256 verification requires 'sha256sum' or 'shasum' (fail-closed verification).\n"
        rm -f "$TEMP_FILE"
        exit 1
    fi

    if [ -z "$ACTUAL_SHA" ]; then
        printf "  ${ERR}▲${RST} Failed to compute SHA-256 digest of downloaded binary (fail-closed verification).\n"
        rm -f "$TEMP_FILE"
        exit 1
    fi

    if [ "$EXPECTED_SHA" != "$ACTUAL_SHA" ]; then
        printf "  ${ERR}▲${RST} SHA-256 checksum verification failed!\n"
        printf "    ${DIM}↳ Expected: %s${RST}\n" "$EXPECTED_SHA"
        printf "    ${DIM}↳ Actual:   %s${RST}\n" "$ACTUAL_SHA"
        rm -f "$TEMP_FILE"
        exit 1
    fi
    printf "    ${BOLD}✔${RST} ${DIM}SHA-256 verified (${ACTUAL_SHA:0:12}...)${RST}\n"

    printf "  ${BOLD}◆${RST} Installing binary to %s/kronumos%s...\n" "$INSTALL_DIR" "$BIN_EXT"
    chmod +x "$TEMP_FILE"
    mv "$TEMP_FILE" "$INSTALL_DIR/kronumos${BIN_EXT}"
    if [ -d "$HOME/.local/bin" ] && [ "$INSTALL_DIR" != "$HOME/.local/bin" ]; then
        cp -f "$INSTALL_DIR/kronumos${BIN_EXT}" "$HOME/.local/bin/kronumos${BIN_EXT}" 2>/dev/null || true
    fi
    printf "  ${BOLD}✔ Kronumos v%s installed cleanly.${RST}\n" "$VERSION"
else
    rm -f "$TEMP_FILE" "$TEMP_SHA"
    if [ -f "engines/kronumos-core/Cargo.toml" ] && command -v cargo >/dev/null 2>&1; then
        printf "  ${BOLD}◆${RST} Compiling Kronumos v%s from local workspace...\n" "$VERSION"
        cargo install --path "engines/kronumos-core" --force
        printf "  ${BOLD}✔ Kronumos v%s compiled and installed.${RST}\n" "$VERSION"
    else
        printf "  ${ERR}▲${RST} Failed to download pre-compiled binary for %s-%s.\n" "$OS" "$ARCH"
        printf "    ${DIM}↳ Visit https://kronumos.com/download for platform artifacts.${RST}\n"
        exit 1
    fi
fi

if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    printf "\n  ${BOLD}▲${RST} %s is not in your PATH.\n" "$INSTALL_DIR"
    printf "    ${DIM}↳ Add to ~/.bashrc or ~/.zshrc: export PATH=\"%s:\$PATH\"${RST}\n" "$INSTALL_DIR"
fi

printf "\n  ${DIM}Next steps:${RST}\n"
printf "    ${BOLD}kronumos${RST}         ${DIM}Launch interactive workbench & slash palette${RST}\n"
printf "    ${BOLD}kronumos setup${RST}   ${DIM}Configure BYOK API key, local Ollama, or Kronumos Cloud${RST}\n"
printf "    ${BOLD}kronumos update${RST}  ${DIM}Self-update anytime (or /update inside REPL)${RST}\n"
printf "    ${BOLD}/hunt  /fix${RST}      ${DIM}0-LLM AST bug audit & autonomous test repair${RST}\n\n"
