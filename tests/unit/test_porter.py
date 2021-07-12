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
import os
from base64 import b64encode

import pytest

from nucypher.control.specifications.exceptions import InvalidInputData
from nucypher.crypto.constants import ENCRYPTED_KFRAG_PAYLOAD_LENGTH
from nucypher.policy.orders import WorkOrder as WorkOrderClass
from nucypher.utilities.porter.control.specifications.fields import (
    TreasureMapID,
    UrsulaChecksumAddress,
    WorkOrder,
    WorkOrderResult
)
from tests.utils.policy import work_order_setup


def test_treasure_map_id_field(enacted_federated_policy):
    treasure_map_id_hex = enacted_federated_policy.treasure_map.public_id()
    other_hex = b"some date".hex()  # length is not 32-bytes

    field = TreasureMapID()
    serialized = field._serialize(value=treasure_map_id_hex, attr=None, obj=None)
    assert serialized == treasure_map_id_hex
    assert serialized != other_hex

    deserialized = field._deserialize(value=serialized, attr=None, data=None)
    assert deserialized == treasure_map_id_hex
    assert deserialized != other_hex

    field._validate(value=treasure_map_id_hex)
    with pytest.raises(InvalidInputData):
        field._validate(value=other_hex)


def test_ursula_checksum_address_field(get_random_checksum_address):
    ursula_checksum = get_random_checksum_address()
    other_address = get_random_checksum_address()

    assert ursula_checksum != other_address

    field = UrsulaChecksumAddress()
    serialized = field._serialize(value=ursula_checksum, attr=None, obj=None)
    assert serialized == ursula_checksum
    assert serialized != other_address

    deserialized = field._deserialize(value=serialized, attr=None, data=None)
    assert deserialized == ursula_checksum
    assert deserialized != other_address

    field._deserialize(value=ursula_checksum, attr=None, data=None)
    field._deserialize(value=ursula_checksum.lower(), attr=None, data=None)
    field._deserialize(value=ursula_checksum.upper(), attr=None, data=None)
    field._deserialize(value=other_address, attr=None, data=None)
    field._deserialize(value=other_address.lower(), attr=None, data=None)
    field._deserialize(value=other_address.upper(), attr=None, data=None)

    with pytest.raises(InvalidInputData):
        field._deserialize(value="0xdeadbeef", attr=None, data=None)


def test_work_order_field(enacted_federated_policy,
                          federated_ursulas,
                          federated_bob,
                          federated_alice,
                          get_random_checksum_address):
    # Setup
    ursula_address, work_order = work_order_setup(enacted_federated_policy,
                                                  federated_ursulas,
                                                  federated_bob,
                                                  federated_alice)
    reencrypt_result = b"cfrags and signatures"

    # Test Work Order
    work_order_bytes = work_order.payload()
    field = WorkOrder()
    serialized = field._serialize(value=work_order, attr=None, obj=None)
    assert serialized == b64encode(work_order_bytes).decode()

    deserialized = field._deserialize(value=serialized, attr=None, data=None)
    assert deserialized == work_order_bytes

    # Test Work Order Result
    field = WorkOrderResult()
    serialized = field._serialize(value=reencrypt_result, attr=None, obj=None)
    assert serialized == b64encode(reencrypt_result).decode()

    deserialized = field.deserialize(value=serialized, attr=None, data=None)
    assert deserialized == reencrypt_result
