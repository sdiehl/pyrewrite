import sys
import pprint
import argparse
import readline
import traceback
from functools import partial

from rewrite import aparse, match
from rewrite.matching import free, freev
from toplevel import module, NoMatch

banner = """Pyrewrite
------------------------------------
Type :help for for more information.
"""

def completer(mod, text, state):
    opts = [i for i in mod.keys() if i.startswith(text)]
    if state < len(opts):
        return opts[state]
    else:
        return None

prelude = {}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('module', nargs='?', help='Module')
    parser.add_argument('--noprelude', action='store_true', help='Include prelude')
    args = parser.parse_args()

    # State
    mod = {}
    last = None
    stack = []

    if args.module:
        with open(args.module) as fd:
            mod = module(fd.read())

    if not args.noprelude:
        mod.update(prelude)

    print banner
    readline.parse_and_bind("tab: complete")
    readline.set_completer(partial(completer, mod))

    while True:
        try:
            line = raw_input('>> ').strip()
        except EOFError:
            break


        #-----------------------------------------------
        if line.startswith('?'):
            at = aparse(line[1:])
            matcher = partial(match, freev(at))
            matched, localbind = matcher(last)
            stack.extend(localbind)

            if matched:
                print stack
            else:
                print 'failed'

        #-----------------------------------------------
        elif line.startswith('!'):
            try:
                rr = mod[line[1:].strip()]
                last = rr.rewrite(last)
                print last
            except KeyError:
                print "No such rule or strategy '%s'" % line[1:]
            except NoMatch:
                print 'failed'

        #-----------------------------------------------
        elif line.startswith(':s'):
            try:
                rr = mod[line[1:].strip()]
                print rr
            except KeyError:
                print "No such rule or strategy '%s'" % line[1:]

        #-----------------------------------------------
        elif line.startswith(':t'):
            try:
                at = aparse(line[2:])
                print type(at).__name__
            except Exception as e:
                print e

        #-----------------------------------------------
        elif line.startswith(':bindings'):
            if stack:
                pprint.pprint(stack)
            continue

        #-----------------------------------------------
        elif line.startswith(':let'):
            env = module(line[4:], _env=mod)
            mod.update(env)

        #-----------------------------------------------
        elif line.startswith(':load'):
            fname = line[5:].strip()
            try:
                contents = open(fname).read()
                mod.update(module(contents))
            except IOError:
                print "No such module", fname
        #-----------------------------------------------
        elif line.startswith(':browse'):
            pprint.pprint(mod)

        #-----------------------------------------------
        elif line.startswith(':help'):
            pass

        #-----------------------------------------------
        else:
            stack = []
            try:
                last = aparse(line)
                print last
            except EOFError:
                pass
            except Exception as e:
                print traceback.format_exc()


if __name__ == '__main__':
    main()
