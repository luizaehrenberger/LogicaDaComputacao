import re

class PrePro:
    @staticmethod
    def filter(code: str) -> str:
        # Remove comentários //... preservando \n
        return re.sub(r"//[^\n]*", "", code)
