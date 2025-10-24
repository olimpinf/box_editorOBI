#!/usr/bin/env python3

import os, sys

def get_compile_command(src_fn, exe_fn):
    u"Build the command line for `src_fn`."
    
    # get compilers from environment
    gcc = os.getenv('CC')
    if not gcc:
        gcc = 'gcc'
        gpp = os.getenv('CXX')
    if not gpp:
        gpp = 'g++'

    if src_fn.endswith('.c'):
        cmd_line = '%s -O2 -std=c17 -o %s %s -lm' % (gcc, exe_fn, src_fn)

    elif src_fn.endswith('.cpp') or src_fn.endswith('.cc'):
        cmd_line = '%s -std=c++17 -O2 -o %s %s' % (gpp, exe_fn, src_fn)
        if sys.platform == 'darwin':
            # (mateus) aumentar o stack size explicitamente para 128 MB
            # quando rodando localmente em mac (para evitar bugs locais)
            cmd_line = cmd_line + " -Wl,-stack_size,0x8000000"

    elif src_fn.endswith('.pas'):
        cmd_line = 'fpc -O2 -Tlinux -o%s %s' % (exe_fn, src_fn)

    elif src_fn.endswith('.java'):
        cmd_line = ('javac %s && ln -sf `pwd`/.box/run_java.sh %s && '
                    'chmod a+x %s' % (src_fn, exe_fn, exe_fn))

    elif src_fn.endswith('.py'):
        cmd_line = 'ln -sf `pwd`/%s %s && chmod a+x %s' % (src_fn, exe_fn, exe_fn)

    elif src_fn.endswith('.js'):
        basename,ext = os.path.splitext(src_fn)
        NODE='~/.nvm/versions/node/v12.16.3/bin/node'
        #exe_fn = change_extension(src_fn, 'exe')
        cmd_line = ('cat `pwd`/.box/prenode.js > tmp && '
                    #cmd_line = ('cat "/home/exec_corretor/bin/saci_exec/prenode.js" > tmp && '
                    #cmd_line = ('cat "/Users/ranido/bin/saci_exec/prenode.js" > tmp && '
                    'cat %s >> tmp && mv tmp %s && '
                    'ln -sf `pwd`/.box/run_javascript.sh %s && '
                    'chmod a+x %s'
                    % (src_fn, basename+'__.tmp', exe_fn, exe_fn))
    else:
        return '', 'Unknown extension for source file.'

    return cmd_line, ''
