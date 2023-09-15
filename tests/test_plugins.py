
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

from corpusaige.registry import PluginRegistry


home_directory = Path.home()
print(home_directory)

plugin_path = Path(__file__).parent / "assets/plugins/"

@pytest.fixture(scope="session")
def plugin_registry():

    PluginRegistry.register_plugins_from_dir(plugin_path)
    return PluginRegistry
   
def test_plugin(plugin_registry):
    plugins = plugin_registry.get_plugins() 
    assert len(plugins) == 2
    
    assert plugins["First plugin"].name == "First plugin"
    
    assert plugins["Another, better, plugin"].name == "Another, better, plugin"
    
    info = plugin_registry.get_plugin_info("First plugin")
    assert info.name == "First plugin"
    
    assert info.instance.DemoClass().get_name() == "Demo class"
    
    

def test_plugin_items(plugin_registry):

    item = plugin_registry.get_plugin_item("First plugin", "DemoClass")
    assert item().get_name() == "Demo class"
    
    item = plugin_registry.get_plugin_item("First plugin", "PrivateClass")      
    assert item is None
    item = plugin_registry.get_plugin_item("Second plugin", "DemoClass") 
    assert item is None
                            
    item = plugin_registry.get_plugin_item("Another, better, plugin", "public_function") 
    assert item() == "public function"
    
