import hashlib
import importlib.util
from pathlib import Path
import sqlite3

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('backup_restore', ROOT / '.kibo/tools/backup_restore.py')
br = importlib.util.module_from_spec(spec)
spec.loader.exec_module(br)


def test_compose_security():
    text = (ROOT / 'docker-compose.yml').read_text()
    services = yaml.safe_load(text)['services']
    assert 'kibo_enterprise_secret' not in text
    assert services['postgres']['environment']['POSTGRES_PASSWORD'] == '${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set}'
    for service, port in [('postgres', 5432), ('redis', 6379)]:
        assert services[service]['ports'] == [f'127.0.0.1:{port}:{port}']
    env = services['kibo-api']['environment']
    assert env['KIBO_STRICT_AUTH'] == '1'
    assert '${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set}' in env['DATABASE_URL']
    for key in ('KIBO_JWT_SECRET', 'KIBO_JWT_ISSUER'):
        assert env[key] == '${' + key + ':?' + key + ' must be set}'


def test_nonroot_container():
    text = (ROOT / 'Dockerfile').read_text()
    instructions = [line.strip() for line in text.splitlines()]
    assert [line for line in instructions if line.startswith('USER ')] == ['USER kibo']
    assert '--uid 10001' in text
    assert 'chown -R kibo:kibo /app' in text
    assert instructions.index('USER kibo') < next(i for i, line in enumerate(instructions) if line.startswith('CMD ['))


def make_db(path, value):
    with sqlite3.connect(path) as conn:
        conn.execute('CREATE TABLE records (id INTEGER PRIMARY KEY, value BLOB)')
        conn.execute('INSERT INTO records VALUES (1, ?)', (value,))


def test_backup_restore_roundtrip(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    paths = [source / name for name in ('kibo_state.db', 'regulatory_intelligence.db')]
    for path in paths:
        make_db(path, b'complete\x00data\xff')
    bundle = tmp_path / 'backup'
    manifest = br.backup(paths, bundle)
    second = tmp_path / 'second'
    assert br.backup(reversed(paths), second) == manifest
    assert (bundle / 'manifest.json').read_bytes() == (second / 'manifest.json').read_bytes()
    assert br.verify(bundle) == manifest
    for name, metadata in manifest['databases'].items():
        assert hashlib.sha256((bundle / name).read_bytes()).hexdigest() == metadata['sha256']
    restored = tmp_path / 'restored'
    br.restore(bundle, restored)
    for path in paths:
        assert (restored / path.name).read_bytes() == (bundle / path.name).read_bytes()
        with sqlite3.connect(restored / path.name) as conn:
            assert conn.execute('SELECT * FROM records').fetchall() == [(1, b'complete\x00data\xff')]
    original = (restored / paths[0].name).read_bytes()
    with (bundle / paths[0].name).open('ab') as stream:
        stream.write(b'corruption')
    with pytest.raises(ValueError, match='SHA-256'):
        br.restore(bundle, restored)
    assert (restored / paths[0].name).read_bytes() == original


def test_failed_restore_rolls_back(tmp_path, monkeypatch):
    source, target = tmp_path / 'source', tmp_path / 'target'
    source.mkdir()
    target.mkdir()
    for name in ('kibo_state.db', 'regulatory_intelligence.db'):
        make_db(source / name, 'new')
        make_db(target / name, 'old')
    br.backup(list(source.iterdir()), tmp_path / 'backup')
    before = {p.name: p.read_bytes() for p in target.iterdir()}
    replace = br.os.replace
    calls = []

    def fail_second(src, dst):
        calls.append(str(dst))
        if len(calls) == 2:
            raise OSError('injected replacement failure')
        return replace(src, dst)

    monkeypatch.setattr(br.os, 'replace', fail_second)
    with pytest.raises(OSError, match='injected'):
        br.restore(tmp_path / 'backup', target)
    assert {p.name: p.read_bytes() for p in target.iterdir()} == before


def test_wal_snapshot_and_unsafe_manifest(tmp_path):
    path = tmp_path / 'state.db'
    with sqlite3.connect(path) as conn:
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('CREATE TABLE data (value)')
        conn.execute("INSERT INTO data VALUES ('committed WAL')")
        conn.commit()
        br.backup([path], tmp_path / 'backup')
        with sqlite3.connect(tmp_path / 'backup/state.db') as snapshot:
            assert snapshot.execute('SELECT * FROM data').fetchall() == [('committed WAL',)]
        offline = tmp_path / 'offline'
        offline.mkdir()
        (offline / 'state.db-wal').touch()
        with pytest.raises(ValueError, match='checkpoint'):
            br.restore(tmp_path / 'backup', tmp_path / 'offline')
    manifest = tmp_path / 'backup/manifest.json'
    manifest.write_text('{"version": 1, "databases": {"../escape.db": {}}}')
    with pytest.raises(ValueError, match='Unsafe'):
        br.verify(tmp_path / 'backup')
