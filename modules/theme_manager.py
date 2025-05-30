# theme_manager.py

import customtkinter as ctk

class ThemeManager:
    _theme = "dark"
    _listeners = []

    @classmethod
    def set_theme(cls, theme: str):
        theme = theme.lower()
        if theme not in ("light", "dark"):
            raise ValueError("Theme must be 'light' or 'dark'")
        cls._theme = theme
        ctk.set_appearance_mode(theme)
        for listener in cls._listeners:
            listener(theme)

    @classmethod
    def get_theme(cls):
        return cls._theme.lower()

    @classmethod
    def register(cls, callback):
        """Register a callback: callback(theme: str)"""
        if callback not in cls._listeners:
            cls._listeners.append(callback)

    @classmethod
    def unregister(cls, callback):
        if callback in cls._listeners:
            cls._listeners.remove(callback)
