# More information: https://wiki.ubuntu.com/Touch/Testing
#
# Notes for autopilot tests:
# -----------------------------------------------------------
# In order to run autopilot tests:
# sudo apt-add-repository ppa:autopilot/ppa
# sudo apt-get update
# sudo apt-get install python-autopilot autopilot-qt
#############################################################

TRANSLATION_ROOT=.

APP_ID=com.ubuntu.checkbox

MO_FILES=$(foreach infile,$(basename $(notdir $(wildcard ./po/*.po))),$(TRANSLATION_ROOT)/share/locale/$(infile)/LC_MESSAGES/$(APP_ID).mo)
QMLJS_FILES:=$(shell find . -name "*.qml" -o -name "*.js" | grep -v ./tests)
PY_FILES=$(wildcard ./py/*.py) build-me get-libs

all:

autopilot:
	./get-libs
	chmod +x tests/autopilot/run
	tests/autopilot/run

check:
	qmltestrunner -qt=5 -input tests/unit

run:
	/usr/bin/qmlscene $@ checkbox-touch.qml

build-translations: $(MO_FILES)
	echo $(MO_FILES)

po:
	mkdir -p $(CURDIR)/po

po/checkbox-touch.pot: $(QMLJS_FILES) $(PY_FILES) | po
	xgettext -o po/checkbox-touch.pot --qt --c++ --add-comments=TRANSLATORS --keyword=tr --keyword=tr:1,2 $(QMLJS_FILES) --from-code=UTF-8
	xgettext -o po/checkbox-touch.pot --join-existing --language=python --add-comments=TRANSLATORS --keyword=_ --keyword=N_ $(PY_FILES)


$(TRANSLATION_ROOT)/share/locale/%/LC_MESSAGES/$(APP_ID).mo: po/%.po
	mkdir -p $(TRANSLATION_ROOT)/share/locale/$*/LC_MESSAGES && msgfmt -o $@ $^

