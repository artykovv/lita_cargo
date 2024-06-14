from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from sqlalchemy.orm import joinedload

from database import get_async_session
from router.model import Client, Product, ProductStatus
from router.root.shemas import CreateClients

router = APIRouter(prefix="/api/v1/routes", tags=["user"])

@router.post("/register")
async def register_client(
    query: CreateClients,
    session: AsyncSession = Depends(get_async_session)
):
    # Проверяем, существует ли клиент с такими же параметрами
    existing_client = await session.execute(select(Client).filter_by(name=query.name, number=query.number, city=query.city))
    existing_client = existing_client.scalar()

    if existing_client:
        # Возвращаем информацию о существующем клиенте
        return {"client": existing_client}

    # Если клиент не существует, создаем нового
    stmt = insert(Client).values(query.dict())
    await session.execute(stmt)
    await session.commit()

    # После сохранения клиента делаем запрос к базе данных, чтобы получить только что созданный объект
    created_client = await session.execute(select(Client).filter_by(name=query.name, number=query.number, city=query.city))
    created_client = created_client.scalar()

    return {"client": created_client}


@router.get("/{client_id}")
async def get_client_with_products(
    client_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    # Query the client by their ID with related products
    query = select(Client).options(joinedload(Client.products)).where(Client.id == client_id)
    result = await session.execute(query)
    client = result.scalars().first()

    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    # Filter out products with status "PICKED_UP"
    non_picked_up_products = [product for product in client.products if product.status != ProductStatus.PICKED_UP]

    if not non_picked_up_products:
        return {"message": "No products found for this client"}

    # Calculate the total amount of all client's products
    total_amount = sum(product.amount for product in non_picked_up_products if product.amount is not None)

    # Calculate the total weight of all client's products in kilograms
    total_weight = sum(product.weight for product in non_picked_up_products if product.weight is not None) / 1000

    # Prepare client and product data
    client_data = {
        "id": client.id,
        "name": client.name,
        "number": client.number,
        "city": client.city,
        "total_amount": total_amount,
        "total_weight": total_weight, 
        "products": [
            {
                "id": product.id,
                "product_code": product.product_code,
                "weight": product.weight / 1000 if product.weight is not None else None,  # Convert to kilograms
                "amount": product.amount,
                "date": product.date.isoformat() if product.date else None,  # Assuming date is a datetime object
                "status": product.status.value
            }
            for product in non_picked_up_products
        ]
    }

    return client_data


@router.get("/get/product")
async def get_product_on_track_code(
    code: str,
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Product).where(Product.product_code == code, Product.status != ProductStatus.PICKED_UP)
    result = await session.execute(query)
    data = result.scalars().all()
    return data
