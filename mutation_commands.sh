#!/bin/bash
set -e  # Script will exit nonzero if any subcommands fail.

projectDir="repos/resyntax/default-recommendations/contract-shortcuts-test.rkt"

subcmd=$1
if [ $subcmd = "setup" ]; then
    # Add any setup that needs to be run once before any other steps are taken.
    true
elif [ $subcmd = "discover_tests" ]; then
    # Prints a newline-separated list of test case names.
    grep "(test-case" "$projectDir" | sed 's/(test-case//g' | sed 's/"//g'
elif [ $subcmd = "run_test" ]; then
    test_name=$2
    # Runs the test called $test_name.
    raco test ++arg -t ++arg "Test Suite" ++arg "$test_name" "$projectDir"
elif [ $subcmd = "run_test_batch" ]; then
    args="raco test "
    for test in "${@:2}"; do
        args+="$arg ++arg -t ++arg 'Test Suite' ++arg '$test' "
    done
    args+="$projectDir"
    eval $args
fi
