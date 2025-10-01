#!/bin/bash

# Package Checker and Installer for Application Share
# Checks for missing packages and provides installation instructions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_package() {
    echo -e "${PURPLE}[PACKAGE]${NC} $1"
}

# Function to detect Linux distribution
detect_distribution() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO_ID=$ID
        DISTRO_VERSION=$VERSION_ID
        DISTRO_NAME=$NAME
    elif [ -f /etc/arch-release ]; then
        DISTRO_ID="arch"
        DISTRO_VERSION="rolling"
        DISTRO_NAME="Arch Linux"
    elif [ -f /etc/debian_version ]; then
        DISTRO_ID="debian"
        DISTRO_VERSION=$(cat /etc/debian_version)
        DISTRO_NAME="Debian"
    else
        DISTRO_ID="unknown"
        DISTRO_VERSION="unknown"
        DISTRO_NAME="Unknown"
    fi
    
    print_status "Detected: $DISTRO_NAME ($DISTRO_ID $DISTRO_VERSION)"
}

# Function to check if package is available
check_package_available() {
    local package=$1
    local distro=$2
    
    case $distro in
        "arch"|"archlinux")
            pacman -Si "$package" &>/dev/null
            ;;
        "debian"|"ubuntu")
            apt-cache show "$package" &>/dev/null
            ;;
        "alpine")
            apk search -q "$package" &>/dev/null
            ;;
        *)
            return 1
            ;;
    esac
}

# Function to check if package is installed
check_package_installed() {
    local package=$1
    local distro=$2
    
    case $distro in
        "arch"|"archlinux")
            pacman -Q "$package" &>/dev/null
            ;;
        "debian"|"ubuntu")
            dpkg -l "$package" &>/dev/null
            ;;
        "alpine")
            apk info -e "$package" &>/dev/null
            ;;
        *)
            return 1
            ;;
    esac
}

# Function to get installation command
get_install_command() {
    local package=$1
    local distro=$2
    
    case $distro in
        "arch"|"archlinux")
            echo "sudo pacman -S $package"
            ;;
        "debian"|"ubuntu")
            echo "sudo apt-get install $package"
            ;;
        "alpine")
            echo "sudo apk add $package"
            ;;
        *)
            echo "Unknown distribution"
            ;;
    esac
}

# Function to check critical packages
check_critical_packages() {
    local distro=$1
    local missing_packages=()
    
    print_status "Checking critical packages..."
    
    # Critical packages that must be available
    local critical_packages=("python3" "docker" "git" "curl" "wget")
    
    for package in "${critical_packages[@]}"; do
        if check_package_installed "$package" "$distro"; then
            print_success "$package is installed"
        elif check_package_available "$package" "$distro"; then
            print_warning "$package is available but not installed"
            missing_packages+=("$package")
        else
            print_error "$package is not available"
            missing_packages+=("$package")
        fi
    done
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        print_error "Missing critical packages: ${missing_packages[*]}"
        return 1
    fi
    
    print_success "All critical packages are available"
    return 0
}

