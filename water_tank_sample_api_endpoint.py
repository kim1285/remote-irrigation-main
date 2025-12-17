from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.PreWaterTankUseCase import GetPreTankWaterLevelByIdUseCase
from src.application.ValveUseCase import GetValveStatusByIdUseCase, OpenValveByIdUseCase, CloseValveByIdUseCase
from src.application.WaterPumpUseCase import GetPumpStatusByIdUseCase, TurnOnWaterPumpByIdUseCase, \
    TurnOffWaterPumpByIdUseCase
from src.application.auth_usecase import AuthUseCase
from src.application.services.water_tank_application_service import WaterTankApplicationService
from src.infrastructure.db.repository.sqlalchemy_esp32_device_manager_repository import (
    SQLAlchemyESP32DeviceManagerRepository)
from src.infrastructure.db.repository.sqlalchemy_pre_water_tank_repository import SQLAlchemyPreWaterTankRepository
from src.infrastructure.db.repository.sqlalchemy_valve_repository import SQLAlchemyValveRepository
from src.infrastructure.db.repository.sqlalchemy_water_pump_repository import SQLAlchemyWaterPumpRepository
from src.infrastructure.db.repository.sqlalchemy_water_tank_repository import SQLAlchemyWaterTankRepository
from src.schemas.http.v1.water_tanks import StartOnlyFillRequest, StartOnlyFillResponse, StartOnlyDrainResponse, \
    StartOnlyDrainRequest, StartOnlyIdleResponse, StartOnlyIdleRequest, StartFillAndDrainResponse, \
    StartFillAndDrainRequest, GetWaterTankStatusRequest, GetWaterTankStatusResponse, GetAllTanksByUserIdResponse
from src.application.services.token_service import TokenService, get_token_service
from src.application.services.http_bearer_service import bearer_scheme  # get token from HTTP request header
from src.infrastructure.db.db_async.session import get_db_session
from src.infrastructure.mqtt.mqtt_publisher import get_publisher, MQTTPublisher
from src.infrastructure.mqtt.app_status import get_app_status, AppStatus

router = APIRouter(prefix='/water_tanks', tags=['water_tanks'])


@router.post('/get-water-tank-status',
             status_code=status.HTTP_200_OK,
             response_model=GetWaterTankStatusResponse,
             description="Get water tank status."
             )
async def get_water_tank_status(request_model: GetWaterTankStatusRequest,
                                token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                                token_service: TokenService = Depends(get_token_service),
                                db_session: AsyncSession = Depends(get_db_session),
                                app_status: AppStatus = Depends(get_app_status),
                                publisher: MQTTPublisher = Depends(get_publisher)
                                ):
    try:
        async with db_session.begin():
            # auth
            auth_uc = AuthUseCase(token_service)
            user_id = auth_uc.auth_user(token)
            # id
            wt_id = request_model.water_tank_id
            # DI
            dvmg_db_repo = SQLAlchemyESP32DeviceManagerRepository(db_session)
            pump_db_repo = SQLAlchemyWaterPumpRepository(db_session)
            valve_db_repo = SQLAlchemyValveRepository(db_session)
            pre_tank_db_repo = SQLAlchemyPreWaterTankRepository(db_session)
            water_tank_db_repo = SQLAlchemyWaterTankRepository(db_session)

            gt_vl_st_by_id_uc = GetValveStatusByIdUseCase(valve_db_repo,
                                                          dvmg_db_repo,
                                                          publisher,
                                                          app_status
                                                          )
            op_vl_by_id_uc = OpenValveByIdUseCase(valve_db_repo,
                                                  dvmg_db_repo,
                                                  publisher,
                                                  app_status
                                                  )
            cl_vl_by_id_uc = CloseValveByIdUseCase(valve_db_repo,
                                                   dvmg_db_repo,
                                                   publisher,
                                                   app_status
                                                   )
            gt_pu_st_by_id_uc = GetPumpStatusByIdUseCase(pump_db_repo,
                                                         dvmg_db_repo,
                                                         publisher,
                                                         app_status
                                                         )
            tu_on_wp_by_id_uc = TurnOnWaterPumpByIdUseCase(pump_db_repo,
                                                           dvmg_db_repo,
                                                           publisher,
                                                           app_status
                                                           )
            tu_off_wp_by_id_uc = TurnOffWaterPumpByIdUseCase(pump_db_repo,
                                                             dvmg_db_repo,
                                                             publisher,
                                                             app_status
                                                             )
            gt_p_wt_wl_by_id_uc = GetPreTankWaterLevelByIdUseCase(pre_tank_db_repo,
                                                                  dvmg_db_repo,
                                                                  publisher,
                                                                  app_status
                                                                  )
            wt_app_sr = WaterTankApplicationService(gt_vl_st_by_id_uc,
                                                    op_vl_by_id_uc,
                                                    cl_vl_by_id_uc,
                                                    gt_pu_st_by_id_uc,
                                                    tu_on_wp_by_id_uc,
                                                    tu_off_wp_by_id_uc,
                                                    gt_p_wt_wl_by_id_uc,
                                                    water_tank_db_repo,
                                                    pre_tank_db_repo,
                                                    pump_db_repo,
                                                    valve_db_repo
                                                    )
            wt_st_dto = await wt_app_sr.get_water_tank_status(wt_id, user_id)
            return GetWaterTankStatusResponse(**wt_st_dto.dict())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/start-only-fill',
             status_code=status.HTTP_200_OK,
             response_model=StartOnlyFillResponse,
             description="Start only filling water tank."
             )
