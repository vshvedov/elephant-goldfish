"""Disposable Git evidence for offline checks and opt-in native smoke tests."""
from pathlib import Path
import subprocess


def git(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True).stdout


def make_repo(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    git(root, 'init', '-q', '-b', 'trunk')
    git(root, 'config', 'user.name', 'Fixture')
    git(root, 'config', 'user.email', 'fixture@example.invalid')
    (root / 'access.py').write_text('def allowed(role):\n    return role == "admin"\n')
    git(root, 'add', 'access.py')
    git(root, 'commit', '-qm', 'Initial fixture')
    (root / 'access.py').write_text('def allowed(role):\n    return role != "admin"\n')
    git(root, 'add', 'access.py')
    (root / 'access.py').write_text('def allowed(role):\n    return role == "admin"\n')
    (root / 'currency ü.py').write_text('def cents(dollars):\n    """Convert dollars to whole cents."""\n    return int(dollars)\n')
    return root


def source_snapshot(root):
    """Exclude only host-installed skills and flow scratch from this fixture check."""
    return {
        'head': git(root, 'rev-parse', 'HEAD'),
        'index': git(root, 'ls-files', '--stage', '-z'),
        'access': (root / 'access.py').read_bytes(),
        'currency': (root / 'currency ü.py').read_bytes(),
    }
