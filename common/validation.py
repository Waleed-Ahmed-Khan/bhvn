import streamlit as st
import re 

class pwdValidator:
    def __init__(self, **kwargs):
        self.pwd = kwargs.pop('pwd', None) 
    def check_digits(self) -> bool:
        return bool(re.search(r'[0-9]', str(self.pwd)))
    def check_uppercase(self) -> bool:
        return bool(re.search(r'[A-Z]', str(self.pwd)))
    def check_lowercase(self) -> bool:
        return bool(re.search(r'[a-z]', str(self.pwd)))
    def check_special_char(self) -> bool:

        return bool(re.search(r'''[~!@#$%-^&*?+`=|/()\;_:,<>.}{]''', str(self.pwd)))
    def check_whitespace(self) -> bool:
        return bool(re.search(r'\s', str(self.pwd)))
    def check_length(self) -> bool:
        return True if 8 <= len(self.pwd) else False

    def validate_pwd(self) -> bool:
        if all([self.check_digits(),
                self.check_uppercase(),
                self.check_lowercase(),
                self.check_special_char(),
                not self.check_whitespace(),
                self.check_length()]):
            return True
        else:
            st.error(" Your password has not met the following requirent(s) 👇 ")

            if not self.check_digits():
                st.warning(" -  Password must have at least one digit (0-9)")
            if not self.check_uppercase():
                st.warning(" -  Password must have at least one upper-case letter (A-Z)")
            if not self.check_lowercase():
                st.warning(" - Password must have at least one lower-case letter (a-z)")
            if not self.check_special_char():
                st.warning(""" - Password must have at least one special charactor (~!@#$%^&*?+`_-][=|/()\;_:,<>.}{)""")
            if self.check_whitespace():
                st.warning(" - Password must NOT contain white-space characters")
            if not self.check_length():
                st.warning(" - Password length must be at least 8 characters")
