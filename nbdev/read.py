# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_read.ipynb.

# %% auto 0
__all__ = ['create_output', 'show_src', 'nbdev_create_config', 'get_config', 'config_key', 'add_init', 'write_cells',
           'basic_export_nb']

# %% ../nbs/01_read.ipynb 2
from datetime import datetime
from fastcore.imports import *
from fastcore.foundation import *
from fastcore.basics import *
from fastcore.imports import *
from fastcore.meta import *
from fastcore.script import *
from fastcore.xdg import *
from fastcore.xtras import *

import ast,functools
from IPython.display import Markdown
from configparser import ConfigParser
from execnb.nbio import read_nb,NbCell
from pprint import pformat,pprint

# %% ../nbs/01_read.ipynb 5
def create_output(txt, mime):
    "Add a cell output containing `txt` of the `mime` text MIME sub-type"
    return [{"data": { f"text/{mime}": str(txt).splitlines(True) },
             "execution_count": 1, "metadata": {}, "output_type": "execute_result"}]

# %% ../nbs/01_read.ipynb 6
def show_src(src, lang='python'): return Markdown(f'```{lang}\n{src}\n```')

# %% ../nbs/01_read.ipynb 10
_nbdev_home_dir = 'nbdev' # sub-directory of xdg base dir
_nbdev_config_name = 'settings.ini'

# %% ../nbs/01_read.ipynb 11
def apply_defaults(
    cfg,
    lib_name:str=None, # Package name, defaults to local repo folder name
    branch='master', # Repo default branch
    git_url='https://github.com/%(user)s/%(lib_name)s', # Repo URL
    custom_sidebar:bool_arg=False, # Create custom sidebar?
    nbs_path='.', # Path to notebooks
    lib_path='%(lib_name)s', # Path to package root
    doc_path='_docs', # Path to rendered docs
    tst_flags='', # Test flags
    version='0.0.1', # Version of this release
    doc_host='https://%(user)s.github.io',  # Hostname for docs
    doc_baseurl='/%(lib_name)s',  # Base URL for docs
    keywords='nbdev jupyter notebook python', # Package keywords
    license='apache2', # License for the package
    copyright:str=None, # Copyright for the package, defaults to '`current_year` onwards, `author`'
    status='3', # Development status PyPI classifier
    min_python='3.7', # Minimum Python version PyPI classifier
    audience='Developers', # Intended audience PyPI classifier
    language='English', # Language PyPI classifier
    recursive:bool_arg=False, # Include subfolders in notebook globs?
    black_formatting:bool_arg=False, # Format libraries with black?
    readme_nb='index.ipynb', # Notebook to export as repo readme
    title='%(lib_name)s', # Quarto website title
    allowed_metadata_keys='', # Preserve the list of keys in the main notebook metadata
    allowed_cell_metadata_keys='', # Preserve the list of keys in cell level metadata
    jupyter_hooks=True, # Run Jupyter hooks?
    clean_ids=True, # Remove ids from plaintext reprs?
):
    "Apply default settings where missing in `cfg`"
    if lib_name is None:
        _parent = Path.cwd().parent
        lib_name = _parent.parent.name if _parent.name=='nbs' else _parent.name
    if copyright is None and hasattr(cfg,'author'): copyright = f"{datetime.now().year} ownwards, {cfg.author}"
    for k,v in locals().items():
        if not (k.startswith('_') or k=='cfg' or k in cfg): cfg[k] = v
    return cfg

# %% ../nbs/01_read.ipynb 12
@call_parse
@delegates(apply_defaults, but='cfg')
def nbdev_create_config(
    user:str, # Repo username
    author:str, # Package author's name
    author_email:str, # Package author's email address
    description:str, # Short summary of the package
    path:str='.', # Path to create config file
    cfg_name:str=_nbdev_config_name, # Name of config file to create
    **kwargs
):
    "Create a config file"
    d = {k:v for k,v in locals().items() if k not in ('path','cfg_name')}
    cfg = Config(path, cfg_name, d, save=False)
    cfg = apply_defaults(cfg, **kwargs)
    cfg.save()

