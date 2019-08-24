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


from nucypher.characters.lawful import Bob
from nucypher.characters.utils import BobCard
from nucypher.utilities.sandbox.middleware import MockRestMiddleware


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