# Function to check audio system conflicts
check_audio_conflicts() {
    local distro=$1
    
    if [ "$distro" = "arch" ] || [ "$distro" = "archlinux" ]; then
        print_status "Checking for audio system conflicts..."
        
        local conflicts=()
        
        # Check if both PulseAudio and PipeWire are installed
        if pacman -Q pulseaudio &>/dev/null && pacman -Q pipewire &>/dev/null; then
            conflicts+=("PulseAudio and PipeWire both installed")
        fi
        
        # Check for conflicting packages
        if pacman -Q pulseaudio-alsa &>/dev/null && pacman -Q pipewire-alsa &>/dev/null; then
            conflicts+=("PulseAudio-ALSA and PipeWire-ALSA both installed")
        fi
        
        if [ ${#conflicts[@]} -gt 0 ]; then
            print_error "Audio conflicts detected:"
            for conflict in "${conflicts[@]}"; do
                echo "  - $conflict"
            done
            echo ""
            print_status "Resolution commands:"
            echo "  ./fix-audio-conflicts.sh --pipewire    # Switch to PipeWire (recommended)"
            echo "  ./fix-audio-conflicts.sh --pulseaudio  # Switch to PulseAudio"
            echo "  ./fix-audio-conflicts.sh --auto        # Auto-resolve conflicts"
            return 1
        else
            print_success "No audio conflicts detected"
            return 0
        fi
    fi
}

# Function to check optional packages
check_optional_packages() {
    local distro=$1
    local missing_packages=()
    local alternative_packages=()
    
    print_status "Checking optional packages..."
    
    # Optional packages with alternatives
    declare -A package_alternatives
    package_alternatives["xvfb"]="xorg-server-xvfb xvfb-run"
    package_alternatives["xrdp"]="freerdp freerdp2-x11"
    package_alternatives["neofetch"]="fastfetch"
    
    for package in "${!package_alternatives[@]}"; do
        local found=false
        local alternatives=(${package_alternatives[$package]})
        
        # Check main package
        if check_package_installed "$package" "$distro"; then
            print_success "$package is installed"
            found=true
        elif check_package_available "$package" "$distro"; then
            print_warning "$package is available but not installed"
            missing_packages+=("$package")
            found=true
        else
            # Check alternatives
            for alt in "${alternatives[@]}"; do
                if check_package_installed "$alt" "$distro"; then
                    print_success "$alt (alternative to $package) is installed"
                    found=true
                    break
                elif check_package_available "$alt" "$distro"; then
                    print_warning "$alt (alternative to $package) is available but not installed"
                    alternative_packages+=("$alt")
                    found=true
                    break
                fi
            done
        fi
        
        if [ "$found" = false ]; then
            print_error "$package and its alternatives are not available"
        fi
    done
    
    # Print installation commands
    if [ ${#missing_packages[@]} -gt 0 ] || [ ${#alternative_packages[@]} -gt 0 ]; then
        echo ""
        print_status "Installation commands:"
        
        for package in "${missing_packages[@]}"; do
            echo "  $(get_install_command "$package" "$distro")"
        done
        
        for package in "${alternative_packages[@]}"; do
            echo "  $(get_install_command "$package" "$distro")"
        done
    fi
}

# Function to install missing packages
install_missing_packages() {
    local distro=$1
    local auto_install=${2:-false}
    
    print_status "Installing missing packages..."
    
    # Update package database
    case $distro in
        "arch"|"archlinux")
            sudo pacman -Syu --noconfirm
            ;;
        "debian"|"ubuntu")
            sudo apt-get update
            ;;
        "alpine")
            sudo apk update
            ;;
    esac
    
    # Install critical packages
    local critical_packages=("python3" "docker" "git" "curl" "wget")
    
    for package in "${critical_packages[@]}"; do
        if ! check_package_installed "$package" "$distro"; then
            if check_package_available "$package" "$distro"; then
                print_package "Installing $package..."
                case $distro in
                    "arch"|"archlinux")
                        sudo pacman -S --noconfirm "$package"
                        ;;
                    "debian"|"ubuntu")
                        sudo apt-get install -y "$package"
                        ;;
                    "alpine")
                        sudo apk add --no-cache "$package"
                        ;;
                esac
                print_success "$package installed successfully"
            else
                print_error "Cannot install $package - not available"
            fi
        fi
    done
    
    # Install optional packages with fallbacks
    if [ "$auto_install" = "true" ]; then
        print_status "Installing optional packages with fallbacks..."
        
        # xvfb
        if ! check_package_installed "xvfb" "$distro"; then
            if check_package_available "xorg-server-xvfb" "$distro"; then
                print_package "Installing xorg-server-xvfb..."
                case $distro in
                    "arch"|"archlinux")
                        sudo pacman -S --noconfirm xorg-server-xvfb
                        ;;
                    "debian"|"ubuntu")
                        sudo apt-get install -y xorg-server-xvfb
                        ;;
                    "alpine")
                        sudo apk add --no-cache xorg-server-xvfb
                        ;;
                esac
            elif check_package_available "xvfb" "$distro"; then
                print_package "Installing xvfb..."
                case $distro in
                    "arch"|"archlinux")
                        sudo pacman -S --noconfirm xvfb
                        ;;
                    "debian"|"ubuntu")
                        sudo apt-get install -y xvfb
                        ;;
                    "alpine")
                        sudo apk add --no-cache xvfb
                        ;;
                esac
            else
                print_warning "xvfb not available, will use xvfb-run from x11-utils"
            fi
        fi
        
        # xrdp
        if ! check_package_installed "xrdp" "$distro"; then
            if check_package_available "xrdp" "$distro"; then
                print_package "Installing xrdp..."
                case $distro in
                    "arch"|"archlinux")
                        sudo pacman -S --noconfirm xrdp
                        ;;
                    "debian"|"ubuntu")
                        sudo apt-get install -y xrdp
                        ;;
                    "alpine")
                        sudo apk add --no-cache xrdp
                        ;;
                esac
            elif check_package_available "freerdp" "$distro"; then
                print_package "Installing freerdp..."
                case $distro in
                    "arch"|"archlinux")
                        sudo pacman -S --noconfirm freerdp
                        ;;
                    "debian"|"ubuntu")
                        sudo apt-get install -y freerdp
                        ;;
                    "alpine")
                        sudo apk add --no-cache freerdp
                        ;;
                esac
            else
                print_warning "xrdp not available, RDP functionality will be limited"
            fi
        fi
        
        # neofetch
        if ! check_package_installed "neofetch" "$distro"; then
            if check_package_available "neofetch" "$distro"; then
                print_package "Installing neofetch..."
                case $distro in
                    "arch"|"archlinux")
                        sudo pacman -S --noconfirm neofetch
                        ;;
                    "debian"|"ubuntu")
                        sudo apt-get install -y neofetch
                        ;;
                    "alpine")
                        sudo apk add --no-cache neofetch
                        ;;
                esac
            elif check_package_available "fastfetch" "$distro"; then
                print_package "Installing fastfetch..."
                case $distro in
                    "arch"|"archlinux")
                        sudo pacman -S --noconfirm fastfetch
                        ;;
                    "debian"|"ubuntu")
                        sudo apt-get install -y fastfetch
                        ;;
                    "alpine")
                        sudo apk add --no-cache fastfetch
                        ;;
                esac
            else
                print_warning "neofetch not available, using basic system info"
            fi
        fi
    fi
}

