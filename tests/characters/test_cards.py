"""
This file is part of nucypher.

nucypher is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

nucypher is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with nucypher.  If not, see <https://www.gnu.org/licenses/>.
"""
from nucypher.crypto.powers import SigningPower, DecryptingPower

from nucypher.characters.lawful import Alice, Bob
from nucypher.characters.utils import AliceCard, BobCard
from nucypher.utilities.sandbox.middleware import MockRestMiddleware


def test_alice_card():
    alice = Alice(federated_only=True,
                  network_middleware=MockRestMiddleware())

    alice_card = alice.get_card()

    hex_alice = alice_card.to_hex()
    assert AliceCard.from_hex(hex_alice) == alice_card

    base64_alice = alice_card.to_base64()
    assert AliceCard.from_base64(base64_alice) == alice_card

    bytes_alice = bytes(alice_card)
    assert AliceCard.from_bytes(bytes_alice) == alice_card

    alice_card_keys = alice_card.keys()
    assert len(alice_card_keys) == 1
    assert 'alice_verifying_key' in alice_card_keys

    alice_card_verifying_key_bytes = alice_card['alice_verifying_key']
    assert bytes(alice.public_keys(SigningPower)) == alice_card_verifying_key_bytes


def test_bob_card():
    bob = Bob(federated_only=True,
              start_learning_now=False,
              network_middleware=MockRestMiddleware())

    bobs_card = bob.get_card()

    hex_bob = bobs_card.to_hex()
    assert BobCard.from_hex(hex_bob) == bobs_card

    base64_bob = bobs_card.to_base64()
    assert BobCard.from_base64(base64_bob) == bobs_card

    bytes_bob = bytes(bobs_card)
    assert BobCard.from_bytes(bytes_bob) == bobs_card

    bobs_card_keys = bobs_card.keys()
    assert len(bobs_card_keys) == 2
    assert 'bob_verifying_key' in bobs_card_keys
    assert 'bob_encrypting_key' in bobs_card_keys

    bobs_card_verifying_key_bytes = bobs_card['bob_verifying_key']
    bobs_card_encrypting_key_bytes = bobs_card['bob_encrypting_key']
    assert bytes(bob.public_keys(SigningPower)) == bobs_card_verifying_key_bytes
    assert bytes(bob.public_keys(DecryptingPower)) == bobs_card_encrypting_key_bytes
