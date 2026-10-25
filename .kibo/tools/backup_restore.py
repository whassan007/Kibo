"""Verified SQLite backups. Stop all database users before backup/restore for a
cross-database consistent recovery point. Restore uses atomic file replacement
and verified rollback on exceptions (not a multi-file power-loss transaction).

CLI: backup_restore.py backup BUNDLE DB [DB ...]
     backup_restore.py verify BUNDLE
     backup_restore.py restore BUNDLE TARGET_DIRECTORY
Bundles are immutable directories; manifests are deterministic, without timestamps.
SHA-256 detects corruption, not malicious replacement of both data and manifest.
"""
from contextlib import closing
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile


def digest(path):
    with open(path, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def check_sqlite(path):
    with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro&immutable=1', uri=True)) as conn:
        if conn.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
            raise ValueError(f'SQLite integrity check failed: {path.name}')


def verify(bundle):
    bundle = Path(bundle)
    manifest = json.loads((bundle / 'manifest.json').read_text())
    entries = manifest.get('databases')
    if manifest.get('version') != 1 or not isinstance(entries, dict) or not entries:
        raise ValueError('Invalid manifest')
    for name, metadata in sorted(entries.items()):
        if Path(name).name != name or name in {'.', '..', 'manifest.json'}:
            raise ValueError('Unsafe database name')
        path = bundle / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f'Missing or unsafe database: {name}')
        if metadata != {'sha256': digest(path), 'size': path.stat().st_size}:
            raise ValueError(f'SHA-256 verification failed: {name}')
        check_sqlite(path)
    if {p.name for p in bundle.iterdir()} != set(entries) | {'manifest.json'}:
        raise ValueError('Unexpected bundle contents')
    return manifest


def backup(databases, bundle):
    bundle = Path(bundle).absolute()
    sources = sorted(map(Path, databases), key=lambda p: p.name)
    if not sources or len({p.name for p in sources}) != len(sources):
        raise ValueError('Supply databases with unique filenames')
    if bundle.exists():
        raise FileExistsError(bundle)
    bundle.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.kibo-backup-', dir=bundle.parent) as tmp:
        stage = Path(tmp) / 'bundle'
        stage.mkdir(mode=0o700)
        entries = {}
        for source in sources:
            if source.name == 'manifest.json' or not source.is_file():
                raise ValueError(f'Invalid database: {source}')
            dest = stage / source.name
            with closing(sqlite3.connect(source.resolve().as_uri() + '?mode=ro', uri=True)) as src:
                with closing(sqlite3.connect(dest)) as dst:
                    src.backup(dst)
                    dst.execute('PRAGMA journal_mode=DELETE')
            entries[source.name] = {'sha256': digest(dest), 'size': dest.stat().st_size}
        (stage / 'manifest.json').write_text(json.dumps(
            {'version': 1, 'databases': entries}, sort_keys=True, indent=2) + '\n')
        verify(stage)
        os.rename(stage, bundle)
    return verify(bundle)


def restore(bundle, target):
    """Restore into an offline directory; reject WAL/journal files before mutation.

    Each replacement is atomic. On any exception all replaced files are rolled
    back and their hashes verified. Retain rollback files if rollback itself fails.
    """
    bundle, target = Path(bundle).resolve(), Path(target).resolve()
    manifest = verify(bundle)
    if target == bundle or bundle.is_relative_to(target):
        raise ValueError('Restore target must not contain the backup bundle')
    target.mkdir(parents=True, exist_ok=True)
    names = sorted(manifest['databases'])
    for name in names:
        dest = target / name
        if dest.is_symlink() or (dest.exists() and not dest.is_file()):
            raise ValueError(f'Unsafe target: {name}')
        if any(Path(str(dest) + suffix).exists() for suffix in ('-wal', '-shm', '-journal')):
            raise ValueError(f'Stop database users and checkpoint first: {name}')
    work = Path(tempfile.mkdtemp(prefix='.kibo-restore-', dir=target))
    (work / "previous").mkdir()
    previous, replaced = {}, []
    cleanup = True
    try:
        for name in names:
            dest = target / name
            previous[name] = digest(dest) if dest.exists() else None
            if dest.exists():
                shutil.copy2(dest, work / 'previous' / name)
            shutil.copyfile(bundle / name, work / name)
            if digest(work / name) != manifest['databases'][name]['sha256']:
                raise ValueError('Staged snapshot verification failed')
        for name in names:
            os.replace(work / name, target / name)
            replaced.append(name)
        for name in names:
            if digest(target / name) != manifest['databases'][name]['sha256']:
                raise ValueError('Restored snapshot verification failed')
            check_sqlite(target / name)
    except BaseException:
        try:
            for name in reversed(replaced):
                if previous[name] is None:
                    (target / name).unlink()
                else:
                    os.replace(work / 'previous' / name, target / name)
            for name in replaced:
                actual = digest(target / name) if (target / name).exists() else None
                if actual != previous[name]:
                    raise RuntimeError(f'Rollback verification failed: {name}')
        except BaseException as error:
            cleanup = False
            raise RuntimeError(f'Rollback failed; recovery files retained at {work}') from error
        raise
    finally:
        if cleanup:
            shutil.rmtree(work)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    create = commands.add_parser('backup')
    create.add_argument('bundle')
    create.add_argument('databases', nargs='+')
    validate = commands.add_parser('verify')
    validate.add_argument('bundle')
    recover = commands.add_parser('restore')
    recover.add_argument('bundle')
    recover.add_argument('target')
    args = parser.parse_args()
    if args.command == 'backup':
        result = backup(args.databases, args.bundle)
    elif args.command == 'restore':
        result = restore(args.bundle, args.target)
    else:
        result = verify(args.bundle)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
