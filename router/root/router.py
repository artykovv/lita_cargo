from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, func
from sqlalchemy.orm import joinedload
import pandas as pd
from io import BytesIO
import logging
from datetime import datetime
from fastapi.responses import HTMLResponse, RedirectResponse

from database import get_async_session
from router.model import Client, ProductStatus, Product



router = APIRouter(prefix="/api/routes", tags=["root"])
    

@router.get("/gettt")
async def get( client_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Client).where(Client.id == client_id)
    result = await session.execute(query)
    route = result.scalars().first()
    return route

logger = logging.getLogger(__name__)


@router.post("/register/users/all")
async def create_all_users(file: UploadFile = File(...), session: AsyncSession = Depends(get_async_session)):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Invalid file type")

    try:
        contents = await file.read()
        data = pd.read_excel(BytesIO(contents))
    except Exception as e:
        logger.error(f"Error reading the Excel file: {e}")
        raise HTTPException(status_code=400, detail="Error reading the Excel file")

    required_columns = ["ФИО", "Контакты", "Персональный код", "Город"]
    
    # Log the columns of the file for debugging
    file_columns = data.columns.tolist()
    logger.debug(f"Columns in the file: {file_columns}")

    missing_columns = [col for col in required_columns if col not in file_columns]
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Missing columns: {', '.join(missing_columns)}"
        )

    clients_to_insert = []
    clients_to_update = []

    for index, row in data.iterrows():
        id = row.get("Персональный код")
        name = row.get("ФИО")
        number = row.get("Контакты")
        city = row.get("Город")
        
        if pd.isna(number):
            number = None
        if pd.isna(city):
            city = None

        # Check if the client already exists
        existing_client = await session.get(Client, id)
        if existing_client:
            existing_client.name = name
            existing_client.number = number
            existing_client.city = city
            clients_to_update.append(existing_client)
        else:
            client = Client(
                id=id,  # Using personal code as id
                name=name,
                number=number,
                city=city
            )
            clients_to_insert.append(client)

    try:
        if clients_to_insert:
            session.add_all(clients_to_insert)
        if clients_to_update:
            for client in clients_to_update:
                session.add(client)
        await session.commit()
    except Exception as e:
        logger.error(f"Error committing the session: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error inserting data: {e}")

    return {"status": "success", "inserted": len(clients_to_insert), "updated": len(clients_to_update)}


@router.post("/register/products")
async def create_all_products(file: UploadFile = File(...), session: AsyncSession = Depends(get_async_session)):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Invalid file type")

    try:
        contents = await file.read()
        data = pd.read_excel(BytesIO(contents))
    except Exception as e:
        logger.error(f"Error reading the Excel file: {e}")
        raise HTTPException(status_code=400, detail="Error reading the Excel file")

    required_columns = ["product_code"]
    
    # Log the columns of the file for debugging
    file_columns = data.columns.tolist()
    logger.debug(f"Columns in the file: {file_columns}")

    missing_columns = [col for col in required_columns if col not in file_columns]
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Missing columns: {', '.join(missing_columns)}"
        )

    products_to_insert = []

    for index, row in data.iterrows():
        product_code = str(row.get("product_code"))  # Ensure product_code is a string
        client_id = row.get("client_id") if pd.notna(row.get("client_id")) else None
        weight = row.get("weight") if "weight" in row else None
        amount = row.get("amount") if "amount" in row else None
        date = row.get("date") if "date" in row else datetime.utcnow()  # Set current date if not provided
        status = ProductStatus.IN_TRANSIT  # Установите начальный статус "в пути"

        product = Product(
            product_code=product_code,
            client_id=client_id,
            weight=weight,
            amount=amount,
            date=date,
            status=status
        )
        products_to_insert.append(product)

    try:
        if products_to_insert:
            session.add_all(products_to_insert)
            await session.commit()
    except Exception as e:
        logger.error(f"Error committing the session: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error inserting data: {e}")

    return {"status": "Успешно !", "inserted": len(products_to_insert)}


