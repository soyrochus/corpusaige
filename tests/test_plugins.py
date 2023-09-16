
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpusaige is a Python tool (and utility library) enabling AI-powered systems analysis 
through deep exploration and understanding of comprehensive document sets and source code.
@copyright: Copyright © 2023 Iwan van der Kleijn
@license: MIT
"""

# Import necessary modules


from pathlib import Path

import pytest

from corpusaige.registry import ServiceRegistry


home_directory = Path.home()
print(home_directory)

plugin_path = Path(__file__).parent / "assets/plugins/"

@pytest.fixture(scope="session")
def service_registry():

    ServiceRegistry.register_plugins_from_dir(plugin_path)
    return ServiceRegistry
   
def test_plugin(service_registry):
    plugins = service_registry.get_services() 
    
    assert plugins["First plugin"].name == "First plugin"
    
    assert plugins["Another, better, plugin"].name == "Another, better, plugin"
    
    info = service_registry.get_service_info("First plugin")
    assert info.type == "plugin"
    assert info.name == "First plugin"
    
    assert info.instance.DemoClass().get_name() == "Demo class"
    
    

def test_plugin_items(service_registry):

    item = service_registry.get_service_item("First plugin", "DemoClass")
    assert item().get_name() == "Demo class"
    
    item = service_registry.get_service_item("First plugin", "PrivateClass")      
    assert item is None
    item = service_registry.get_service_item("Second plugin", "DemoClass") 
    assert item is None
                            
    item = service_registry.get_service_item("Another, better, plugin", "public_function") 
    assert item() == "public function"
    
