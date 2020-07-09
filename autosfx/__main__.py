'''AutoSFX'''

def main():
    import argparse, os
    parser = argparse.ArgumentParser(description=__doc__)
    import autosfx
    parser.add_argument('--version', action='version', version='autosfx '+autosfx.__version__)

    import autosfx.commands.setup
    import autosfx.commands.powdersum
    import autosfx.commands.centerfinder
    import autosfx.commands.peakfinder
    import autosfx.commands.indexer
    import autosfx.commands.distoptimizer

    modules = [autosfx.commands.setup,
               autosfx.commands.powdersum,
               autosfx.commands.centerfinder,
               autosfx.commands.peakfinder,
               autosfx.commands.indexer,
               autosfx.commands.distoptimizer,
              ]

    subparsers = parser.add_subparsers(title='Choose a command')
    subparsers.required = 'True'

    def get_str_name(module):
        return os.path.splitext(os.path.basename(module.__file__))[0]

    for module in modules:
        this_parser = subparsers.add_parser(get_str_name(module), description=module.__doc__)
        module.add_args(this_parser)
        this_parser.set_defaults(func=module.main)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
