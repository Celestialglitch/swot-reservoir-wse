project = "swot-reservoir-wse"
author = "Ongkar Dasgupta"

extensions = [
    "myst_parser",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

master_doc = "index"

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

html_theme = "sphinx_rtd_theme"