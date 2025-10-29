import re

class PrePro:
    @staticmethod
    def filter(code: str) -> str:
        return re.sub(r"//[^\n]*", "", code)
