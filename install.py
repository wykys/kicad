#!/usr/bin/env python3
# wykys
# automation of installation and administration of KLIB in KiCAD
import os
import sys

from colorama import Back, Fore, Style

KLIB = {
    'W3D': 'packages3d',
    'WMOD': 'modules',
    'WSYM': 'library',
}

KICAD = {
    'KISYSMOD': '/usr/share/kicad/modules',
    'KISYS3DMOD': '/usr/share/kicad/modules/packages3d',
    'KICAD_PTEMPLATES': '/usr/share/kicad/template',
    'KICAD_SYMBOL_DIR': '/usr/share/kicad/library',
}

LIB = '.lib'
MOD = '.pretty'


path_klib = os.getcwd()
path_kicad_common = os.path.expanduser('~') + '/.config/kicad/kicad_common'
path_fp_lib_table = os.path.expanduser('~') + '/.config/kicad/fp-lib-table'
path_sym_lib_table = os.path.expanduser('~') + '/.config/kicad/sym-lib-table'


def error(text):
    print('{}{}ERROR:{} {}{}'.format(Fore.RED, Style.BRIGHT, Style.NORMAL, text, Style.RESET_ALL), file=sys.stderr)
    exit(1)


def ok(text):
    print('{}{}OK:{} {}{}'.format(Fore.GREEN, Style.BRIGHT, Style.NORMAL, text, Style.RESET_ALL), file=sys.stdout)


def info(text):
    print('{}{}INFO:{} {}{}'.format(Fore.WHITE, Style.BRIGHT, Style.NORMAL, text, Style.RESET_ALL), file=sys.stdout)


def get_libraries(path, extension):
    if not os.path.exists(path):
        error('file {} does not exist'.format(path))

    ext_len = len(extension)
    return sorted(
        f.name[:-ext_len] for f in os.scandir(path) if len(f.name) > ext_len and f.name[-ext_len:] == extension
    )


def environment_variables(path):
    if not os.path.exists(path):
        error('file {} does not exist'.format(path))

    with open(path, 'r') as fr:
        config_old = fr.readlines()

    config_new = [
        line for line in config_old if not any(
            (
                any(key in line for key in KICAD),
                any(key in line for key in KLIB)
            )
        )
    ]

    for key in KICAD:
        config_new.append('{}={}\n'.format(key, KICAD[key]))

    for key in KLIB:
        config_new.append('{}={}/{}\n'.format(key, path_klib, KLIB[key]))

    with open(path, 'w') as fw:
        fw.writelines(config_new)

    ok('{} is updated'.format(path))


def lib_table(path, library, var, extension):
    if not os.path.exists(path):
        error('file {} does not exist'.format(path))

    with open(path, 'r') as fr:
        lib_table_old = fr.readlines()

    lib_table_new = [line for line in lib_table_old if not var in line][:-1]
    var = '${{{}}}'.format(var)

    for lib in library:
        lib_table_new.append(
            '  (lib (name {})(type {})(uri {}/{}{})(options "")(descr ""))\n'.format(
                lib,
                'Legacy' if extension == LIB else 'KiCad',
                var,
                lib,
                extension
            )
        )

    lib_table_new.append(')\n')

    with open(path, 'w') as fw:
        fw.writelines(lib_table_new)

    ok('{} is updated'.format(path))


if __name__ == '__main__':
    klib_library = get_libraries(KLIB['WSYM'], LIB)
    klib_modules = get_libraries(KLIB['WMOD'], MOD)

    kicad_library = get_libraries(KICAD['KICAD_SYMBOL_DIR'], LIB)
    kicad_modules = get_libraries(KICAD['KISYSMOD'], MOD)

    info('update enviroment variables')
    environment_variables(path_kicad_common)

    info('update official kicad library')
    lib_table(path_sym_lib_table, kicad_library, 'KICAD_SYMBOL_DIR', LIB)
    lib_table(path_fp_lib_table, kicad_modules, 'KISYSMOD', MOD)

    info('update klib')
    lib_table(path_sym_lib_table, klib_library, 'WSYM', LIB)
    lib_table(path_fp_lib_table, klib_modules, 'WMOD', MOD)
