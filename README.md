# Atlas Glyphs 3 Palette Plugin

Atlas is a Glyphs 3 palette plugin that displays the currently selected glyph as a reference, for all languages and symbols. This is primarily to help facilitate with multilingual type design but works for all glyphs. It supports both light and dark modes.

## Features

- Shows a preview of the currently selected glyph in the palette.
- Works in both light and dark mode in Glyphs 3.

## Installation

### 1. Download

Clone or download this repository:

```sh
git clone https://github.com/yourusername/Atlas.glyphsPalette.git
```

### 2. Install

Copy or symlink the plugin bundle to your Glyphs 3 Plugins folder:

```sh
cp -R Atlas.glyphsPalette ~/Library/Application\ Support/Glyphs\ 3/Plugins/
```

Or, if you want to symlink for development:

```sh
ln -s /path/to/your/Atlas.glyphsPalette ~/Library/Application\ Support/Glyphs\ 3/Plugins/Atlas.glyphsPalette
```

### 3. Restart Glyphs

- Quit and reopen Glyphs 3.
- The "Atlas" palette should appear under `Window → Palette → Atlas`.

## Troubleshooting

- If the palette does not appear, check the Macro Panel for errors.
- Ensure the plugin bundle structure is preserved:

```
Atlas.glyphsPalette/
  Contents/
    Info.plist
    MacOS/
      plugin
    Resources/
      plugin.py
      IBdialog.xib
      IBdialog.nib/
        keyedobjects.nib
        keyedobjects-101300.nib
```

## License

Copyright © 2026 Brindle

See [Contents/Info.plist](Contents/Info.plist) for details.