# Function to show help
show_help() {
    echo "Package Checker and Installer for Application Share"
    echo "==================================================="
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --check-only     Only check packages, don't install"
    echo "  --auto-install   Automatically install missing packages"
    echo "  --help           Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 --check-only     # Check packages without installing"
    echo "  $0 --auto-install   # Check and install missing packages"
    echo "  $0                  # Interactive mode"
}

# Main function
main() {
    local check_only=false
    local auto_install=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --check-only)
                check_only=true
                shift
                ;;
            --auto-install)
                auto_install=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    echo -e "${BLUE}🔍 Package Checker for Application Share${NC}"
    echo "=============================================="
    echo ""
    
    # Detect distribution
    detect_distribution
    
    # Check critical packages
    if ! check_critical_packages "$DISTRO_ID"; then
        print_error "Critical packages are missing. Please install them first."
        exit 1
    fi
    
    # Check audio conflicts (Arch Linux only)
    check_audio_conflicts "$DISTRO_ID"
    
    # Check optional packages
    check_optional_packages "$DISTRO_ID"
    
    # Install missing packages if requested
    if [ "$check_only" = false ]; then
        if [ "$auto_install" = true ]; then
            install_missing_packages "$DISTRO_ID" true
        else
            echo ""
            read -p "Do you want to install missing packages? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                install_missing_packages "$DISTRO_ID" true
            fi
        fi
    fi
    
    print_success "Package check complete!"
}

# Run main function
main "$@"
