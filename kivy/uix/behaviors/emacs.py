# -*- encoding: utf-8 -*-
'''
Emacs Behavior
==============

.. versionadded:: 1.9.2

This `mixin <https://en.wikipedia.org/wiki/Mixin>`_ allows you to add
`Emacs <https://www.gnu.org/software/emacs/>`_ keyboard shortcuts for basic
movement and editing to the :class:`~kivy.uix.textinput.TextInput` widget.
The shortcuts currently available are listed below::

Emacs shortcuts
---------------
=============== ========================================================
   Shortcut     Description
--------------- --------------------------------------------------------
Control + a     Move cursor to the beginning of the line
Control + e     Move cursor to the end of the line
Control + f     Move cursor one character to the right
Control + b     Move cursor one character to the left
Alt + f         Move cursor to the end of the word to the right
Alt + b         Move cursor to the start of the word to the left
Alt + Backspace Delete text left of the cursor to the beginning of word
Alt + d         Delete text right of the cursor to the end of the word
Alt + w         Copy selection
Control + w     Cut selection
Control + y     Paste selection
=============== ========================================================

.. warning::
    If you have the :mod:`~kivy.modules.inspector` module enabled, the
    shortcut for opening the inspector (Control + e) conflicts with the
    Emacs shortcut to move to the end of the line (it will still move the
    cursor to the end of the line, but the inspector will open as well).
'''

__all__ = ('EmacsBehavior', )


class EmacsBehavior(object):
    '''
    A `mixin <https://en.wikipedia.org/wiki/Mixin>`_ that enables Emacs-style
    keyboard shortcuts for the :class:`~kivy.uix.textinput.TextInput` widget.
    '''

    def __init__(self, **kwargs):
        super(EmacsBehavior, self).__init__(**kwargs)

        self.bindings = {
            'ctrl': {
                'a': lambda: self.do_cursor_movement('cursor_home'),
                'e': lambda: self.do_cursor_movement('cursor_end'),
                'f': lambda: self.do_cursor_movement('cursor_right'),
                'b': lambda: self.do_cursor_movement('cursor_left'),
                'w': lambda: self._cut(self.selection_text),
                'y': self.paste,
            },
            'alt': {
                'w': self.copy,
                'f': lambda: self.do_cursor_movement('cursor_right',
                                                     control=True),
                'b': lambda: self.do_cursor_movement('cursor_left',
                                                     control=True),
                'd': self.delete_word_right,
                '\x08': self.delete_word_left,  # alt + backspace
            },
        }

    def keyboard_on_key_down(self, window, keycode, text, modifiers):

        key, key_str = keycode
        mod = modifiers[0] if modifiers else None
        is_emacs_shortcut = False

        if key in range(256):
            is_emacs_shortcut = ((mod == 'ctrl' and
                                  chr(key) in self.bindings['ctrl'].keys()) or
                                 (mod == 'alt' and
                                  chr(key) in self.bindings['alt'].keys()))
        if is_emacs_shortcut:
            emacs_shortcut = self.bindings[mod][chr(key)]  # Look up mod and key
            emacs_shortcut()
        else:
            super(EmacsBehavior, self).keyboard_on_key_down(window, keycode,
                                                            text, modifiers)

    def delete_word_right(self):
        '''Delete text right of the cursor to the end of the word'''
        start_index = self.cursor_index()
        start_cursor = self.cursor
        self.do_cursor_movement('cursor_right', control=True)
        end_index = self.cursor_index()
        if start_index != end_index:
            self.text = self.text[:start_index] + self.text[end_index:]
            self._set_cursor(pos=start_cursor)

    def delete_word_left(self):
        '''Delete text left of the cursor to the beginning of word'''
        start_index = self.cursor_index()
        self.do_cursor_movement('cursor_left', control=True)
        end_cursor = self.cursor
        end_index = self.cursor_index()
        if start_index != end_index:
            self.text = self.text[:end_index] + self.text[start_index:]
            self._set_cursor(pos=end_cursor)