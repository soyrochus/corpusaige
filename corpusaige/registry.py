#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

import importlib
from pathlib import Path
import types

from typing import Any, List, Protocol, Type, Dict, Optional
from pathlib import Path

class ServiceInfo:
    def __init__(self, name: str, path: Path, type: str, exported_items: List[str], instance: Type = None):
        self.name = name
        self.path = path
        self.type = type
        self.exported_items = exported_items
        self.instance = instance

    def __repr__(self):
        return f"<ServiceInfo(name={self.name}, path={str(self.path)}, type={self.type}, exported_items={self.exported_items})>"

class ServiceRegistry(Protocol):
    """Service registry for providers and plugins."""
    _services: Dict[str, ServiceInfo] = {}
    
    
    @classmethod
    def register_provider(cls, module: types.ModuleType) -> None:
        """Register a provider module."""
        if hasattr(module, "_name"):
            info = ServiceInfo(module._name, None, "provider", module._exported_items, module)
            cls._services[module._name] = info
        else:
            raise ValueError(f"Module {module} has no _name attribute")
        
    @classmethod
    def register_plugins(cls, paths: List[Path]) -> None:
        
            
        for path in paths:
            try:
                # Dynamic import of the module (assuming it's a python file)
                module_name = path.stem
                spec = importlib.util.spec_from_file_location(module_name, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Register the plugin (may fail on module without _name attribute, etc)
                info = ServiceInfo(module._name, path, "plugin", module._exported_items, module)
            
                cls._services[module._name] = info 
            except Exception as e:
                print(f"Error while registering plugin {path}: {e}")

    @classmethod
    def register_plugins_from_dir(cls, dir: Path) -> None:
        python_files = [f for f in dir.iterdir() if f.is_file() and f.suffix == '.py']
        cls.register_plugins(python_files)

    
    @classmethod
    def get_service_info(cls, plugin_name: str) -> ServiceInfo:
        return cls._services.get(plugin_name, None)
       
        
    @classmethod
    def get_service_instance(cls, plugin_name: str) -> Any:
        info = cls.get_service_info(plugin_name)
        if info is not None:
            return info.instance
        else:     
            return None

    @classmethod
    def get_services(cls) -> Dict[str, ServiceInfo]:
        return cls._services
    
    
    @classmethod
    def get_service_item(cls, plugin_name: str, item_name: str) -> Any:
        info = cls.get_service_info(plugin_name)
        if info is not None:
            if item_name in info.exported_items:
                return getattr(info.instance, item_name, None)

        return None
    
# Usage example

