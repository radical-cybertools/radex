import os

project = "RaDex"
author = "RaDex Contributors"

extensions = [
    "breathe",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"

# Default path can be overridden via:
# sphinx-build -Dbreathe_projects.raddex=/path/to/doxygen/xml
breathe_projects = {
    "raddex": os.path.abspath("_build/doxygen/xml"),
}
breathe_default_project = "raddex"
