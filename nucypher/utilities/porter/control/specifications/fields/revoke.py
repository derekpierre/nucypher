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
from base64 import b64encode, b64decode
from dataclasses import dataclass

from eth_typing import ChecksumAddress
from marshmallow import fields, post_load

from nucypher.characters.control.specifications.exceptions import InvalidNativeDataTypes
from nucypher.control.specifications.base import BaseSchema
from nucypher.control.specifications.exceptions import InvalidInputData
from nucypher.control.specifications.fields import String, BaseField
from nucypher.policy.collections import Revocation as RevocationClass
from nucypher.utilities.porter.control.specifications.fields import UrsulaChecksumAddress


class Revocation(BaseField, fields.Field):
    def _serialize(self, value: RevocationClass, attr, obj, **kwargs):
        return b64encode(bytes(value)).decode()

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            revocation_bytes = b64decode(value)
            revocation = RevocationClass.from_bytes(revocation_bytes)
            return revocation
        except InvalidNativeDataTypes as e:
            raise InvalidInputData(f"Could not parse {self.name}: {e}")


@dataclass
class RevokeInfo:
    """Simple object that stores revocation information associated with the RevokeInfoSchema."""
    ursula: ChecksumAddress
    revocation: RevocationClass


class RevokeInfoSchema(BaseSchema):
    """Schema for the information needed for off-chain revocation."""
    ursula = UrsulaChecksumAddress(required=True)
    revocation = Revocation(required=True)

    @post_load
    def make_revoke_info(self, data, **kwargs):
        return RevokeInfo(**data)


class RevokeFailureSchema(BaseSchema):
    """Schema for the failed result of off-chain revocation"""
    ursula = UrsulaChecksumAddress()
    failure = String()
