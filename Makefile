AIRLINE_NAME?= "French Airline"
AIRPLANE_NAME?= FA101
SNAPSHOT_FILENAME?= french_airline.snap


DOCTEST_BIN?= python -m doctest
# __DOCTEST_OPTS+= -v
DOCTEST_ENVIRONMENT_|+= DEBUG=False #
DOCTEST?= $(DOCTEST_ENVIRONMENT_|)$(DOCTEST_BIN) $(__DOCTEST_OPTS)
# |_DOCTEST?= | more


CLI_BIN?= python cli.py
CLI_ENVIRONMENT_|+= AIRLINE_NAME=$(AIRLINE_NAME)
CLI_ENVIRONMENT_|+= AIRPLANE_NAME=$(AIRPLANE_NAME)
CLI_ENVIRONMENT_|+= #
CLI?= $(CLI_ENVIRONMENT_|)$(CLI_BIN)

# |_RUN_ADD?= && cat $(SNAPSHOT_FILENAME)
# |_RUN_BOOK?= && cat $(SNAPSHOT_FILENAME)
# |_RUN_CANCEL?= && cat $(SNAPSHOT_FILENAME)
# |_RUN_LIST?= && cat $(SNAPSHOT_FILENAME)


#----------------------------------------------------------------------
# Targets
#----------------------------------------------------------------------

_default_target :: test clean_tests
_default_target :: run

install_module:
	pip install -r requirements.txt

test: test_airplane test_airline
test_airline:
	$(DOCTEST) airline.py $(|_DOCTEST)

test_airplane:
	$(DOCTEST) airplane.py $(|_DOCTEST)

run: run_usage delete_snapshot run_list run_add run_book show_snapshot run_cancel

run_add:
	$(CLI) ADD $(AIRPLANE_NAME) $(|_RUN_ADD)  # FAIL if pre-loaded from snapshot, SUCCESS otherwise

run_book:
	$(CLI) BOOK A0 1 $(|_RUN_BOOK) # FAIL if pre-loaded from snapshot, SUCCESS otherwise
	$(CLI) BOOK A1 1 $(|_RUN_BOOK) # SUCCESS
	$(CLI) BOOK F8 1 $(|_RUN_BOOK) # FAIL    (out of bound!)
	$(CLI) BOOK L0 8 $(|_RUN_BOOK) # SUCCESS

run_cancel:
	$(CLI) CANCEL A1 1 $(|_RUN_CANCEL) # SUCCESS
	$(CLI) CANCEL L0 8 $(|_RUN_CANCEL) # SUCCESS

run_list:
	$(CLI) LIST $(|_RUN_LIST)

run_usage:
	$(CLI)

delete_snapshot:
	rm -f $(SNAPSHOT_FILENAME)

show_snapshot:
	cat $(SNAPSHOT_FILENAME)

distclean: clean_cache clean_tests

clean_cache:
	rm -rf __pycache__

clean_tests:
	rm -rf test*

package_code: distclean
	cd .. && tar --exclude='.git' -cvzf challenge.gz airline
