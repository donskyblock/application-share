#!/bin/bash

# Audio System Conflict Resolver for Application Share
# Resolves PulseAudio/PipeWire conflicts on Arch Linux

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

print_audio() {
    echo -e "${PURPLE}[AUDIO]${NC} $1"
}

# Function to detect audio system
detect_audio_system() {
    print_status "Detecting current audio system..."
    
    if pacman -Q pipewire &>/dev/null; then
        AUDIO_SYSTEM="pipewire"
        print_audio "PipeWire detected"
    elif pacman -Q pulseaudio &>/dev/null; then
        AUDIO_SYSTEM="pulseaudio"
        print_audio "PulseAudio detected"
    else
        AUDIO_SYSTEM="none"
        print_warning "No audio system detected"
    fi
}

# Function to check for conflicts
check_conflicts() {
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
        return 1
    else
        print_success "No audio conflicts detected"
        return 0
    fi
}

# Function to resolve conflicts by choosing PipeWire
resolve_conflicts_pipewire() {
    print_status "Resolving conflicts by switching to PipeWire..."
    
    # Remove PulseAudio packages
    print_audio "Removing PulseAudio packages..."
    sudo pacman -Rns --noconfirm pulseaudio pulseaudio-alsa pulseaudio-bluetooth pulseaudio-equalizer pulseaudio-jack pulseaudio-lirc pulseaudio-zeroconf 2>/dev/null || true
    
    # Install PipeWire packages
    print_audio "Installing PipeWire packages..."
    sudo pacman -S --noconfirm pipewire pipewire-pulse pipewire-alsa pipewire-jack pipewire-zeroconf
    
    # Enable PipeWire services
    print_audio "Enabling PipeWire services..."
    sudo systemctl --user enable pipewire pipewire-pulse pipewire-media-session
    
    print_success "Switched to PipeWire successfully"
}

# Function to resolve conflicts by choosing PulseAudio
resolve_conflicts_pulseaudio() {
    print_status "Resolving conflicts by switching to PulseAudio..."
    
    # Remove PipeWire packages
    print_audio "Removing PipeWire packages..."
    sudo pacman -Rns --noconfirm pipewire pipewire-pulse pipewire-alsa pipewire-jack pipewire-zeroconf pipewire-media-session 2>/dev/null || true
    
    # Install PulseAudio packages
    print_audio "Installing PulseAudio packages..."
    sudo pacman -S --noconfirm pulseaudio pulseaudio-alsa pulseaudio-bluetooth
    
    # Enable PulseAudio service
    print_audio "Enabling PulseAudio service..."
    sudo systemctl --user enable pulseaudio
    
    print_success "Switched to PulseAudio successfully"
}

# Function to install recommended audio system
install_recommended_audio() {
    print_status "Installing recommended audio system (PipeWire)..."
    
    # Install PipeWire
    print_audio "Installing PipeWire audio system..."
    sudo pacman -S --noconfirm pipewire pipewire-pulse pipewire-alsa pipewire-jack pipewire-zeroconf pipewire-media-session
    
    # Enable services
    print_audio "Enabling audio services..."
    sudo systemctl --user enable pipewire pipewire-pulse pipewire-media-session
    
    print_success "PipeWire installed and configured"
}

# Function to test audio system
test_audio() {
    print_status "Testing audio system..."
    
    if command -v pactl &>/dev/null; then
        print_audio "Testing with PulseAudio tools..."
        if pactl info &>/dev/null; then
            print_success "Audio system is working"
            return 0
        else
            print_warning "Audio system test failed"
            return 1
        fi
    elif command -v pw-cli &>/dev/null; then
        print_audio "Testing with PipeWire tools..."
        if pw-cli info &>/dev/null; then
            print_success "Audio system is working"
            return 0
        else
            print_warning "Audio system test failed"
            return 1
        fi
    else
        print_warning "No audio tools available for testing"
        return 1
    fi
}

# Function to show audio status
show_audio_status() {
    print_status "Current audio system status:"
    echo ""
    
    if pacman -Q pipewire &>/dev/null; then
        print_audio "PipeWire: Installed"
        if systemctl --user is-active pipewire &>/dev/null; then
            print_success "  Status: Active"
        else
            print_warning "  Status: Inactive"
        fi
    else
        print_warning "PipeWire: Not installed"
    fi
    
    if pacman -Q pulseaudio &>/dev/null; then
        print_audio "PulseAudio: Installed"
        if systemctl --user is-active pulseaudio &>/dev/null; then
            print_success "  Status: Active"
        else
            print_warning "  Status: Inactive"
        fi
    else
        print_warning "PulseAudio: Not installed"
    fi
    
    echo ""
    print_status "Available audio devices:"
    if command -v pactl &>/dev/null; then
        pactl list short sinks 2>/dev/null || print_warning "No audio sinks found"
    elif command -v pw-cli &>/dev/null; then
        pw-cli list-objects | grep -i sink || print_warning "No audio sinks found"
    else
        print_warning "No audio tools available"
    fi
}

# Function to show help
show_help() {
    echo "Audio System Conflict Resolver for Application Share"
    echo "===================================================="
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --pipewire       Switch to PipeWire (recommended)"
    echo "  --pulseaudio     Switch to PulseAudio"
    echo "  --auto           Automatically resolve conflicts"
    echo "  --test           Test current audio system"
    echo "  --status         Show current audio status"
    echo "  --help           Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 --pipewire    # Switch to PipeWire"
    echo "  $0 --auto        # Auto-resolve conflicts"
    echo "  $0 --test        # Test audio system"
    echo "  $0 --status      # Show audio status"
}

# Main function
main() {
    local action=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --pipewire)
                action="pipewire"
                shift
                ;;
            --pulseaudio)
                action="pulseaudio"
                shift
                ;;
            --auto)
                action="auto"
                shift
                ;;
            --test)
                action="test"
                shift
                ;;
            --status)
                action="status"
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
    
    echo -e "${BLUE}🔊 Audio System Conflict Resolver${NC}"
    echo "====================================="
    echo ""
    
    # Detect current audio system
    detect_audio_system
    
    case $action in
        "pipewire")
            resolve_conflicts_pipewire
            test_audio
            ;;
        "pulseaudio")
            resolve_conflicts_pulseaudio
            test_audio
            ;;
        "auto")
            if check_conflicts; then
                print_success "No conflicts to resolve"
            else
                print_status "Auto-resolving conflicts..."
                resolve_conflicts_pipewire
                test_audio
            fi
            ;;
        "test")
            test_audio
            ;;
        "status")
            show_audio_status
            ;;
        "")
            # Interactive mode
            if check_conflicts; then
                print_success "No conflicts detected"
                show_audio_status
            else
                echo ""
                echo "Choose resolution method:"
                echo "1) Switch to PipeWire (recommended)"
                echo "2) Switch to PulseAudio"
                echo "3) Show current status"
                echo "4) Exit"
                echo ""
                read -p "Enter your choice (1-4): " choice
                
                case $choice in
                    1)
                        resolve_conflicts_pipewire
                        test_audio
                        ;;
                    2)
                        resolve_conflicts_pulseaudio
                        test_audio
                        ;;
                    3)
                        show_audio_status
                        ;;
                    4)
                        echo "Exiting..."
                        exit 0
                        ;;
                    *)
                        print_error "Invalid choice"
                        exit 1
                        ;;
                esac
            fi
            ;;
    esac
    
    print_success "Audio conflict resolution complete!"
}

# Run main function
main "$@"
