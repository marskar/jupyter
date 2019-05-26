from pathlib import Path
from typing import List

import nbformat
import pytest

from nbless import nbless, nbuild, nbconv


def make_tempfiles(tmp_path: Path) -> List[Path]:
    """Helper function to create a list of pathlib Path objects."""
    md = tmp_path / "intro.md"
    py = tmp_path / "plot.py"
    txt = tmp_path / "discussion.txt"
    md.write_text("# Introduction\nHere's a plot made with the matplotlib.")
    py.write_text("import numpy as np\nimport matplotlib.pyplot as plt\n"
                  "N = 50\nx = y = colors = np.random.rand(N)\n"
                  "area = np.pi * (15 * np.random.rand(N)) ** 2\n"
                  "plt.scatter(x, y, s=area, c=colors, alpha=0.5)\nplt.show()"
                  )
    txt.write_text("Discussion\nMatplotlib is verbose, but makes cool plots!")
    return [md, py, txt]


def test_nbuild(tmp_path: Path) -> None:
    """Run nbuild() to create a temporary notebook file from 3 tempfiles."""
    for tempfile in make_tempfiles(tmp_path):
        assert nbuild([tempfile]).cells[0].source == tempfile.read_text()


def test_nbless(tmp_path: Path) -> None:
    """Run nbless() to create and execute a temporary notebook file."""
    for tempfile in make_tempfiles(tmp_path):
        assert nbless([tempfile]).cells[0].source == tempfile.read_text()


@pytest.mark.parametrize('not_exporters', ['htm', 'ipython', 'markup'])
def test_raises(not_exporters, tmp_path: Path) -> None:
    """Make sure a ValueError is raised if nbconv() gets a bad exporter."""
    p = tmp_path / "input.ipynb"
    nbformat.write(nbuild(make_tempfiles(tmp_path)), p.name)
    with pytest.raises(ValueError):
        nbconv(filename='input.ipynb', exporter=not_exporters)


@pytest.mark.parametrize('exporters', ['html', 'asciidoc', 'rst'])
def test_nbconv(exporters, tmp_path: Path) -> None:
    """Convert ``tempfiles`` with each exporter in ``exporters``."""
    p = tmp_path / "notebook.ipynb"
    nbformat.write(nbuild(make_tempfiles(tmp_path)), p.name)
    assert nbconv(filename=p, exporter=exporters)[0].endswith("." + exporters)
