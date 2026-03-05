from typing import Optional
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, exists, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from .models import User, Purchase, Domain, PromoCode, PromoCodeUsage


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
        stmt = select(User).where(User.id == user_id).with_for_update()
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        price_dec = Decimal(str(amount))

        user.balance += price_dec
        return True, "success"

    except Exception as e:
        return False, f"error: {str(e)}"


async def create_promocode(
        session: AsyncSession,
        promocode: str,
        max_uses: int,
        amount: float
    ):
    try:
        async with session.begin():
            promocode = PromoCode(
                code=promocode,
                max_uses=max_uses,
                bonus_amount=amount
            )
            session.add(promocode)
            return True, "success"

    except Exception as e:
        return False, f"error: {str(e)}"


async def get_all_users(session: AsyncSession) -> list[User]:
    """
    Возвращает список всех пользователей
    """
    stmt = select(User).order_by(User.id)
    result = await session.execute(stmt)
    users = result.scalars().all()
    return users


async def get_all_domains_user(session: AsyncSession, user_id: int) -> List[Domain]:
    """
    Возвращает список всех доменов пользователя.
    """
    stmt = (
        select(Domain)
        .where(Domain.owner_id == user_id)
        .order_by(Domain.created_at.desc())
    )

    result = await session.execute(stmt)
    domains = result.scalars().all()

    return domains


async def get_domain_by_id(domain_id: int, session: AsyncSession):
    stmt = select(Domain).where(Domain.id == domain_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_promo_or_none(promocode, session: AsyncSession):
    stmt = select(PromoCode).where(
        PromoCode.code == promocode
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_promo_use(promocode, user_id: int, session: AsyncSession):
    if await session.scalar(
        select(exists().where(
            PromoCodeUsage.promo_code_id == promocode.id,
            PromoCodeUsage.user_id == user_id
        ))
    ):
        return False, "promocode_used"

    if promocode.max_uses is not None and promocode.uses_count >= promocode.max_uses:
        return False, "promo_uses_limit_reached"

    session.add(PromoCodeUsage(promo_code_id=promocode.id, user_id=user_id))

    await session.execute(
        update(PromoCode)
        .where(PromoCode.id == promocode.id)
        .values(
            uses_count=PromoCode.uses_count + 1,
            active=PromoCode.max_uses.is_(None) | (PromoCode.uses_count + 1 < PromoCode.max_uses)
        )
    )

    return True, "success"
