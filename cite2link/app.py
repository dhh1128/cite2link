import sys


def main(argv = None):
    if not argv:
        argv = sys.argv
    try:
        cmd = match_command(argv[1])
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        cmd = help.cmd
    try:
        cmd(*argv[2:])
    except SyntaxWarning:
        sys.stderr.write('\nBad command-line syntax.\n')
        help.cmd()
        sys.exit(1)


if __name__ == '__main__':
    main()