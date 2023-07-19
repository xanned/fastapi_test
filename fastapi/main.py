import datetime
import os
from typing import Dict

from fastapi import FastAPI
from pydantic import BaseModel, Field, RootModel
from starlette.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise

from models import TariffDB

DATABASE_URL = f"postgres://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{'postgres'}:{5432}/{os.environ['POSTGRES_DB']}"
app = FastAPI()


class CargoTariff(BaseModel):
    cargo_type: str = Field(min_length=1)
    rate: float = Field(gt=0, lt=1)


class Tariff(RootModel):
    root: Dict[datetime.date, list[CargoTariff]]


@app.get('/')
async def get_insurance(cargo_type: str, value: float, date: datetime.date = datetime.date.today()):
    obj = await TariffDB.get_or_none(date=date, cargo_type=cargo_type)
    if obj:
        return {'insurance': obj.rate * value}
    return {'error': 'Тариф не найден'}


@app.post('/tariff')
async def load_tariff(tariff: Tariff):
    tariff = tariff.root
    for date in tariff:
        for cargo in tariff.get(date):
            obj = await TariffDB.update_or_create(date=date, cargo_type=cargo.cargo_type, rate=cargo.rate)
    return JSONResponse({'message': 'Тариф загружен'})


register_tortoise(
    app,
    db_url=DATABASE_URL,
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
