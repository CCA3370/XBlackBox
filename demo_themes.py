#!/usr/bin/env python3
"""
Demo script to show available themes and translations
"""

from themes import get_theme_names, THEMES
from translations import TRANSLATIONS

print("=" * 60)
print("XBlackBox XDR Viewer - Theme and Translation System")
print("=" * 60)
print()

print("Available Themes:")
print("-" * 60)
for theme_name in get_theme_names():
    theme = THEMES[theme_name]
    print(f"  • {theme.name}")
    print(f"    Primary Color: {theme.colors['primary']}")
    print(f"    Background: {theme.colors['background']}")
    print(f"    Plot Colors: {len(theme.plot_colors)} colors available")
    print()

print("=" * 60)
print("Available Languages:")
print("-" * 60)
for lang_code in TRANSLATIONS.keys():
    if lang_code == 'en_US':
        print(f"  • English (en_US)")
    elif lang_code == 'zh_CN':
        print(f"  • 中文 (zh_CN)")
    print(f"    Window Title: {TRANSLATIONS[lang_code]['window_title']}")
    print(f"    Status Ready: {TRANSLATIONS[lang_code]['status_ready']}")
    print()

print("=" * 60)
print("Features:")
print("-" * 60)
print("  ✓ Multiple theme support (Dark, Light, High Contrast)")
print("  ✓ Theme switching from menu bar")
print("  ✓ Multi-language support (English, Chinese)")
print("  ✓ Language switching from menu bar")  
print("  ✓ Auto-detect system language")
print("  ✓ Persistent theme and language preferences")
print("  ✓ All UI text fully translated")
print("=" * 60)
