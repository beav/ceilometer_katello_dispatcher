# a lot of this is based on python-rhsm and katello-cli's Makfiles

SRC_DIR     = src/ceilometer_katello_dispatcher
PYFILES=`find  src/ -name "*.py"`
TESTFILES=`find test/ -name "*.py"`
STYLEFILES=$(PYFILES)

.PHONY: test cover

cover:
	nosetests --with-coverage --cover-package=ceilometer_katello_dispatcher --cover-inclusive .
test:
	cd test && nosetests

pyflakes:
# pyflakes doesn't have a config file, cli options, or a ignore tag
# and the variants of "redefination" we get now aren't really valid
# and other tools detect the valid cases, so ignore these
#
    -@TMPFILE=`mktemp` || exit 1; \
    pyflakes $(STYLEFILES) |  grep -v "redefinition of unused.*from line.*" \
    | grep -v ".*ourjson.*unable to detect undefined names" | tee $$TMPFILE; \
    ! test -s $$TMPFILE

pylint:
	-@PYTHONPATH="src/" pylint --rcfile=pylintrc $(STYLEFILES)

tablint:
	@! GREP_COLOR='7;31' grep --color -nP "^\W*\t" $(STYLEFILES)

trailinglint:
	@! GREP_COLOR='7;31'  grep --color -nP "[ \t]$$" $(STYLEFILES)

whitespacelint: tablint trailinglint

# look for things that are likely debugging code left in by accident
debuglint:
	@! GREP_COLOR='7;31' grep --color -nP "pdb.set_trace|pydevd.settrace|import ipdb|import pdb|import pydevd" $(STYLEFILES)

gettext_lint:
	@TMPFILE=`mktemp` || exit 1; \
	pcregrep -n --color=auto -M  "_\(.*[\'|\"].*[\'|\"]\s*\+\s*[\"|\'].*[\"|\'].*\)" $(STYLEFILES) | tee $$TMPFILE; \
	! test -s $$TMPFILE

INDENT_IGNORE="E121,E122,E123,E124,E125,E126,E127,E128"
pep8:
	@TMPFILE=`mktemp` || exit 1; \
	pep8 --ignore E501,$(INDENT_IGNORE) --exclude ".#*" --repeat src $(STYLEFILES) | tee $$TMPFILE; \
	! test -s $$TMPFILE

rpmlint:
	@TMPFILE=`mktemp` || exit 1; \
	rpmlint -f rpmlint.config ceilometer_katello_dispatcher.spec | grep -v "^.*packages and .* specfiles checked\;" | grep -v "invalid-url" | tee $$TMPFILE; \
	! test -s $$TMPFILE

stylish: pyflakes whitespacelint pep8 gettext_lint rpmlint debuglint