async def start_only_fill(request_model: StartOnlyFillRequest,
                          db_session: AsyncSession = Depends(get_db_session),
                          token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                          token_service: TokenService = Depends(get_token_service),
                          app_status: AppStatus = Depends(get_app_status),
                          publisher: MQTTPublisher = Depends(get_publisher)
                          ):
    try:
        async with db_session.begin():
            # auth
            auth_uc = AuthUseCase(token_service)
            user_id = auth_uc.auth_user(token)
            # id
            wt_id = request_model.water_tank_id
            # DI
            dvmg_db_repo = SQLAlchemyESP32DeviceManagerRepository(db_session)
            pump_db_repo = SQLAlchemyWaterPumpRepository(db_session)
            valve_db_repo = SQLAlchemyValveRepository(db_session)
            pre_tank_db_repo = SQLAlchemyPreWaterTankRepository(db_session)
            water_tank_db_repo = SQLAlchemyWaterTankRepository(db_session)

            gt_vl_st_by_id_uc = GetValveStatusByIdUseCase(valve_db_repo,
                                                          dvmg_db_repo,
                                                          publisher,
                                                          app_status
                                                          )
            op_vl_by_id_uc = OpenValveByIdUseCase(valve_db_repo,
                                                  dvmg_db_repo,
                                                  publisher,
                                                  app_status
                                                  )
            cl_vl_by_id_uc = CloseValveByIdUseCase(valve_db_repo,
                                                   dvmg_db_repo,
                                                   publisher,
                                                   app_status
                                                   )
            gt_pu_st_by_id_uc = GetPumpStatusByIdUseCase(pump_db_repo,
                                                         dvmg_db_repo,
                                                         publisher,
                                                         app_status
                                                         )
            tu_on_wp_by_id_uc = TurnOnWaterPumpByIdUseCase(pump_db_repo,
                                                           dvmg_db_repo,
                                                           publisher,
                                                           app_status
                                                           )
            tu_off_wp_by_id_uc = TurnOffWaterPumpByIdUseCase(pump_db_repo,
                                                             dvmg_db_repo,
                                                             publisher,
                                                             app_status
                                                             )
            gt_p_wt_wl_by_id_uc = GetPreTankWaterLevelByIdUseCase(pre_tank_db_repo,
                                                                  dvmg_db_repo,
                                                                  publisher,
                                                                  app_status
                                                                  )
            wt_app_sr = WaterTankApplicationService(gt_vl_st_by_id_uc,
                                                    op_vl_by_id_uc,
                                                    cl_vl_by_id_uc,
                                                    gt_pu_st_by_id_uc,
                                                    tu_on_wp_by_id_uc,
                                                    tu_off_wp_by_id_uc,
                                                    gt_p_wt_wl_by_id_uc,
                                                    water_tank_db_repo,
                                                    pre_tank_db_repo,
                                                    pump_db_repo,
                                                    valve_db_repo
                                                    )
            wt_st_dto = await wt_app_sr.start_only_fill(wt_id, user_id)
            return StartOnlyFillResponse(**wt_st_dto.dict())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/start-only-drain',
             status_code=status.HTTP_200_OK,
             response_model=StartOnlyDrainResponse,
             description="Start only draining water tank."
             )
