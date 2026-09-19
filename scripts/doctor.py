#!/usr/bin/env python3
"""Read-only bootstrap inventory. Only CORE failures affect exit status."""
import importlib.metadata
import platform
import shlex
import shutil
import subprocess


def probe(argv):
    print('$ ' + shlex.join(argv), flush=True)
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=20)
        print('stdout:\n' + (result.stdout.rstrip() or '(empty)'))
        print('stderr:\n' + (result.stderr.rstrip() or '(empty)'))
        print(f'exit={result.returncode}')
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f'BROKEN: {error}')
        return False


def main():
    print(f'Host: {platform.platform()} / {platform.machine()}')
    groups = {
        'CORE': [('git', '--version'), ('python3', '--version'), ('make', '--version')],
        'GITHUB': [('gh', '--version')],
        'SIMULATION': [('verilator', '--version')],
        'FORMAL': [('yosys', '-V'), ('sby', '--version'), ('z3', '--version'),
                   ('boolector', '--version'), ('bitwuzla', '--version'),
                   ('yices', '--version'), ('yices-smt2', '--version'),
                   ('cvc5', '--version'), ('cvc4', '--version')],
        'IMPLEMENTATION': [('yosys', '-V'), ('nextpnr-ecp5', '--version'),
                           ('ecppack', '--version')],
    }
    failures = []
    for category, commands in groups.items():
        print(f'\n[{category}] ' + ('MANDATORY for bootstrap' if category == 'CORE' else 'OPTIONAL for bootstrap; required as applicable by later workflows'))
        for name, flag in commands:
            path = shutil.which(name)
            print(f'{name}: path={path or "MISSING (not on PATH)"}')
            ok = probe([path, flag]) if path else False
            if not ok:
                failures.append((category, name))
    print('\n[SIMULATION] Python package metadata in current interpreter (not import tests)')
    for package in ('cocotb', 'pytest', 'numpy', 'Pillow'):
        try:
            print(f'{package}: {importlib.metadata.version(package)}')
        except importlib.metadata.PackageNotFoundError:
            print(f'{package}: MISSING in this interpreter')
    print('\n[IMPLEMENTATION] ECP5 capability discovery; not a synthesis/route test')
    yosys = shutil.which('yosys')
    nextpnr = shutil.which('nextpnr-ecp5')
    if yosys:
        probe([yosys, '-Q', '-T', '-p', 'help synth_ecp5'])
    if nextpnr:
        probe([nextpnr, '--help'])
    print('Intended target: LFE5U-45F / CABGA381 / speed grade 6.')
    print('Exact target/database usability remains UNPROVEN until a later controlled smoke flow.')
    print('\nMissing/broken executable probes: ' + (', '.join(f'{c}/{n}' for c, n in failures) or 'none'))
    code = int(any(category == 'CORE' for category, _ in failures))
    print(f'Bootstrap doctor exit={code}; this is not RTL/formal/implementation verification.')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
