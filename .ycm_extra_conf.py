def Settings( **kwargs ):
    return {
        'flags' : [
            '-x',
            'cxx',
            '-Wall',
            '-Wextra',
            '-Werror',
            # libs
            '-lsystemd',
            '-pthread',
            # includes
            '-I./src',
            ],
        }
