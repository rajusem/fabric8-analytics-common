"""Implementation of benchmarks.

Copyright (c) 2019 Red Hat Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys

from random import randint
from fastlog import log
from time import time
from queue import Queue
from threading import Thread

from report_generator import generate_csv_report
from component_generator import ComponentGenerator
from setup import parse_tags


# directory containing test results
RESULT_DIRECTORY = "test_results"


def check_number_of_results(queue_size, component_analysis_count, stack_analysis_count):
    """Check if we really got the same number of results as expected.

    When the server respond by any HTTP error code (4xx, 5xx), the results
    are NOT stored in the queue. This means that number of results stored
    in the queue might be less than number of threads set up by user via
    CLI parameters in certain situations. This function check this situation.
    """
    log.info("queue size: {size}".format(size=queue_size))

    expected = component_analysis_count + 2 * stack_analysis_count
    if queue_size != expected:
        log.warning("Warning: {expected} results expected, but only {got} is presented".format(
            expected=expected, got=queue_size))
        log.warning("This means that {n} analysis ends with error or exception".format(
            n=expected - queue_size))


def component_analysis_benchmark(queue, threads, component_analysis, thread_count):
    """Component analysis benchmark."""
    g = ComponentGenerator().generator_for_ecosystem("pypi")

    # don't start the generator from the 1st item
    for i in range(randint(10, 100)):
        next(g)

    for t in range(thread_count):
        ecosystem, component, version = next(g)
        with log.indent():
            log.info("Component analysis for e/c/v {} {} {}".format(ecosystem, component, version))
        t = Thread(target=component_analysis.start,
                   args=(t, ecosystem, component, version, queue))
        t.start()
        threads.append(t)
        # skip some items
        for i in range(randint(5, 10)):
            next(g)


def stack_analysis_benchmark(queue, threads, stack_analysis, thread_count):
    """Stack analysis benchmark."""
    # TODO: read automagically from the filelist
    manifests = (
        ("maven", "junit.xml"),
        ("maven", "springboot.xml"),
        ("maven", "vertx_3_4_1.xml"),
        ("maven", "vertx_3_4_2.xml"),
        ("pypi", "requirements_click_6_star.txt"),
        ("pypi", "array_split.txt"),
        ("npm", "wisp.json"),
    )

    for t in range(thread_count):
        manifest_idx = randint(0, len(manifests) - 1)
        manifest = manifests[manifest_idx]

        with log.indent():
            log.info("Stack analysis")
        ecosystem = manifest[0]
        manifest_file = manifest[1]
        t = Thread(target=stack_analysis.start,
                   args=(t, ecosystem, manifest_file, queue))
        t.start()
        threads.append(t)


def wait_for_all_threads(threads):
    """Wait for all threads to finish."""
    log.info("Waiting for all threads to finish")
    for t in threads:
        t.join()
    log.success("Done")


def run_test(cfg, test, i, component_analysis, stack_analysis):
    """Run one selected test."""
    test_name = test["Name"]
    log.info("Starting test #{n} with name '{desc}'".format(n=i, desc=test_name))
    with log.indent():
        start = time()

        threads = []
        queue = Queue()

        with log.indent():
            component_analysis_count = int(test["Component analysis"])
            stack_analysis_count = int(test["Stack analysis"])
            component_analysis_benchmark(queue, threads, component_analysis,
                                         component_analysis_count)
            stack_analysis_benchmark(queue, threads, stack_analysis,
                                     stack_analysis_count)

        wait_for_all_threads(threads)
        queue_size = queue.qsize()
        check_number_of_results(queue_size, component_analysis_count, stack_analysis_count)

        end = time()
        # TODO: use better approach to join paths
        filename = RESULT_DIRECTORY + "/" + test_name.replace(" ", "_") + ".csv"
        log.info("Generating test report into file '{filename}'".format(filename=filename))
        generate_csv_report(queue, start, end, end - start, filename)


def run_all_loaded_tests(cfg, tests, component_analysis, stack_analysis):
    """Run all tests read from CSV file."""
    i = 1
    for test in tests:
        run_test(cfg, test, i, component_analysis, stack_analysis)
        i += 1


def run_tests_with_tags(cfg, tests, tags, component_analysis, stack_analysis):
    """Run tests read from CSV file that are marged by any of tags provided in tags parameter."""
    i = 1
    for test in tests:
        test_tags = parse_tags(test["Tags"])
        test_name = test["Name"]
        if tags <= test_tags:
            run_test(cfg, test, i, component_analysis, stack_analysis)
            i += 1
        else:
            log.info("Skipping test #{n} with name '{desc}'".format(n=i, desc=test_name))


def no_tests(tests):
    """Predicate for number of tests."""
    return not tests or len(tests) == 0


def start_tests(cfg, tests, tags, component_analysis, stack_analysis):
    """Start all tests using the already loaded configuration."""
    log.info("Run tests")
    with log.indent():
        if no_tests(tests):
            log.error("No tests loaded!")
            sys.exit(-1)
        if len(tests) == 1:
            log.success("Loaded 1 test")
        else:
            log.success("Loaded {n} tests".format(n=len(tests)))
        if not tags:
            run_all_loaded_tests(cfg, tests, component_analysis, stack_analysis)
        else:
            run_tests_with_tags(cfg, tests, tags, component_analysis, stack_analysis)