from typing import Optional
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, Purchase, Domain


async def get_user_or_create(
    session: AsyncSession,
    user_id: int,
    username: Optional[str] = None,
    full_name: Optional[str] = None,
) -> Optional[User]:
    """
    Получает пользователя по telegram ID.
    
    Args:
        session: активная асинхронная сессия
        user_id: telegram ID пользователя
        username, full_name: данные для создания
    
    Returns:
        User или None
    """
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is not None:
        return user

    new_user = User(
        id=user_id,
        username=username,
        full_name=full_name or "Unknown",
        balance=0,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


async def buy_domain(
    session: AsyncSession,
    user_id: int,
    price: float | Decimal | str | int,
    domain_name: str,
    years: int,
    payment_method: str = "balance",
    description: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Списывает деньги с баланса и создаёт запись о покупке домена.
    """
    try:
        async with session.begin():
            stmt = select(User).where(User.id == user_id).with_for_update()
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            price_dec = Decimal(str(price))

            if user.balance < price_dec:
                return False, "insufficient_funds"

            user.balance -= price_dec

            purchase = Purchase(
                user_id=user_id,
                amount=price_dec,
                item_type="domain",
                description=description or f"Покупка домена {domain_name}",
                success=True,
                payment_method=payment_method,
            )
            session.add(purchase)
            domain = Domain(
                domain_name=domain_name,
                owner_id=user_id,
                status="active",
                expires_at=datetime.now(timezone.utc) + timedelta(days=365 * years),
            )
            session.add(domain)
            return True, "success"

    except Exception as e:
        return False, f"error: {str(e)}"


async def topup_balance(
        session: AsyncSession,
        user_id: int,
        amount: float
    ):
    try:
        async with session.begin():
            stmt = select(User).where(User.id == user_id).with_for_update()
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            price_dec = Decimal(str(amount))

            user.balance += price_dec
            return True, "success"

    except Exception as e:
        return False, f"error: {str(e)}"