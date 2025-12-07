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
lang_names = {
    'en_US': 'English',
    'zh_CN': '中文 (Chinese)',
    'ja_JP': '日本語 (Japanese)',
    'es_ES': 'Español (Spanish)',
    'fr_FR': 'Français (French)',
}
for lang_code in TRANSLATIONS.keys():
    lang_name = lang_names.get(lang_code, lang_code)
    print(f"  • {lang_name}")
    print(f"    Window Title: {TRANSLATIONS[lang_code]['window_title']}")
    print(f"    Status Ready: {TRANSLATIONS[lang_code]['status_ready']}")
    print()

print("=" * 60)
print("Features:")
print("-" * 60)
print("  ✓ Multiple theme support (6 themes: Dark, Light, High Contrast, Blue, Solarized Dark, Nord)")
print("  ✓ Theme switching from menu bar")
print("  ✓ Multi-language support (5 languages: English, Chinese, Japanese, Spanish, French)")
print("  ✓ Language switching from menu bar")  
print("  ✓ Auto-detect system language")
print("  ✓ Persistent theme and language preferences")
print("  ✓ All UI text fully translated")
print("=" * 60)
