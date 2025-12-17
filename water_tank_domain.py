from dataclasses import dataclass
from typing import List


@dataclass(frozen=False)
class WaterTankDeviceActionSet:
    open_valve_ids: List[str]
    close_valve_ids: List[str]
    start_pump_ids: List[str]
    stop_pump_ids: List[str]


@dataclass(frozen=False)
class WaterTankConnectedDevices:
    connected_valve_ids: List[str]
    connected_pump_ids: List[str]
    connected_pre_tank_ids: List[str]


class WaterTank:
    def __init__(self,
                 id: str,
                 owner_id: str,
                 connected_hub_id: str,
                 _pre_tank_id: str,
                 _only_idle: WaterTankDeviceActionSet,
                 _only_filling: WaterTankDeviceActionSet,
                 _only_draining: WaterTankDeviceActionSet,
                 _filling_and_draining: WaterTankDeviceActionSet,
                 water_level: float = 0.0,
                 status: str = None,
                 provision_status: bool = False,
                 ):
        self.id = id
        self.owner_id = owner_id
        self.connected_hub_id = connected_hub_id
        self.water_level = water_level
        self._pre_tank_id = _pre_tank_id
        self._only_idle = _only_idle
        self._only_filling = _only_filling
        self._only_draining = _only_draining
        self._filling_and_draining = _filling_and_draining
        self.status = status
        self.provision_status = provision_status

    async def get_current_status(self):
        return self.status

    async def get_water_level(self):
        return self.water_level

    async def start_only_idle(self):
        pass

    async def start_only_filling(self):
        pass

    async def start_only_draining(self):
        pass

    async def start_filling_and_draining(self):
        pass

    async def get_connected_devices(self) -> WaterTankConnectedDevices:
        # get unique device ids per _state:WaterTankDeviceActionSet
        def wt_dv_act_set_id_getter(water_tank_device_action_set: WaterTankDeviceActionSet):
            # this does not get pre tank.
            valve_ids_list = []
            pump_ids_list = []

            # pass generator obj directly to .extend list obj method
            valve_ids_list.extend(v_id for v_id in water_tank_device_action_set.close_valve_ids)
            valve_ids_list.extend(v_id for v_id in water_tank_device_action_set.open_valve_ids)
            pump_ids_list.extend(p_id for p_id in water_tank_device_action_set.stop_pump_ids)
            pump_ids_list.extend(p_id for p_id in water_tank_device_action_set.start_pump_ids)

            valve_ids_set = set(valve_ids_list)
            pump_ids_set = set(pump_ids_list)

            return valve_ids_set, pump_ids_set

        # final list with still duplicates inside.
        val_id_outer_lst = []
        pum_id_outer_lst = []

        vals_tmp, pumps_tmp = wt_dv_act_set_id_getter(self._only_idle)
        val_id_outer_lst.extend(vals_tmp)
        pum_id_outer_lst.extend(pumps_tmp)

        vals_tmp, pumps_tmp = wt_dv_act_set_id_getter(self._only_filling)
        val_id_outer_lst.extend(vals_tmp)
        pum_id_outer_lst.extend(pumps_tmp)

        vals_tmp, pumps_tmp = wt_dv_act_set_id_getter(self._only_draining)
        val_id_outer_lst.extend(vals_tmp)
        pum_id_outer_lst.extend(pumps_tmp)

        vals_tmp, pumps_tmp = wt_dv_act_set_id_getter(self._filling_and_draining)
        val_id_outer_lst.extend(vals_tmp)
        pum_id_outer_lst.extend(pumps_tmp)

        # final list with unique ids
        valve_ids_list = list(set(val_id_outer_lst))
        pump_ids_list = list(set(pum_id_outer_lst))
        pre_tank_ids_list = [self._pre_tank_id]

        # create and return dataclass
        wt_conn_dvs = WaterTankConnectedDevices(connected_pump_ids=pump_ids_list,
                                                connected_valve_ids=valve_ids_list,
                                                connected_pre_tank_ids=pre_tank_ids_list
                                                )

        return wt_conn_dvs
