# src/storage.py
from whitenoise.storage import CompressedManifestStaticFilesStorage

class CustomStaticFilesStorage(CompressedManifestStaticFilesStorage):
    patterns = (
        (
            "*.css",
            (
                r"""(url\(['"]{0,1}\s*(?P<url>.*?)["']{0,1}\))""",
            ),
        ),
    )