async def start_only_drain(request_model: StartOnlyDrainRequest,
                           db_session: AsyncSession = Depends(get_db_session),
                           token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                           token_service: TokenService = Depends(get_token_service),
                           app_status: AppStatus = Depends(get_app_status),
                           publisher: MQTTPublisher = Depends(get_publisher)):
    try:
        async with db_session.begin():
            # auth
            auth_uc = AuthUseCase(token_service)
            user_id = auth_uc.auth_user(token)
            # id
            wt_id = request_model.water_tank_id
            # DI
            dvmg_db_repo = SQLAlchemyESP32DeviceManagerRepository(db_session)
            pump_db_repo = SQLAlchemyWaterPumpRepository(db_session)
            valve_db_repo = SQLAlchemyValveRepository(db_session)
            pre_tank_db_repo = SQLAlchemyPreWaterTankRepository(db_session)
            water_tank_db_repo = SQLAlchemyWaterTankRepository(db_session)

            gt_vl_st_by_id_uc = GetValveStatusByIdUseCase(valve_db_repo,
                                                          dvmg_db_repo,
                                                          publisher,
                                                          app_status
                                                          )
            op_vl_by_id_uc = OpenValveByIdUseCase(valve_db_repo,
                                                  dvmg_db_repo,
                                                  publisher,
                                                  app_status
                                                  )
            cl_vl_by_id_uc = CloseValveByIdUseCase(valve_db_repo,
                                                   dvmg_db_repo,
                                                   publisher,
                                                   app_status
                                                   )
            gt_pu_st_by_id_uc = GetPumpStatusByIdUseCase(pump_db_repo,
                                                         dvmg_db_repo,
                                                         publisher,
                                                         app_status
                                                         )
            tu_on_wp_by_id_uc = TurnOnWaterPumpByIdUseCase(pump_db_repo,
                                                           dvmg_db_repo,
                                                           publisher,
                                                           app_status
                                                           )
            tu_off_wp_by_id_uc = TurnOffWaterPumpByIdUseCase(pump_db_repo,
                                                             dvmg_db_repo,
                                                             publisher,
                                                             app_status
                                                             )
            gt_p_wt_wl_by_id_uc = GetPreTankWaterLevelByIdUseCase(pre_tank_db_repo,
                                                                  dvmg_db_repo,
                                                                  publisher,
                                                                  app_status
                                                                  )
            wt_app_sr = WaterTankApplicationService(gt_vl_st_by_id_uc,
                                                    op_vl_by_id_uc,
                                                    cl_vl_by_id_uc,
                                                    gt_pu_st_by_id_uc,
                                                    tu_on_wp_by_id_uc,
                                                    tu_off_wp_by_id_uc,
                                                    gt_p_wt_wl_by_id_uc,
                                                    water_tank_db_repo,
                                                    pre_tank_db_repo,
                                                    pump_db_repo,
                                                    valve_db_repo
                                                    )
            wt_st_dto = await wt_app_sr.start_only_drain(wt_id, user_id)
            return StartOnlyDrainResponse(**wt_st_dto.dict())

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/start-only-idle',
             status_code=status.HTTP_200_OK,
             response_model=StartOnlyIdleResponse,
             description="Start only idling water tank."
             )
