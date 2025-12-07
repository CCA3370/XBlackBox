# XBlackBox XDR Viewer - Theme and Internationalization Guide

## Overview

The XBlackBox XDR Viewer now supports multiple themes and languages, allowing users to customize their experience based on preferences and accessibility needs.

## Features

### 🎨 Theme System

The viewer includes three professionally designed themes:

#### 1. **Dark Theme** (Default)
- **Primary Color**: Teal (#0d7377)
- **Background**: Dark gray (#1e1e1e)
- **Best for**: General use, reduced eye strain in low-light environments
- **Characteristics**: Modern, vibrant colors with excellent contrast

#### 2. **Light Theme**
- **Primary Color**: Teal (#0d7377)
- **Background**: Light gray (#f5f5f5)
- **Best for**: Bright environments, printing, presentations
- **Characteristics**: Clean, professional appearance with high readability

#### 3. **High Contrast Theme**
- **Primary Color**: Cyan (#00ffff)
- **Background**: Pure black (#000000)
- **Best for**: Accessibility, visual impairments, maximum readability
- **Characteristics**: Maximum contrast with bold borders and large fonts

### 🌍 Internationalization (i18n)

Full multi-language support with comprehensive translations:

#### Supported Languages:
1. **English (en_US)** - Default
2. **中文 (zh_CN)** - Chinese Simplified

#### Auto-Detection:
- Automatically detects system language on first launch
- Falls back to English if system language is not supported

## How to Use

### Changing Themes

**Method 1: Menu Bar**
1. Click on "Theme" menu in the menu bar
2. Select your preferred theme:
   - Dark Theme
   - Light Theme
   - High Contrast

**Result:**
- UI immediately updates with new colors
- Plot colors automatically adjust
- Theme preference is saved for next session

### Changing Languages

**Method 1: Menu Bar**
1. Click on "Language" (or "语言") menu in the menu bar
2. Select your preferred language:
   - Follow System (auto-detect)
   - English
   - 中文 (Chinese)

**Result:**
- A dialog will prompt you to restart the application
- After restart, all UI elements will be in the selected language
- Language preference is saved for next session

**Note:** Language changes require an application restart to fully apply.

## What Gets Translated

All UI elements are fully translated, including:

### Menus
- File, View, Analysis, Theme, Language, Help
- All menu items and actions
- Keyboard shortcuts descriptions

### UI Components
- Window title
- Button labels
- Tab names
- Dialog titles and messages
- Tooltips
- Status bar messages

### Data Labels
- Plot axis labels
- Statistical analysis headers
- Table column headers
- File information labels

## Technical Details

### File Structure

```
XBlackBox/
├── xdr_viewer.py      # Main application (updated)
├── themes.py          # Theme system (NEW)
├── translations.py    # Translation system (NEW)
└── demo_themes.py     # Demo script (NEW)
```

### Theme Architecture

Each theme defines:
- **Color palette**: Primary, background, surface, border, text colors
- **Qt stylesheet**: Complete CSS-like styling for all UI components
- **Plot colors**: 20 distinct colors for parameter plots
- **Plot style**: Matplotlib configuration for plots

### Translation Architecture

Translations are stored in a structured dictionary:
- **Key-based system**: Each UI string has a unique key
- **Language codes**: Standard ISO codes (en_US, zh_CN)
- **Fallback**: English is used if translation is missing
- **Helper functions**: `tr(key)` for easy translation access

### Persistence

User preferences are stored using Qt's QSettings:
- **Location**: System-specific (Registry on Windows, plist on macOS, conf on Linux)
- **Keys stored**:
  - `theme`: Current theme name ('dark', 'light', 'high_contrast')
  - `language`: Current language ('system', 'en_US', 'zh_CN')
  - Also stores: recent files, window geometry, etc.

## For Developers

### Adding a New Theme

1. Create a new theme class in `themes.py`:
```python
class MyTheme(Theme):
    def __init__(self):
        super().__init__("My Theme Name")
        self.colors = {
            'primary': '#color',
            'background': '#color',
            # ... other colors
        }
        self.plot_colors = ['#color1', '#color2', ...]
    
    def get_stylesheet(self) -> str:
        # Return Qt stylesheet string
        pass
    
    def get_plot_style(self) -> Dict:
        # Return matplotlib style dict
        pass
```

2. Add to THEMES dictionary:
```python
THEMES = {
    'dark': DarkTheme(),
    'light': LightTheme(),
    'high_contrast': HighContrastTheme(),
    'my_theme': MyTheme(),  # Add here
}
```

### Adding a New Language

1. Add translation dictionary in `translations.py`:
```python
TRANSLATIONS = {
    'en_US': { ... },
    'zh_CN': { ... },
    'fr_FR': {  # New language
        'window_title': 'XBlackBox XDR Viewer - Édition Moderne',
        'menu_file': '&Fichier',
        # ... all translation keys
    }
}
```

2. Update language menu in `xdr_viewer.py`:
```python
lang_french_action = QAction('Français', self)
lang_french_action.triggered.connect(partial(self.change_language, 'fr_FR'))
language_menu.addAction(lang_french_action)
```

### Using Translations in Code

```python
from translations import tr

# In any function or method:
label = QLabel(tr('file_info_title'))
button = QPushButton(tr('btn_update_plot'))
statusBar().showMessage(tr('status_ready'))
```

## Benefits

### User Experience
- **Personalization**: Choose appearance that suits your needs
- **Accessibility**: High contrast theme for better visibility
- **Localization**: Use interface in your native language
- **Consistency**: Themes apply uniformly across all UI elements

### Performance
- **No overhead**: Theme/language switching has negligible performance impact
- **Instant themes**: Theme changes apply immediately without restart
- **Efficient**: Translation lookup is dictionary-based (O(1) complexity)

### Maintainability
- **Centralized**: All styling in themes.py, all text in translations.py
- **Extensible**: Easy to add new themes and languages
- **Consistent**: Single source of truth for colors and text

## Comparison with Previous Version

### Before (v2.5)
- ❌ Single hardcoded dark theme
- ❌ English-only interface
- ❌ No customization options
- ❌ Limited accessibility

### After (v3.0)
- ✅ 3 professionally designed themes
- ✅ Full multi-language support (EN, CN)
- ✅ Easy theme/language switching
- ✅ Auto-detect system language
- ✅ Persistent user preferences
- ✅ Improved accessibility (high contrast)
- ✅ Better international reach

## Screenshots (Conceptual)

### Dark Theme
```
┌────────────────────────────────────────────┐
│ File View Analysis Theme Language Help    │ Dark Background
├────────────────────────────────────────────┤ Teal Accents
│ [UI Elements with dark colors]             │ Vibrant Plots
└────────────────────────────────────────────┘
```

### Light Theme
```
┌────────────────────────────────────────────┐
│ File View Analysis Theme Language Help    │ Light Background
├────────────────────────────────────────────┤ Teal Accents
│ [UI Elements with light colors]            │ Professional Look
└────────────────────────────────────────────┘
```

### High Contrast Theme
```
┌────────────────────────────────────────────┐
│ File View Analysis Theme Language Help    │ Black Background
├────────────────────────────────────────────┤ Cyan Accents
│ [UI Elements with maximum contrast]        │ Bold Borders
└────────────────────────────────────────────┘
```

### Chinese Interface
```
┌────────────────────────────────────────────┐
│ 文件 查看 分析 主题 语言 帮助              │ Chinese UI
├────────────────────────────────────────────┤ All text translated
│ [所有界面元素都是中文]                     │ Native experience
└────────────────────────────────────────────┘
```

## Future Enhancements

Potential future improvements:

1. **More Themes**:
   - Solarized Dark/Light
   - Nord Theme
   - Dracula Theme
   - Custom theme editor

2. **More Languages**:
   - Spanish (es_ES)
   - French (fr_FR)
   - German (de_DE)
   - Japanese (ja_JP)

3. **Advanced Features**:
   - Theme preview before applying
   - Export/import custom themes
   - Per-component theme customization
   - Dynamic theme based on time of day

4. **Accessibility**:
   - Screen reader support
   - Keyboard navigation improvements
   - Font size customization
   - Color blind friendly themes

## Troubleshooting

### Theme not changing
- **Solution**: Check if QSettings is writable. Try running as administrator (Windows) or with correct permissions.

### Language partially changed
- **Solution**: Restart the application. Language changes require a full restart.

### Translation missing
- **Solution**: File an issue on GitHub. The key will fall back to English automatically.

### Colors look wrong
- **Solution**: 
  - Calibrate your monitor
  - Try a different theme
  - Check color profile settings in your OS

## Support

For issues, questions, or feature requests:
- **GitHub Issues**: https://github.com/CCA3370/XBlackBox/issues
- **Discussions**: https://github.com/CCA3370/XBlackBox/discussions

## Version History

- **v3.0** (Current): Theme system and internationalization added
- **v2.5**: Modern UI with enhanced features
- **v2.0**: Advanced analysis capabilities
- **v1.0**: Initial release

---

**XBlackBox XDR Viewer v3.0**  
*Modern Edition with Theme and Language Support*  
© 2024 XBlackBox Project
