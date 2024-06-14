from fastapi import FastAPI, Request, Depends, HTTPException, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging
from datetime import datetime
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_404_NOT_FOUND

from database import get_async_session
from router.model import Product, ProductStatus
from router.user.router import router as clients
from router.root.router import router as root, get_monthly_report
from router.admin.router import router as admin

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(admin)
app.include_router(clients)
app.include_router(root)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# index
@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request, session: AsyncSession = Depends(get_async_session)):
    query = select(Product)
    result = await session.execute(query)
    products = result.scalars().all()
    total_amount = sum(product.amount if product.amount is not None else 0 for product in products)
    total_weight_kg = sum(product.weight if product.weight is not None else 0 for product in products) / 1000  # Преобразуем вес в кг
    return templates.TemplateResponse("index.html", {"request": request, "products": products, "title": "Главная", "total_amount": total_amount, "total_weight_kg": total_weight_kg})

# register
@app.get("/registration", response_class=HTMLResponse)
async def register_client_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "Регистрация клиента"})

# report
@app.get("/reports")
async def show_reports(request: Request, start_date: str = Query(None), end_date: str = Query(None), session: AsyncSession = Depends(get_async_session)):
    report_data = []
    if start_date and end_date:
        report_data = await get_monthly_report(start_date, end_date, session)
    return templates.TemplateResponse("report.html", {"request": request, "report_data": report_data, "start_date": start_date, "end_date": end_date,  "title": "Отчет"})

# china 
@app.get("/china")
async def china_upload_form(request: Request):
    return templates.TemplateResponse("china.html", {"request": request, "title": "Китай"})

# bishkek
@app.get("/bishkek")
async def bishkek_upload_form(request: Request):
    return templates.TemplateResponse("bishkek.html", {"request": request, "title": "Бишкек"})

# search
@app.get("/search")
async def take_products(request: Request):
    return templates.TemplateResponse("take.html", {"request": request, "title": "Выдать"})

from pydantic import BaseModel
from typing import List

class UpdateProductStatusRequest(BaseModel):
    product_ids: List[int]

@app.post("/api/v1/routes/update-status")
async def update_product_status(
    request: UpdateProductStatusRequest,
    session: AsyncSession = Depends(get_async_session)
):
    product_ids = request.product_ids
    if not product_ids:
        raise HTTPException(status_code=400, detail="No product IDs provided")

    query = select(Product).where(Product.id.in_(product_ids))
    result = await session.execute(query)
    products = result.scalars().all()

    if not products:
        raise HTTPException(status_code=404, detail="Products not found")

    for product in products:
        product.status = ProductStatus.PICKED_UP
        product.date = datetime.utcnow()

    await session.commit()

    return {"message": "Product statuses updated successfully"}

# 404 page
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == HTTP_404_NOT_FOUND:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=HTTP_404_NOT_FOUND)
    return HTMLResponse(str(exc.detail), status_code=exc.status_code)