async def start_only_idle(request_model: StartOnlyIdleRequest,
                          db_session: AsyncSession = Depends(get_db_session),
                          token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                          token_service: TokenService = Depends(get_token_service),
                          app_status: AppStatus = Depends(get_app_status),
                          publisher: MQTTPublisher = Depends(get_publisher)):
    try:
        async with db_session.begin():
            # auth
            auth_uc = AuthUseCase(token_service)
            user_id = auth_uc.auth_user(token)
            # id
            wt_id = request_model.water_tank_id
            # DI
            dvmg_db_repo = SQLAlchemyESP32DeviceManagerRepository(db_session)
            pump_db_repo = SQLAlchemyWaterPumpRepository(db_session)
            valve_db_repo = SQLAlchemyValveRepository(db_session)
            pre_tank_db_repo = SQLAlchemyPreWaterTankRepository(db_session)
            water_tank_db_repo = SQLAlchemyWaterTankRepository(db_session)

            gt_vl_st_by_id_uc = GetValveStatusByIdUseCase(valve_db_repo,
                                                          dvmg_db_repo,
                                                          publisher,
                                                          app_status
                                                          )
            op_vl_by_id_uc = OpenValveByIdUseCase(valve_db_repo,
                                                  dvmg_db_repo,
                                                  publisher,
                                                  app_status
                                                  )
            cl_vl_by_id_uc = CloseValveByIdUseCase(valve_db_repo,
                                                   dvmg_db_repo,
                                                   publisher,
                                                   app_status
                                                   )
            gt_pu_st_by_id_uc = GetPumpStatusByIdUseCase(pump_db_repo,
                                                         dvmg_db_repo,
                                                         publisher,
                                                         app_status
                                                         )
            tu_on_wp_by_id_uc = TurnOnWaterPumpByIdUseCase(pump_db_repo,
                                                           dvmg_db_repo,
                                                           publisher,
                                                           app_status
                                                           )
            tu_off_wp_by_id_uc = TurnOffWaterPumpByIdUseCase(pump_db_repo,
                                                             dvmg_db_repo,
                                                             publisher,
                                                             app_status
                                                             )
            gt_p_wt_wl_by_id_uc = GetPreTankWaterLevelByIdUseCase(pre_tank_db_repo,
                                                                  dvmg_db_repo,
                                                                  publisher,
                                                                  app_status
                                                                  )
            wt_app_sr = WaterTankApplicationService(gt_vl_st_by_id_uc,
                                                    op_vl_by_id_uc,
                                                    cl_vl_by_id_uc,
                                                    gt_pu_st_by_id_uc,
                                                    tu_on_wp_by_id_uc,
                                                    tu_off_wp_by_id_uc,
                                                    gt_p_wt_wl_by_id_uc,
                                                    water_tank_db_repo,
                                                    pre_tank_db_repo,
                                                    pump_db_repo,
                                                    valve_db_repo
                                                    )
            wt_st_dto = await wt_app_sr.start_only_idle(wt_id, user_id)
            return StartOnlyIdleResponse(**wt_st_dto.dict())

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/start-fill-and-drain',
             status_code=status.HTTP_200_OK,
             response_model=StartFillAndDrainResponse,
             description="Start filling and draining water tank."
             )
async def start_fill_and_drain(request_model: StartFillAndDrainRequest,
                               db_session: AsyncSession = Depends(get_db_session),
                               token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                               token_service: TokenService = Depends(get_token_service),
                               app_status: AppStatus = Depends(get_app_status),
                               publisher: MQTTPublisher = Depends(get_publisher)):
    try:
        async with db_session.begin():
            # auth
            auth_uc = AuthUseCase(token_service)
            user_id = auth_uc.auth_user(token)
            # id
            wt_id = request_model.water_tank_id
            # DI
            dvmg_db_repo = SQLAlchemyESP32DeviceManagerRepository(db_session)
            pump_db_repo = SQLAlchemyWaterPumpRepository(db_session)
            valve_db_repo = SQLAlchemyValveRepository(db_session)
            pre_tank_db_repo = SQLAlchemyPreWaterTankRepository(db_session)
            water_tank_db_repo = SQLAlchemyWaterTankRepository(db_session)

            gt_vl_st_by_id_uc = GetValveStatusByIdUseCase(valve_db_repo,
                                                          dvmg_db_repo,
                                                          publisher,
                                                          app_status
                                                          )
            op_vl_by_id_uc = OpenValveByIdUseCase(valve_db_repo,
                                                  dvmg_db_repo,
                                                  publisher,
                                                  app_status
                                                  )
            cl_vl_by_id_uc = CloseValveByIdUseCase(valve_db_repo,
                                                   dvmg_db_repo,
                                                   publisher,
                                                   app_status
                                                   )
            gt_pu_st_by_id_uc = GetPumpStatusByIdUseCase(pump_db_repo,
                                                         dvmg_db_repo,
                                                         publisher,
                                                         app_status
                                                         )
            tu_on_wp_by_id_uc = TurnOnWaterPumpByIdUseCase(pump_db_repo,
                                                           dvmg_db_repo,
                                                           publisher,
                                                           app_status
                                                           )
            tu_off_wp_by_id_uc = TurnOffWaterPumpByIdUseCase(pump_db_repo,
                                                             dvmg_db_repo,
                                                             publisher,
                                                             app_status
                                                             )
            gt_p_wt_wl_by_id_uc = GetPreTankWaterLevelByIdUseCase(pre_tank_db_repo,
                                                                  dvmg_db_repo,
                                                                  publisher,
                                                                  app_status
                                                                  )
            wt_app_sr = WaterTankApplicationService(gt_vl_st_by_id_uc,
                                                    op_vl_by_id_uc,
                                                    cl_vl_by_id_uc,
                                                    gt_pu_st_by_id_uc,
                                                    tu_on_wp_by_id_uc,
                                                    tu_off_wp_by_id_uc,
                                                    gt_p_wt_wl_by_id_uc,
                                                    water_tank_db_repo,
                                                    pre_tank_db_repo,
                                                    pump_db_repo,
                                                    valve_db_repo
                                                    )
            wt_st_dto = await wt_app_sr.start_fill_and_drain(wt_id, user_id)
            return StartFillAndDrainResponse(**wt_st_dto.dict())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/read_tanks_all",
            response_model=GetAllTanksByUserIdResponse,
            description="Get all the tanks a user has.",
            status_code=status.HTTP_200_OK
            )