@router.put("/update/products")
async def update_products(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))
    except Exception as e:
        logger.error(f"Error reading the Excel file: {e}")
        raise HTTPException(status_code=400, detail="Error reading the Excel file")

    # Проход по строкам DataFrame и обновление базы данных для каждой записи
    for _, row in df.iterrows():
        product_code = str(row['product_code'])
        weight = int(row['weight']) if pd.notna(row['weight']) else None
        amount = int(row['amount']) if pd.notna(row['amount']) else None
        client_id = row.get("client_id") if pd.notna(row.get("client_id")) else None
        
        stmt = (
            update(Product)
            .where(Product.product_code == product_code)
            .values({
                "weight": weight,
                "amount": amount,
                "status": ProductStatus.IN_WAREHOUSE,  # Установите статус "на складе"
                "date": datetime.utcnow(),  # current date
                "client_id": client_id
            })
        )
        await session.execute(stmt)
    
    # Подтверждение транзакции
    await session.commit()
    
    return {"status": "Товары обновлены"}



@router.put("/update/products/taken")
async def update_products(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session)
):
    # Чтение данных из загруженного файла Excel
    df = pd.read_excel(file.file)

    # Проход по строкам DataFrame и обновление базы данных для каждой записи
    for _, row in df.iterrows():
        product_code = str(row['product_code'])
        weight = int(row['weight'])
        amount = int(row['amount'])
        
        stmt = (
            update(Product)
            .where(Product.product_code == product_code)
            .values({
                "weight": weight,
                "amount": amount,
                "status": "PICKED_UP",
                "date": datetime.utcnow()  
            })
        )
        await session.execute(stmt)
    
    # Подтверждение транзакции
    await session.commit()
    
    return {"status": "Товары обнолены"}

@router.get("/report/today")
async def get_daily_report(session: AsyncSession = Depends(get_async_session)):
    # Запрос списка клиентов без подгрузки их продуктов
    query = select(Client)
    result = await session.execute(query)
    clients = result.scalars().all()

    if not clients:
        raise HTTPException(status_code=404, detail="No clients found")

    # Создание словаря для хранения отчета за день
    daily_report = []

    total_amount_all_clients = 0  # Инициализация переменной для общей суммы всех клиентов
    total_clients_with_products = 0  # Инициализация переменной для общего количества клиентов с продуктами

    for client in clients:
        # Проверка наличия продукта со статусом "PICKED_UP" у клиента за текущий день
        product_query = select(Product).where(
            Product.client_id == client.id,
            Product.date == func.current_date(),
            Product.status == ProductStatus.PICKED_UP
        )
        has_picked_up_product = await session.execute(product_query)
        has_picked_up_product = has_picked_up_product.scalars().first()

        # Если у клиента нет продукта со статусом "PICKED_UP", пропускаем его
        if not has_picked_up_product:
            continue

        total_clients_with_products += 1  # Увеличиваем счетчик клиентов с продуктами

        # Вычисление общей суммы amount всех продуктов клиента со статусом "PICKED_UP" за текущий день
        total_amount_query = select(func.sum(Product.amount)).where(
            Product.client_id == client.id,
            Product.date == func.current_date(),
            Product.status == ProductStatus.PICKED_UP
        )
        total_amount_result = await session.scalar(total_amount_query)

        total_amount_all_clients += total_amount_result or 0  # Суммирование total_amount каждого клиента

        # Добавление данных клиента в отчет за день
        client_data = {
            "client_id": client.id,
            "name": client.name,
            "total_amount": total_amount_result or 0  # Если сумма равна None, присваиваем 0
        }

        daily_report.append(client_data)

    # Добавление общей суммы всех клиентов в отчет за день
    daily_report.append({"total_amount_all_clients": total_amount_all_clients})
    # Добавление общего количества клиентов с продуктами в отчет за день
    daily_report.append({"total_clients_with_products": total_clients_with_products})

    return daily_report

