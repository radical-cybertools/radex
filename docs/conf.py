import os
from datetime import datetime

project = "RaDex"
author = "Hewlett Packard Enterprise and Rutgers University"
copyright = f"{datetime.now().year}"

extensions = [
    "breathe",
    "sphinx.ext.githubpages",
    "sphinxcontrib.mermaid",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_title = "RaDex"
html_logo = None

html_theme_options = {
    "collapse_navigation": False,
    "navigation_depth": 4,
    "style_external_links": True,
}

# Default path can be overridden via:
# sphinx-build -Dbreathe_projects.raddex=/path/to/doxygen/xml
breathe_projects = {
    "raddex": os.path.abspath("_build/doxygen/xml"),
}
breathe_default_project = "raddex"
