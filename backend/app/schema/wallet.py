import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from backend.app.core.enum.operation import OperationType


class OperationRequestSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    operation_type: OperationType
    amount: Decimal


class WalletCreateSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    user_id: uuid.UUID
    balance: Decimal = Decimal("0.00")


class WalletResponseSchema(BaseModel):
    id: uuid.UUID
    balance: Decimal
