from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from src.domain.interfaces.water_tank_repo import WaterTankRepository
from src.domain.model.water_tank import WaterTank
from src.infrastructure.db.models.water_tank import WaterTankModel
from src.infrastructure.db.mappers.water_tank_mapper import to_orm, to_domain
from typing import List


class SQLAlchemyWaterTankRepository(WaterTankRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, water_tank: WaterTank):
        wt_orm = to_orm(water_tank)
        self.session.add(wt_orm)

    async def get_by_id(self, water_tank_id: str) -> WaterTank:
        stmt = select(WaterTankModel).where(WaterTankModel.id == water_tank_id)
        result = await self.session.execute(stmt)
        result = result.scalar_one_or_none()
        if result is not None:
            wt_domain = to_domain(result)
            return wt_domain
        else:
            raise Exception("Water Tank with given id not found.")

    async def update_status(self, water_tank: WaterTank):
        # updates water level, status
        stmt = (update(WaterTankModel).where(WaterTankModel.id == water_tank.id)
                .values(water_level=water_tank.water_level, status=water_tank.status))
        result = await self.session.execute(stmt)
        result = result.rowcount
        if result != 1:
            raise Exception("Water Tank status in db not updated.")

    async def remove_by_id(self, water_tank_id: str):
        pass

    async def get_all_by_owner(self, owner_id: str) -> List[WaterTank]:
        stmt = select(WaterTankModel).where(WaterTankModel.owner_id == owner_id)
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        wt_dom_list = [to_domain(wt_orm) for wt_orm in rows if wt_orm]
        return wt_dom_list
