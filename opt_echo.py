import streamlit as st
import traceback


class opt_echo:
    """Replacement for st.echo that includes a checkbox saying "show code".
    Usage
    -----
    >>> with opt_echo():
    ...     a = 1337
    """
    def __init__(self):
        self.checkbox = st.checkbox("show code")

        # This is a mega-hack!
        # And it's also not thread-safe. Don't use this if you have threaded
        # code that depends on traceback.extract_stack
        self.orig_extract_stack = traceback.extract_stack

        if self.checkbox:
            traceback.extract_stack = lambda: self.orig_extract_stack()[:-2]
            self.echo = st.echo()

    def __enter__(self):
        if self.checkbox:
            return self.echo.__enter__()

    def __exit__(self, type, value, traceback):
        if self.checkbox:
            self.echo.__exit__(type, value, traceback)

        # For some reason need to import this again.
        import traceback

        traceback.extract_stack = self.orig_extract_stack