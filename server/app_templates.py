"""
Application Templates and Presets for Application Share
Provides pre-configured application setups and templates
"""

import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

class AppTemplateManager:
    def __init__(self):
        self.templates_dir = os.getenv("TEMPLATES_DIR", "templates")
        self.presets_dir = os.getenv("PRESETS_DIR", "presets")
        
        # Create directories
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.presets_dir, exist_ok=True)
        
        # Initialize default templates
        self._create_default_templates()
    
    def _create_default_templates(self):
        """Create default application templates"""
        default_templates = {
            "development": {
                "name": "Development Environment",
                "description": "Complete development setup with IDE, terminal, and tools",
                "icon": "💻",
                "category": "development",
                "applications": [
                    {
                        "name": "code",
                        "display_name": "VS Code",
                        "args": ["--new-window"],
                        "env": {"DISPLAY": ":99"}
                    },
                    {
                        "name": "gnome-terminal",
                        "display_name": "Terminal",
                        "args": ["--maximize"],
                        "env": {"DISPLAY": ":99"}
                    },
                    {
                        "name": "firefox",
                        "display_name": "Firefox",
                        "args": ["--new-window"],
                        "env": {"DISPLAY": ":99"}
                    }
                ],
                "layout": {
                    "type": "tiled",
                    "windows": [
                        {"app": "code", "position": {"x": 0, "y": 0, "width": 0.6, "height": 1.0}},
                        {"app": "gnome-terminal", "position": {"x": 0.6, "y": 0, "width": 0.4, "height": 0.5}},
                        {"app": "firefox", "position": {"x": 0.6, "y": 0.5, "width": 0.4, "height": 0.5}}
                    ]
                },
                "settings": {
                    "auto_start": True,
                    "persistent": True,
                    "shared": True
                }
            },
            "office": {
                "name": "Office Suite",
                "description": "Complete office productivity suite",
                "icon": "📊",
                "category": "productivity",
                "applications": [
                    {
                        "name": "libreoffice",
                        "display_name": "LibreOffice Writer",
                        "args": ["--writer"],
                        "env": {"DISPLAY": ":99"}
                    },
                    {
                        "name": "libreoffice",
                        "display_name": "LibreOffice Calc",
                        "args": ["--calc"],
                        "env": {"DISPLAY": ":99"}
                    },
                    {
                        "name": "libreoffice",
                        "display_name": "LibreOffice Impress",
                        "args": ["--impress"],
                        "env": {"DISPLAY": ":99"}
                    }
                ],
                "layout": {
                    "type": "cascade",
                    "windows": [
                        {"app": "libreoffice", "position": {"x": 0.1, "y": 0.1, "width": 0.8, "height": 0.8}}
                    ]
                },
                "settings": {
                    "auto_start": False,
                    "persistent": False,
                    "shared": True
                }
            },
            "multimedia": {
                "name": "Multimedia Studio",
                "description": "Audio, video, and image editing suite",
                "icon": "🎬",
                "category": "multimedia",
                "applications": [
                    {
                        "name": "gimp",
                        "display_name": "GIMP",
                        "args": [],
                        "env": {"DISPLAY": ":99"}
                    },
                    {
                        "name": "vlc",
                        "display_name": "VLC Media Player",
                        "args": [],
                        "env": {"DISPLAY": ":99"}
                    },
                    {
                        "name": "audacity",
                        "display_name": "Audacity",
                        "args": [],
                        "env": {"DISPLAY": ":99"}
                    }
                ],
                "layout": {
                    "type": "tiled",
                    "windows": [
                        {"app": "gimp", "position": {"x": 0, "y": 0, "width": 0.5, "height": 1.0}},
                        {"app": "vlc", "position": {"x": 0.5, "y": 0, "width": 0.5, "height": 0.5}},
                        {"app": "audacity", "position": {"x": 0.5, "y": 0.5, "width": 0.5, "height": 0.5}}
                    ]
                },
                "settings": {
                    "auto_start": False,
                    "persistent": True,
                    "shared": False
                }
            },
            "gaming": {
                "name": "Gaming Setup",
                "description": "Gaming environment with Steam and emulators",
                "icon": "🎮",
                "category": "gaming",
                "applications": [
                    {
                        "name": "steam",
                        "display_name": "Steam",
                        "args": [],
                        "env": {"DISPLAY": ":99"}
                    },
                    {
                        "name": "lutris",
                        "display_name": "Lutris",
                        "args": [],
                        "env": {"DISPLAY": ":99"}
                    }
                ],
                "layout": {
                    "type": "fullscreen",
                    "windows": [
                        {"app": "steam", "position": {"x": 0, "y": 0, "width": 1.0, "height": 1.0}}
                    ]
                },
                "settings": {
                    "auto_start": False,
                    "persistent": False,
                    "shared": False
                }
            }
        }
        
        # Save default templates
        for template_id, template in default_templates.items():
            self.save_template(template_id, template)
    
    def save_template(self, template_id: str, template: Dict[str, Any]) -> bool:
        """Save a template"""
        try:
            template_path = os.path.join(self.templates_dir, f"{template_id}.json")
            with open(template_path, 'w') as f:
                json.dump(template, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving template {template_id}: {e}")
            return False
    
    def load_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Load a template"""
        try:
            template_path = os.path.join(self.templates_dir, f"{template_id}.json")
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading template {template_id}: {e}")
            return None
    
    def list_templates(self, category: str = None) -> List[Dict[str, Any]]:
        """List available templates"""
        try:
            templates = []
            for filename in os.listdir(self.templates_dir):
                if filename.endswith('.json'):
                    template_id = filename[:-5]
                    template = self.load_template(template_id)
                    if template and (not category or template.get('category') == category):
                        templates.append({
                            "id": template_id,
                            "name": template.get('name', template_id),
                            "description": template.get('description', ''),
                            "icon": template.get('icon', '📱'),
                            "category": template.get('category', 'other'),
                            "app_count": len(template.get('applications', []))
                        })
            return templates
        except Exception as e:
            print(f"Error listing templates: {e}")
            return []
    
    def create_preset(self, preset_id: str, template_id: str, customizations: Dict[str, Any]) -> bool:
        """Create a preset from a template with customizations"""
        try:
            template = self.load_template(template_id)
            if not template:
                return False
            
            # Apply customizations
            preset = template.copy()
            preset.update(customizations)
            preset['template_id'] = template_id
            preset['created_at'] = time.time()
            
            preset_path = os.path.join(self.presets_dir, f"{preset_id}.json")
            with open(preset_path, 'w') as f:
                json.dump(preset, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error creating preset {preset_id}: {e}")
            return False
    
    def load_preset(self, preset_id: str) -> Optional[Dict[str, Any]]:
        """Load a preset"""
        try:
            preset_path = os.path.join(self.presets_dir, f"{preset_id}.json")
            if os.path.exists(preset_path):
                with open(preset_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading preset {preset_id}: {e}")
            return None
    
    def list_presets(self) -> List[Dict[str, Any]]:
        """List available presets"""
        try:
            presets = []
            for filename in os.listdir(self.presets_dir):
                if filename.endswith('.json'):
                    preset_id = filename[:-5]
                    preset = self.load_preset(preset_id)
                    if preset:
                        presets.append({
                            "id": preset_id,
                            "name": preset.get('name', preset_id),
                            "description": preset.get('description', ''),
                            "icon": preset.get('icon', '📱'),
                            "template_id": preset.get('template_id'),
                            "created_at": preset.get('created_at', 0)
                        })
            return presets
        except Exception as e:
            print(f"Error listing presets: {e}")
            return []
    
    def get_categories(self) -> List[str]:
        """Get available categories"""
        try:
            categories = set()
            for template in self.list_templates():
                if template.get('category'):
                    categories.add(template['category'])
            return sorted(list(categories))
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        try:
            template_path = os.path.join(self.templates_dir, f"{template_id}.json")
            if os.path.exists(template_path):
                os.remove(template_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting template {template_id}: {e}")
            return False
    
    def delete_preset(self, preset_id: str) -> bool:
        """Delete a preset"""
        try:
            preset_path = os.path.join(self.presets_dir, f"{preset_id}.json")
            if os.path.exists(preset_path):
                os.remove(preset_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting preset {preset_id}: {e}")
            return False
