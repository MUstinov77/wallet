from fastapi import APIRouter, Depends, status

from backend.app.core.exceptions import NotFoundException
from backend.app.core.utils.encrypt import get_hashed_password
from backend.app.schema.auth import UserResponseSchema, UserSignupSchema
from backend.app.schema.wallet import WalletCreateSchema
from backend.app.service.user import UserService, get_user_service
from backend.app.service.wallet import WalletService, get_wallet_service


BASE_PREFIX = "/auth"

router = APIRouter(
    prefix=BASE_PREFIX,
    tags=["auth"],
)


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseSchema
)
async def signup(
        create_data: UserSignupSchema,
        user_service: UserService = Depends(get_user_service),
        wallet_service: WalletService = Depends(get_wallet_service)
):
    user_data = create_data.model_dump()
    hashed_password = await get_hashed_password(user_data.pop("password"))
    user_data["hashed_password"] = hashed_password
    user = await user_service.create_instance(user_data)
    if not user:
        raise NotFoundException
    wallet_default_data = WalletCreateSchema(user_id=user.id)
    wallet_create_data = wallet_default_data.model_dump()
    await wallet_service.create_instance(wallet_create_data)
    return user
