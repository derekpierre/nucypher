import random
import time
from typing import Callable

import maya
import pytest
import pytest_twisted as pt
import requests
from twisted.internet import threads

from nucypher.network.middleware import NucypherMiddlewareClient
from nucypher.network.trackers import AvailabilityTracker
from nucypher.utilities.sandbox.ursula import start_pytest_ursula_services


@pytest.fixture(scope="module")
def ursula_services_subset(blockchain_ursulas):
    # we don't need all ten ursulas to have services running
    _subset_of_ursulas = set(blockchain_ursulas[0:5])

    # Start up self-services
    for u in _subset_of_ursulas:
        start_pytest_ursula_services(ursula=u)

    yield _subset_of_ursulas


@pt.inlineCallbacks
def test_availability_tracker_success(ursula_services_subset):
    ursula = random.choice(tuple(ursula_services_subset))
    ursula._availability_tracker = AvailabilityTracker(ursula=ursula)

    def measure():
        ursula._availability_tracker.start()
        assert ursula._availability_tracker.score == AvailabilityTracker.MAXIMUM_SCORE
        ursula._availability_tracker.record(False, reason='why not?')
        assert ursula._availability_tracker.score == AvailabilityTracker.CHARGE_RATE * AvailabilityTracker.MAXIMUM_SCORE
        for i in range(7):
            ursula._availability_tracker.record(True)
        assert ursula._availability_tracker.score > 9.5

    def maintain():
        tracker = ursula._availability_tracker
        tracker.maintain()

        # The node goes offline for some time...
        for _ in range(10):
            ursula._availability_tracker.record(False, reason='fake failure reason')

        assert tracker.score < 4
        assert tracker.status() == (tracker.score > (tracker.SENSITIVITY * tracker.MAXIMUM_SCORE))
        assert not tracker.status()

        original_issuer = AvailabilityTracker.issue_alerts
        warnings = dict()
        def issue_warnings(tracker, *args, **kwargs):
            result = original_issuer(tracker, *args, **kwargs)
            warnings[tracker.score] = result
        AvailabilityTracker.issue_alerts = issue_warnings
        tracker.maintain()
        assert warnings
        AvailabilityTracker.issue_alerts = original_issuer

        # to keep this test fast, were just checking for a single entry
        # (technically there will be 10, but resolution is one second.)
        assert len(tracker.excuses) > 0

    def raise_to_maximum():
        tracker = ursula._availability_tracker
        for i in range(150):
            tracker.record(True)
        assert tracker.score > 9.98
        assert tracker.status() == bool(tracker.score > (tracker.SENSITIVITY * tracker.MAXIMUM_SCORE))
        assert tracker.status()

    # Run the Callbacks
    try:
        d = threads.deferToThread(measure)
        yield d
        d = threads.deferToThread(maintain)
        yield d
        d = threads.deferToThread(raise_to_maximum)
        yield d
    finally:
        if ursula._availability_tracker:
            ursula._availability_tracker.stop()
            ursula._availability_tracker = None


@pt.inlineCallbacks
def test_availability_tracker_integration(ursula_services_subset, monkeypatch):
    # Start up self-services
    ursula = random.choice(tuple(ursula_services_subset))
    ursula._availability_tracker = AvailabilityTracker(ursula=ursula)
    assert not ursula._availability_tracker.running, "Tracker not yet started"
    assert ursula._availability_tracker.score == AvailabilityTracker.MAXIMUM_SCORE, "Initial score is maximum"
    assert len(ursula._availability_tracker.responders) == 0, "No responders since not started"
    assert len(ursula._availability_tracker.excuses) == 0, "No excuses since not started"

    def maintain():
        tracker = ursula._availability_tracker

        def mock_node_information_endpoint(middleware, port, *args, **kwargs):
            if ursula.rest_interface.port == port:
                raise requests.exceptions.ConnectionError("Fake Reason")  # Make this node unreachable
            for u in ursula_services_subset:
                if u.rest_interface.port == port:
                    return bytes(u)

        # apply the monkeypatch for requests.get to mock_get
        monkeypatch.setattr(NucypherMiddlewareClient,
                            NucypherMiddlewareClient.node_information.__name__,
                            mock_node_information_endpoint)

        tracker.start()

        def is_running():
            return tracker.running
        _wait_for_assertion(assertion_check=is_running)

        # use one ursula: any ursula except itself
        tracker.measure_sample(random.sample(ursula_services_subset.difference({ursula}), k=1))

        assert len(tracker.excuses), "Issue encountered due to node being unreachable"
        assert len(tracker.responders)
        assert tracker.score < AvailabilityTracker.MAXIMUM_SCORE, "Score is decreased due to node being unreachable"

    # Run the Callbacks
    try:
        d = threads.deferToThread(maintain)
        yield d
    finally:
        if ursula._availability_tracker:
            ursula._availability_tracker.stop()
            ursula._availability_tracker = None


