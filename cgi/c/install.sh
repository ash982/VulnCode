#!/bin/bash

# Installation script for CGI programs

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default paths
CGI_DIR="/var/www/cgi-bin"
WEB_USER="www-data"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root for installation
check_permissions() {
    if [[ $EUID -ne 0 ]] && [[ "$1" == "install" ]]; then
        print_error "Installation requires root privileges. Use sudo."
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating directories..."
    mkdir -p bin
    mkdir -p docs
    
    if [[ "$1" == "install" ]]; then
        if [[ ! -d "$CGI_DIR" ]]; then
            print_status "Creating CGI directory: $CGI_DIR"
            mkdir -p "$CGI_DIR"
        fi
    fi
}

# Compile programs
compile() {
    print_status "Compiling CGI programs..."
    make clean
    make all
    
    if [[ $? -eq 0 ]]; then
        print_status "Compilation successful!"
    else
        print_error "Compilation failed!"
        exit 1
    fi
}

# Install to web server
install_cgi() {
    print_status "Installing CGI programs to $CGI_DIR..."
    
    cp bin/hello "$CGI_DIR/"
    cp bin/form_handler "$CGI_DIR/"
    
    chmod +x "$CGI_DIR/hello"
    chmod +x "$CGI_DIR/form_handler"
    
    # Set ownership to web server user
    if id "$WEB_USER" &>/dev/null; then
        chown "$WEB_USER:$WEB_USER" "$CGI_DIR/hello" "$CGI_DIR/form_handler"
        print_status "Set ownership to $WEB_USER"
    else
        print_warning "User $WEB_USER not found. Skipping ownership change."
    fi
    
    print_status "Installation complete!"
    print_status "Access your CGI programs at:"
    print_status "  http://your-server/cgi-bin/hello"
    print_status "  http://your-server/cgi-bin/form_handler"
}

# Test programs locally
test_programs() {
    print_status "Testing CGI programs..."
    make test
    print_status "Test files created in /tmp/"
}

# Main installation function
main() {
    case "$1" in
        "compile")
            create_directories
            compile
            ;;
        "install")
            check_permissions "$1"
            create_directories "$1"
            compile
            install_cgi
            ;;
        "test")
            create_directories
            compile
            test_programs
            ;;
        "clean")
            make clean
            print_status "Cleaned build files"
            ;;
        *)
            echo "Usage: $0 {compile|install|test|clean}"
            echo ""
            echo "  compile  - Compile the CGI programs only"
            echo "  install  - Compile and install to web server (requires sudo)"
            echo "  test     - Compile and test programs locally"
            echo "  clean    - Clean build files"
            exit 1
            ;;
    esac
}

main "$@"
