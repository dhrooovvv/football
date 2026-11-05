"""Whitelist extraction of competition bundles, with local-only provenance."""
from pathlib import Path, PurePosixPath
import hashlib
import io
import json
import stat
import zipfile


def destination(info):
    p = PurePosixPath(info.filename)
    if p.is_absolute() or '..' in p.parts or '\\' in info.filename or stat.S_ISLNK(info.external_attr >> 16):
        raise ValueError('Unsafe archive member')
    if info.is_dir() or '__MACOSX' in p.parts or p.name.startswith('._'):
        return None
    for source in ('tactical', 'broadcast'):
        prefix = 'BAR-ATH_' + source
        if p.name in {prefix + s for s in ('_atd.txt', '_atd.xml', '_homography.csv', '_smart_tagging.xml')}:
            return Path(source) / p.name
        if p.name in (prefix + '.mp4', prefix + '-002.mp4'):
            return Path(source) / (prefix + '.mp4')
    return None


def extract_bundle(archive, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    records, seen = [], set()
    def unpack(z, parent, depth=0):
        if depth > 1:
            raise ValueError('Unexpected archive nesting')
        for info in z.infolist():
            target = destination(info)  # validate all members before considering type
            if '__MACOSX' in PurePosixPath(info.filename).parts or info.is_dir():
                continue
            if info.filename.endswith('.zip'):
                if info.file_size > 512 * 1024**2:
                    raise ValueError('Nested archive exceeds declared budget')
                with zipfile.ZipFile(io.BytesIO(z.read(info))) as nested:
                    unpack(nested, parent + [info.filename], depth + 1)
                continue
            if target is None:
                continue
            if target in seen:
                raise ValueError('Duplicate archive destination')
            seen.add(target)
            dest = output / target
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                raise FileExistsError('Refusing to overwrite extracted assets')
            temporary = dest.with_suffix(dest.suffix + '.partial')
            if temporary.exists():
                raise FileExistsError('Unresolved partial extraction')
            digest = hashlib.sha256()
            try:
                with z.open(info) as src, temporary.open('xb') as dst:
                    while chunk := src.read(8 * 1024**2):
                        dst.write(chunk)
                        digest.update(chunk)
                temporary.rename(dest)
            except BaseException:
                temporary.unlink(missing_ok=True)
                raise
            records.append(dict(source=parent + [info.filename], destination=str(target), bytes=info.file_size, sha256=digest.hexdigest()))
    with zipfile.ZipFile(archive) as outer:
        unpack(outer, [str(archive)])
    (output / 'manifest.json').write_text(json.dumps(records, indent=2))
    return records