# %% ../nbs/01_read.ipynb 14
def _nbdev_config_file(cfg_name=_nbdev_config_name, path=None):
    cfg_path = path = Path.cwd() if path is None else Path(path)
    while cfg_path != cfg_path.parent and not (cfg_path/cfg_name).exists(): cfg_path = cfg_path.parent
    if not (cfg_path/cfg_name).exists(): cfg_path = path
    return cfg_path/cfg_name

# %% ../nbs/01_read.ipynb 16
def _xdg_config_paths(cfg_name=_nbdev_config_name):
    xdg_config_paths = reversed([xdg_config_home()]+xdg_config_dirs())
    return [o/_nbdev_home_dir/cfg_name for o in xdg_config_paths]

# %% ../nbs/01_read.ipynb 17
@functools.lru_cache(maxsize=None)
def get_config(cfg_name=_nbdev_config_name, path=None):
    "`Config` for ini file found in `path` (defaults to `cwd`)"
    cfg_file = _nbdev_config_file(cfg_name, path)
    extra_files = _xdg_config_paths(cfg_name)
    cfg = Config(cfg_file.parent, cfg_file.name, extra_files=extra_files)
    return apply_defaults(cfg)

# %% ../nbs/01_read.ipynb 21
def config_key(c, default=None, path=True, missing_ok=None):
    "Look for key `c` in settings.ini and fail gracefully if not found and no default provided"
    if missing_ok is not None:
        warn("`missing_ok` is no longer used. Don't pass it to `config_key` to silence this warning.")
    cfg = get_config()
    res = cfg.path(c, default) if path else cfg.get(c, default)
    if res is None: raise ValueError(f'`{c}` not specified in {_nbdev_config_name}')
    return res

# %% ../nbs/01_read.ipynb 24
_init = '__init__.py'

def _has_py(fs): return any(1 for f in fs if f.endswith('.py'))

def add_init(path):
    "Add `__init__.py` in all subdirs of `path` containing python files if it's not there already"
    # we add the lowest-level `__init__.py` files first, which ensures _has_py succeeds for parent modules
    path = Path(path)
    path.mkdir(exist_ok=True)
    if not (path/_init).exists(): (path/_init).touch()
    for r,ds,fs in os.walk(path, topdown=False):
        r = Path(r)
        subds = (os.listdir(r/d) for d in ds)
        if _has_py(fs) or any(filter(_has_py, subds)) and not (r/_init).exists(): (r/_init).touch()

# %% ../nbs/01_read.ipynb 28
def write_cells(cells, hdr, file, offset=0):
    "Write `cells` to `file` along with header `hdr` starting at index `offset` (mainly for nbdev internal use)"
    for cell in cells:
        if cell.source.strip(): file.write(f'\n\n{hdr} {cell.idx_+offset}\n{cell.source}')

# %% ../nbs/01_read.ipynb 29
def basic_export_nb(fname, name, dest=None):
    "Basic exporter to bootstrap nbdev"
    if dest is None: dest = config_key('lib_path')
    fname,dest = Path(fname),Path(dest)
    nb = read_nb(fname)

    # grab the source from all the cells that have an `export` comment
    cells = L(cell for cell in nb.cells if re.match(r'#\s*\|export', cell.source))

    # find all the exported functions, to create `__all__`:
    trees = cells.map(NbCell.parsed_).concat()
    funcs = trees.filter(risinstance((ast.FunctionDef,ast.ClassDef))).attrgot('name')
    exp_funcs = [f for f in funcs if f[0]!='_']

    # write out the file
    with (dest/name).open('w') as f:
        f.write(f"# %% auto 0\n__all__ = {exp_funcs}")
        write_cells(cells, f"# %% {fname.relpath(dest)}", f)
        f.write('\n')
