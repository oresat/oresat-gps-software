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
            '-I./src/sgp4/libsgp4',
            ],
        }