@router.get("/report/day")
async def get_daily_report(date: str, session: AsyncSession = Depends(get_async_session)):
    # Преобразуем строку даты в объект datetime
    try:
        selected_date = datetime.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Please use ISO format.")

    # Запрос списка клиентов без подгрузки их продуктов
    query = select(Client)
    result = await session.execute(query)
    clients = result.scalars().all()

    if not clients:
        raise HTTPException(status_code=404, detail="No clients found")

    # Создание словаря для хранения отчета за день
    daily_report = []

    total_amount_all_clients = 0  # Инициализация переменной для общей суммы всех клиентов
    total_clients_with_products = 0  # Инициализация переменной для общего количества клиентов с продуктами

    for client in clients:
        # Проверка наличия продукта со статусом "PICKED_UP" у клиента за выбранный день
        product_query = select(Product).where(
            Product.client_id == client.id,
            Product.date == selected_date,
            Product.status == ProductStatus.PICKED_UP
        )
        has_picked_up_product = await session.execute(product_query)
        has_picked_up_product = has_picked_up_product.scalars().first()

        # Если у клиента нет продукта со статусом "PICKED_UP" за выбранный день, пропускаем его
        if not has_picked_up_product:
            continue

        total_clients_with_products += 1  # Увеличиваем счетчик клиентов с продуктами

        # Вычисление общей суммы amount всех продуктов клиента со статусом "PICKED_UP" за выбранный день
        total_amount_query = select(func.sum(Product.amount)).where(
            Product.client_id == client.id,
            Product.date == selected_date,
            Product.status == ProductStatus.PICKED_UP
        )
        total_amount_result = await session.scalar(total_amount_query)

        total_amount_all_clients += total_amount_result or 0  # Суммирование total_amount каждого клиента

        # Добавление данных клиента в отчет за день
        client_data = {
            "client_id": client.id,
            "name": client.name,
            "total_amount": total_amount_result or 0  # Если сумма равна None, присваиваем 0
        }

        daily_report.append(client_data)

    # Добавление общей суммы всех клиентов в отчет за день
    daily_report.append({"total_amount_all_clients": total_amount_all_clients})
    # Добавление общего количества клиентов с продуктами в отчет за день
    daily_report.append({"total_clients_with_products": total_clients_with_products})

    return daily_report


@router.get("/report/date")
async def get_monthly_report(start_date: str, end_date: str, session: AsyncSession = Depends(get_async_session)):
    try:
        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Please use ISO format.")

    query = select(Client)
    result = await session.execute(query)
    clients = result.scalars().all()

    if not clients:
        raise HTTPException(status_code=404, detail="No clients found")

    monthly_report = []
    total_amount_all_clients = 0
    total_clients_with_products = 0

    for client in clients:
        product_query = select(Product).where(
            Product.client_id == client.id,
            Product.date >= start_date,
            Product.date <= end_date,
            Product.status == ProductStatus.PICKED_UP
        )
        has_picked_up_product = await session.execute(product_query)
        has_picked_up_product = has_picked_up_product.scalars().first()

        if not has_picked_up_product:
            continue

        total_clients_with_products += 1

        total_amount_query = select(func.sum(Product.amount)).where(
            Product.client_id == client.id,
            Product.date >= start_date,
            Product.date <= end_date,
            Product.status == ProductStatus.PICKED_UP
        )
        total_amount_result = await session.scalar(total_amount_query)
        total_amount_all_clients += total_amount_result or 0

        client_data = {
            "client_id": client.id,
            "name": client.name,
            "total_amount": total_amount_result or 0
        }
        monthly_report.append(client_data)

    monthly_report.append({"total_amount_all_clients": total_amount_all_clients})
    monthly_report.append({"total_clients_with_products": total_clients_with_products})

    return monthly_report

@router.get("/report/clients/count")
async def get_clients_count(session: AsyncSession = Depends(get_async_session)):
    query = select(func.count(Client.id))
    result = await session.scalar(query)
    return {"total_clients": result}