@pt.inlineCallbacks
def test_availability_tracker_score_decreases_then_increases(ursula_services_subset, monkeypatch):
    # Start up self-services
    ursula = random.choice(tuple(ursula_services_subset))
    ursula._availability_tracker = AvailabilityTracker(ursula=ursula)

    def maintain():
        tracker = ursula._availability_tracker

        make_node_reachable = False

        def mock_node_information_endpoint(middleware, port, *args, **kwargs):
            if ursula.rest_interface.port == port:
                if not make_node_reachable:
                    raise requests.exceptions.ConnectionError("Fake Reason")  # Make this node unreachable
                else:
                    return bytes(ursula)
            for u in ursula_services_subset:
                if u.rest_interface.port == port:
                    return bytes(u)

        # apply the monkeypatch for requests.get to mock_get
        monkeypatch.setattr(NucypherMiddlewareClient,
                            NucypherMiddlewareClient.node_information.__name__,
                            mock_node_information_endpoint)

        tracker.start()

        # use any ursula but itself
        tracker.measure_sample(random.sample(ursula_services_subset.difference({ursula}), k=1))

        assert len(tracker.responders) > 0
        assert len(tracker.excuses) > 0, "node unreachable so there were problems"
        assert tracker.score < AvailabilityTracker.MAXIMUM_SCORE, "Score drops because node was unreachable"

        old_score = tracker.score

        # perform check again, but this time make node reachable
        make_node_reachable = True

        tracker.measure_sample(random.sample(ursula_services_subset.difference({ursula}), k=1))

        # ensure score increased
        assert tracker.score > old_score, "Score increased since node is now reachable"

    # Run the Callbacks
    try:
        d = threads.deferToThread(maintain)
        yield d
    finally:
        if ursula._availability_tracker:
            ursula._availability_tracker.stop()
            ursula._availability_tracker = None


@pt.inlineCallbacks
def test_availability_tracker_integration_multiple_nodes(ursula_services_subset, monkeypatch):
    for u in ursula_services_subset:
        u._availability_tracker = AvailabilityTracker(ursula=u)

    def maintain():
        def mock_node_information_endpoint(middleware, port, *args, **kwargs):
            for u in ursula_services_subset:
                if u.rest_interface.port == port:
                    return bytes(u)

        # apply the monkeypatch for requests.get to mock_get
        monkeypatch.setattr(NucypherMiddlewareClient,
                            NucypherMiddlewareClient.node_information.__name__,
                            mock_node_information_endpoint)

        for u in ursula_services_subset:
            u._availability_tracker.start(now=False)  # don't start immediately to allow for test

        for u in ursula_services_subset:
            # run check with all other ursulas except itself
            u._availability_tracker.measure_sample(ursulas=list(ursula_services_subset.difference({u})))

        for u in ursula_services_subset:
            assert len(u._availability_tracker.responders) == len(ursula_services_subset) - 1  # everyone but itself
            assert len(u._availability_tracker.excuses) == 0, "no issues"
            assert u._availability_tracker.score == AvailabilityTracker.MAXIMUM_SCORE

    # Run the Callbacks
    try:
        d = threads.deferToThread(maintain)
        yield d
    finally:
        for u in ursula_services_subset:
            if u._availability_tracker:
                u._availability_tracker.stop()
                u._availability_tracker = None


@pt.inlineCallbacks
def test_availability_tracker_integration_all_nodes_impersonate_other_nodes_except_one(ursula_services_subset, monkeypatch):
    valid_ursula = random.choice(tuple(ursula_services_subset))

    for u in ursula_services_subset:
        u._availability_tracker = AvailabilityTracker(ursula=u)

    def maintain():
        def mock_node_information_endpoint(middleware, *args, **kwargs):
            # all nodes except for valid_ursula are invalid since their bytes representation is incorrect
            return bytes(valid_ursula)

        # apply the monkeypatch for requests.get to mock_get
        monkeypatch.setattr(NucypherMiddlewareClient,
                            NucypherMiddlewareClient.node_information.__name__,
                            mock_node_information_endpoint)

        for u in ursula_services_subset:
            u._availability_tracker.start(now=False)  # don't start immediately to allow for test

        for u in ursula_services_subset:
            # run check with all other ursulas except itself
            u._availability_tracker.measure_sample(ursulas=list(ursula_services_subset.difference({u})))

        for u in ursula_services_subset:
            if valid_ursula is u:
                # only 1 valid ursula so no one else to use for check since all others are invalid nodes
                # nothing changes since invalid nodes can't be used for availability check
                assert len(u._availability_tracker.responders) == 0, "no responders since other nodes are invalid"
                assert len(u._availability_tracker.excuses) == 0, "no excuses"
                assert u._availability_tracker.score == AvailabilityTracker.MAXIMUM_SCORE, "score remained unchanged since no responders"
            else:
                assert len(u._availability_tracker.responders) == 1,  "only valid_ursula responded"
                assert len(u._availability_tracker.excuses) == 1,  "excuse from valid_ursula"
                # score decreased because valid_ursula responded to check, and bytes don't match
                assert u._availability_tracker.score < AvailabilityTracker.MAXIMUM_SCORE, "score decreased"
    # Run the Callbacks
    try:
        d = threads.deferToThread(maintain)
        yield d
    finally:
        for u in ursula_services_subset:
            if u._availability_tracker:
                u._availability_tracker.stop()
                u._availability_tracker = None


def _wait_for_assertion(assertion_check: Callable, timeout: int = 1):
    start = maya.now()
    while True:
        try:
            assert assertion_check()
        except AssertionError:
            now = maya.now()
            if (now - start).total_seconds() > timeout:
                pytest.fail()
            time.sleep(0.1)
            continue
        else:
            break