async def read_all_tanks(db_session: AsyncSession = Depends(get_db_session),
                         token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
                         token_service: TokenService = Depends(get_token_service),
                         app_status: AppStatus = Depends(get_app_status),
                         publisher: MQTTPublisher = Depends(get_publisher)
                         ):
    try:
        async with db_session.begin():
            # auth
            auth_uc = AuthUseCase(token_service)
            user_id = auth_uc.auth_user(token)

            # DI
            dvmg_db_repo = SQLAlchemyESP32DeviceManagerRepository(db_session)
            pump_db_repo = SQLAlchemyWaterPumpRepository(db_session)
            valve_db_repo = SQLAlchemyValveRepository(db_session)
            pre_tank_db_repo = SQLAlchemyPreWaterTankRepository(db_session)
            water_tank_db_repo = SQLAlchemyWaterTankRepository(db_session)

            gt_vl_st_by_id_uc = GetValveStatusByIdUseCase(valve_db_repo,
                                                          dvmg_db_repo,
                                                          publisher,
                                                          app_status
                                                          )
            op_vl_by_id_uc = OpenValveByIdUseCase(valve_db_repo,
                                                  dvmg_db_repo,
                                                  publisher,
                                                  app_status
                                                  )
            cl_vl_by_id_uc = CloseValveByIdUseCase(valve_db_repo,
                                                   dvmg_db_repo,
                                                   publisher,
                                                   app_status
                                                   )
            gt_pu_st_by_id_uc = GetPumpStatusByIdUseCase(pump_db_repo,
                                                         dvmg_db_repo,
                                                         publisher,
                                                         app_status
                                                         )
            tu_on_wp_by_id_uc = TurnOnWaterPumpByIdUseCase(pump_db_repo,
                                                           dvmg_db_repo,
                                                           publisher,
                                                           app_status
                                                           )
            tu_off_wp_by_id_uc = TurnOffWaterPumpByIdUseCase(pump_db_repo,
                                                             dvmg_db_repo,
                                                             publisher,
                                                             app_status
                                                             )
            gt_p_wt_wl_by_id_uc = GetPreTankWaterLevelByIdUseCase(pre_tank_db_repo,
                                                                  dvmg_db_repo,
                                                                  publisher,
                                                                  app_status
                                                                  )
            wt_app_sr = WaterTankApplicationService(gt_vl_st_by_id_uc,
                                                    op_vl_by_id_uc,
                                                    cl_vl_by_id_uc,
                                                    gt_pu_st_by_id_uc,
                                                    tu_on_wp_by_id_uc,
                                                    tu_off_wp_by_id_uc,
                                                    gt_p_wt_wl_by_id_uc,
                                                    water_tank_db_repo,
                                                    pre_tank_db_repo,
                                                    pump_db_repo,
                                                    valve_db_repo
                                                    )

            wt_st_dto_tuple = await wt_app_sr.get_all_tank_status_by_owner_id(user_id)

            return GetAllTanksByUserIdResponse(water_tank_status_list=
                                               [
                                                   GetWaterTankStatusResponse(
                                                       timestamp=wt_st_dto.timestamp,
                                                       water_tank_id=wt_st_dto.water_tank_id,
                                                       water_tank_status=wt_st_dto.water_tank_status,
                                                       water_level=wt_st_dto.water_level
                                                   )
                                                   for wt_st_dto in wt_st_dto_tuple
                                               ]
                                               )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}")
