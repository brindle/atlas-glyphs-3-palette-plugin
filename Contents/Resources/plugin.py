# encoding: utf-8
from __future__ import division, print_function, unicode_literals

import os
from datetime import datetime

import objc
from GlyphsApp import Glyphs, GSEditViewController, UPDATEINTERFACE
from GlyphsApp.plugins import PalettePlugin


# ------------------------------------------------------------
# Atlas debug logging (prints to macro window if open)
# ------------------------------------------------------------
def macro_log(*parts):
	msg = " ".join([str(p) for p in parts])
	# Removed Glyphs.showMacroWindow() - logs visible when window opened manually
	print(msg)


macro_log("ATLAS LOADED:", __file__)
try:
	macro_log("ATLAS MTIME:", datetime.fromtimestamp(os.path.getmtime(__file__)))
except Exception as e:
	macro_log("ATLAS MTIME FAILED:", e)


class Atlas(PalettePlugin):

	dialog = objc.IBOutlet()
	textField = objc.IBOutlet()
	
	# Store current character for link handling
	current_char = None

	# ============================================================
	# USER CONFIGURABLE SETTINGS (edit here)
	# ============================================================
	# Default font size for glyph name and links (in points)
	DEFAULT_FONT_SIZE = 11.0
	# Independent size for character preview (in points)
	DEFAULT_CHAR_SIZE = 130.0
	# Character line height multiplier (0.8 = tight, 1.0 = normal, 1.2 = loose)
	DEFAULT_CHAR_LINEHEIGHT = 1.03
	# Fixed height of palette (in points)
	DEFAULT_PALETTE_HEIGHT = 1
	# ============================================================

	@objc.python_method
	def settings(self):
		macro_log("ATLAS settings() ENTER")
		try:
			self.name = Glyphs.localize({
				'en': 'Atlas',
				'de': 'Atlas',
				'fr': 'Atlas',
				'es': 'Atlas',
				'pt': 'Atlas',
			})
			macro_log("ATLAS settings() name set:", self.name)

			# Load .nib dialog (without .extension)
			macro_log("ATLAS settings() loadNib('IBdialog')...")
			self.loadNib('IBdialog', __file__)
			macro_log("ATLAS settings() loadNib OK. dialog:", self.dialog, "textField:", self.textField)

			# Configure text field: non-editable, selectable for links
			self.textField.setEditable_(False)
			self.textField.setSelectable_(True)
			
			# Set up click handler for opening links
			self.textField.setDelegate_(self)

			# Hook controller (required for some nib setups)
			try:
				self.dialog.setController_(self)
				macro_log("ATLAS settings() dialog.setController_ OK")
			except Exception as e:
				macro_log("ATLAS settings() dialog.setController_ FAILED:", e)

		except Exception as e:
			macro_log("ATLAS settings() FAILED:", e)
		finally:
			macro_log("ATLAS settings() EXIT")

	@objc.python_method
	def start(self):
		macro_log("ATLAS start() ENTER")
		try:
			# Adding a callback for the 'GSUpdateInterface' event
			Glyphs.addCallback(self.update, UPDATEINTERFACE)
			macro_log("ATLAS start() addCallback OK:", UPDATEINTERFACE)
		except Exception as e:
			macro_log("ATLAS start() FAILED:", e)
		finally:
			macro_log("ATLAS start() EXIT")

	@objc.python_method
	def __del__(self):
		macro_log("ATLAS __del__() ENTER")
		try:
			Glyphs.removeCallback(self.update)
			macro_log("ATLAS __del__() removeCallback OK")
		except Exception as e:
			macro_log("ATLAS __del__() removeCallback FAILED:", e)
		finally:
			macro_log("ATLAS __del__() EXIT")

	def minHeight(self):
		# Always allow small minimum for resizing
		macro_log("ATLAS minHeight() -> 50")
		return 50

	def maxHeight(self):
		# Return configured palette height as max
		height = self.getPaletteHeight()
		macro_log("ATLAS maxHeight() ->", height)
		return height

	@objc.python_method
	def getPaletteHeight(self):
		"""Get palette height from preferences, defaults to DEFAULT_PALETTE_HEIGHT"""
		try:
			height = Glyphs.defaults["com.atlas.paletteHeight"]
			if height and isinstance(height, (int, float)):
				return int(height)
		except Exception:
			pass
		return self.DEFAULT_PALETTE_HEIGHT

	@objc.python_method
	def update(self, sender):
		macro_log("ATLAS update() ENTER")

		try:
			currentTab = sender.object()
			macro_log("ATLAS update() currentTab:", currentTab)

			layers = getattr(currentTab, "selectedLayers", None)
			macro_log("ATLAS update() selectedLayers:", layers)

			if not layers:
				macro_log("ATLAS update() no layers, skipping")
				return

			layer = layers[0]
			glyph = getattr(layer, "parent", None)

			if glyph is None:
				macro_log("ATLAS update() no parent glyph")
				return
			name = getattr(glyph, "name", None)
			char = getattr(glyph, "string", None)

			macro_log("ATLAS update() name:", name)
			macro_log("ATLAS update() char:", char)
			
			# Store character for click handler
			self.current_char = char

			# Get font sizes from preferences
			font_size = self.getFontSize()
			char_size = self.getCharSize()
			char_lineheight = self.getCharLineHeight()

			from AppKit import NSMutableAttributedString, NSFontAttributeName, NSFont, NSParagraphStyle

			attr = NSMutableAttributedString.alloc().init()

			# --- Glyph name only (no label) [COMMENTED OUT FOR NOW]
			# if name:
			# 	start = attr.length()
			# 	attr.appendAttributedString_(
			# 		NSMutableAttributedString.alloc().initWithString_(name + "\n")
			# 	)
			# 	font = NSFont.systemFontOfSize_(font_size)
			# 	attr.addAttribute_value_range_(
			# 		NSFontAttributeName,
			# 		font,
			# 		(start, attr.length() - start),
			# 	)

			# --- Character preview (large, with line height control)
			if char:
				start = attr.length()
				attr.appendAttributedString_(
					NSMutableAttributedString.alloc().initWithString_(char)
				)
				
				# Set font size for character
				font = NSFont.systemFontOfSize_(char_size)
				attr.addAttribute_value_range_(
					NSFontAttributeName,
					font,
					(start, len(char)),
				)
				
				# Set paragraph style with line height control
				para_style = NSParagraphStyle.defaultParagraphStyle().mutableCopy()
				para_style.setLineHeightMultiple_(char_lineheight)
				para_style.setMinimumLineHeight_(char_size * char_lineheight)
				para_style.setMaximumLineHeight_(char_size * char_lineheight)
				attr.addAttribute_value_range_(
					"NSParagraphStyle",
					para_style,
					(start, len(char)),
				)			# Apply to field
			self.textField.setAttributedStringValue_(attr)

			macro_log("ATLAS update() wrote attributed text")

		except Exception as e:
			macro_log("ATLAS update() HARD FAIL:", e)

		macro_log("ATLAS update() EXIT")

	def mouseDown_(self, event):
		"""Handle mouse clicks on the palette to open Jisho link"""
		if self.current_char:
			from AppKit import NSWorkspace
			url = "https://jisho.org/search/%s" % self.current_char
			workspace = NSWorkspace.sharedWorkspace()
			from Foundation import NSURL
			ns_url = NSURL.URLWithString_(url)
			workspace.openURL_(ns_url)
			macro_log("ATLAS mouseDown: opened", url)

	@objc.python_method
	def getFontSize(self):
		"""Get default font size from preferences, defaults to DEFAULT_FONT_SIZE"""
		try:
			size = Glyphs.defaults["com.atlas.fontSize"]
			if size and isinstance(size, (int, float)):
				return float(size)
		except Exception:
			pass
		return self.DEFAULT_FONT_SIZE

	@objc.python_method
	def getCharSize(self):
		"""Get character preview size from preferences, defaults to DEFAULT_CHAR_SIZE"""
		try:
			size = Glyphs.defaults["com.atlas.charSize"]
			if size and isinstance(size, (int, float)):
				return float(size)
		except Exception:
			pass
		return self.DEFAULT_CHAR_SIZE

	@objc.python_method
	def getCharLineHeight(self):
		"""Get character line height multiplier from preferences, defaults to DEFAULT_CHAR_LINEHEIGHT"""
		try:
			lineheight = Glyphs.defaults["com.atlas.charLineHeight"]
			if lineheight and isinstance(lineheight, (int, float)):
				return float(lineheight)
		except Exception:
			pass
		return self.DEFAULT_CHAR_LINEHEIGHT

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__