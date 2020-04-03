import pytest_twisted as pt
from twisted.internet import threads

from nucypher.network.middleware import NucypherMiddlewareClient, RestMiddleware
from nucypher.network.sensors import AvailabilitySensor
from nucypher.utilities.sandbox.ursula import start_pytest_ursula_services


@pt.inlineCallbacks
def test_availability_sensor_success(blockchain_ursulas):

    # Start up self-services
    ursula = blockchain_ursulas.pop()
    start_pytest_ursula_services(ursula=ursula)

    ursula._availability_sensor = AvailabilitySensor(ursula=ursula)

    def measure():
        ursula._availability_sensor.start()
        assert ursula._availability_sensor.score == 10
        ursula._availability_sensor.record(False)
        assert ursula._availability_sensor.score == 9.0
        for i in range(7):
            ursula._availability_sensor.record(True)
        assert ursula._availability_sensor.score > 9.5

    def maintain():
        sensor = ursula._availability_sensor
        sensor.maintain()

        # The node goes offline for some time...
        for _ in range(10):
            ursula._availability_sensor.record(False, reason={'error': 'fake failure reason'})

        assert sensor.score < 4
        assert sensor.status() == (sensor.score > (sensor.SENSOR_SENSITIVITY * sensor.MAXIMUM_SCORE))
        assert not sensor.status()

        original_issuer = AvailabilitySensor.issue_warnings
        warnings = dict()
        def issue_warnings(sensor, *args, **kwargs):
            result = original_issuer(sensor, *args, **kwargs)
            warnings[sensor.score] = result
        AvailabilitySensor.issue_warnings = issue_warnings
        sensor.maintain()
        assert warnings
        AvailabilitySensor.issue_warnings = original_issuer

        # to keep this test fast, were just checking for a single entry
        # (technically there will be 10, but resolution is one second.)
        assert len(sensor._AvailabilitySensor__excuses) > 0

    def raise_to_maximum():
        sensor = ursula._availability_sensor
        for i in range(150):
            sensor.record(True)
        assert sensor.score > 9.98
        assert sensor.status() == bool(sensor.score > (sensor.SENSOR_SENSITIVITY * sensor.MAXIMUM_SCORE))
        assert sensor.status()

    # Run the Callbacks
    try:
        d = threads.deferToThread(measure)
        yield d
        d = threads.deferToThread(maintain)
        yield d
        d = threads.deferToThread(raise_to_maximum)
        yield d
    finally:
        if ursula._availability_sensor:
            ursula._availability_sensor.stop()
            ursula._availability_sensor = None


@pt.inlineCallbacks
def test_availability_sensor_integration(blockchain_ursulas, monkeypatch):

    # Start up self-services
    ursula = blockchain_ursulas[0]
    start_pytest_ursula_services(ursula=ursula)

    def maintain():
        sensor = ursula._availability_sensor

        def mock_node_information_endpoint(middleware, port, *args, **kwargs):
            for u in blockchain_ursulas:
                if u.rest_interface.port == port:
                    if u is ursula:
                        raise RestMiddleware.NotFound("Fake Reason")  # Make this node unreachable
                    else:
                        return bytes(u)

        # apply the monkeypatch for requests.get to mock_get
        monkeypatch.setattr(NucypherMiddlewareClient,
                            NucypherMiddlewareClient.node_information.__name__,
                            mock_node_information_endpoint)

        ursula._availability_sensor.start()
        sensor.measure()  # This makes a REST Call

        # to keep this test fast, were just checking for a single entry
        # (technically there will be 10, but resolution is one second.)
        assert len(sensor._AvailabilitySensor__excuses) > 0

    # Run the Callbacks
    try:
        d = threads.deferToThread(maintain)
        yield d
    finally:
        if ursula._availability_sensor:
            ursula._availability_sensor.stop()
            ursula._availability_sensor = None


@pt.inlineCallbacks
def test_availability_sensor_integration_multiple_checks(blockchain_ursulas, monkeypatch):

    # Start up self-services
    for u in blockchain_ursulas:
        start_pytest_ursula_services(ursula=u)

    def maintain():
        def mock_node_information_endpoint(middleware, port, *args, **kwargs):
            for u in blockchain_ursulas:
                if u.rest_interface.port == port:
                    return bytes(u)

            raise RestMiddleware.NotFound("Fake Reason")  # Make this node unreachable

        # apply the monkeypatch for requests.get to mock_get
        monkeypatch.setattr(NucypherMiddlewareClient,
                            NucypherMiddlewareClient.node_information.__name__,
                            mock_node_information_endpoint)

        for u in blockchain_ursulas:
            u._availability_sensor = AvailabilitySensor(ursula=u)
            u._availability_sensor.start()

        for u in blockchain_ursulas:
            u._availability_sensor.measure()  # This makes a REST Call

        # to keep this test fast, were just checking for a single entry
        # (technically there will be 10, but resolution is one second.)

        for u in blockchain_ursulas:
            assert len(u._availability_sensor.responders) > 0
            assert u._availability_sensor.score == 10

    # Run the Callbacks
    try:
        d = threads.deferToThread(maintain)
        yield d
    finally:
        for u in blockchain_ursulas:
            if u._availability_sensor:
                u._availability_sensor.stop()
                u._availability_sensor = None


@pt.inlineCallbacks
def test_availability_sensor_integration_all_nodes_impersonate_same_node(blockchain_ursulas, monkeypatch):

    ursula = blockchain_ursulas[0]

    # Start up self-services
    for u in blockchain_ursulas:
        start_pytest_ursula_services(ursula=u)

    def maintain():
        def mock_node_information_endpoint(middleware, port, *args, **kwargs):
            return bytes(ursula)

        # apply the monkeypatch for requests.get to mock_get
        monkeypatch.setattr(NucypherMiddlewareClient,
                            NucypherMiddlewareClient.node_information.__name__,
                            mock_node_information_endpoint)

        for u in blockchain_ursulas:
            u._availability_sensor = AvailabilitySensor(ursula=u)
            u._availability_sensor.start()

        for u in blockchain_ursulas:
            u._availability_sensor.measure()  # This makes a REST Call

        # to keep this test fast, were just checking for a single entry
        # (technically there will be 10, but resolution is one second.)

        for u in blockchain_ursulas:
            assert len(u._availability_sensor.responders) > 0
            assert u._availability_sensor.score < 10
            assert len(u._availability_sensor._AvailabilitySensor__excuses) > 0

    # Run the Callbacks
    try:
        d = threads.deferToThread(maintain)
        yield d
    finally:
        for u in blockchain_ursulas:
            if u._availability_sensor:
                u._availability_sensor.stop()
                u._availability_sensor = None