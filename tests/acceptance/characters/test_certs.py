from http import HTTPStatus

import pytest_twisted
from twisted.internet.threads import deferToThread

from nucypher.crypto.powers import TLSHostingPower
from nucypher.crypto.tls import generate_self_signed_certificate
from nucypher.utilities.certs import P2PSession
from nucypher.utilities.logging import GlobalLoggerSettings

GlobalLoggerSettings.set_log_level(log_level_name="debug")
GlobalLoggerSettings.start_console_logging()


@pytest_twisted.inlineCallbacks
def test_cert_changed_for_service(monkeypatch, ursulas):
    ursula = ursulas[0]
    deployer = ursula.get_deployer()
    deployer.addServices()
    deployer.catalogServers(deployer.hendrix)
    deployer.start()

    session = P2PSession()

    def check_connection_to_ursula(node):
        response = session.get("https://{}/public_information".format(node.rest_url()))
        assert response.status_code == HTTPStatus.OK

    def error_handler(e):
        """Prints the error and raises it"""
        print(e.getTraceback())
        raise e

    d = deferToThread(check_connection_to_ursula, ursula)
    d.addErrback(error_handler)
    yield d

    yield deployer.tls_service.stopService()
    yield deployer.hendrix.stopService()

    # generate new certificate for ursula
    certificate, key = generate_self_signed_certificate(host=ursula.rest_interface.host)
    hosting_power = ursula._crypto_power.power_ups(TLSHostingPower)
    hosting_power.keypair._privkey = key
    hosting_power.keypair.certificate = certificate

    deployer = ursula.get_deployer()
    deployer.addServices()
    deployer.start()

    d = deferToThread(check_connection_to_ursula, ursula)
    d.addErrback(error_handler)
    yield d
