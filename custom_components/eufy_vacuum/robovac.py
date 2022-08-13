# -*- coding: utf-8 -*-

# Copyright 2019 Richard Mitchell
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import base64
import json
import time

from .property import DeviceProperty, StringEnum
from .tuya import TuyaDevice


_LOGGER = logging.getLogger(__name__)


class WorkMode(StringEnum):
    AUTO = 'auto'
    NO_SWEEP = 'Nosweep'
    SMALL_ROOM = 'SmallRoom'
    EDGE = 'Edge'
    SPOT = 'Spot'
    ROOM = 'room'

class Direction(StringEnum):
    LEFT = 'left'
    RIGHT = 'right'
    FORWARD = 'forward'
    BACKWARD = 'backward'


class WorkStatus(StringEnum):
    # Cleaning
    RUNNING = 'Running'
    # In the dock, charging
    CHARGING = 'Charging'
    # Not in the dock, paused
    STAND_BY = 'standby'
    # Not in the dock - goes into this state after being paused for a while
    SLEEPING = 'Sleeping'
    # Going home because battery is depleted
    RECHARGE_NEEDED = 'Recharge'
    # In the dock, full charged
    COMPLETED = 'completed'


class CleanSpeed(StringEnum):
    NO_SUCTION = 'No_suction'
    STANDARD = 'Standard'
    BOOST_IQ = 'Boost_IQ'
    MAX = 'Max'


class ErrorCode(StringEnum):
    NO_ERROR = 'no_error'
    WHEEL_STUCK = 'Wheel_stuck'
    R_BRUSH_STUCK = 'R_brush_stuck'
    CRASH_BAR_STUCK = 'Crash_bar_stuck'
    SENSOR_DIRTY = 'sensor_dirty'
    NOT_ENOUGH_POWER = 'N_enough_pow'
    STUCK_5_MIN = 'Stuck_5_min'
    FAN_STUCK = 'Fan_stuck'
    S_BRUSH_STUCK = 'S_brush_stuck'


def current_milli_time():
    return round(time.time() * 1000)

class Robovac(TuyaDevice):
    """Represents a generic Eufy Robovac."""

    POWER = '1'
    PLAY_PAUSE = '2'
    DIRECTION = '3'
    WORK_MODE = '5'
    WORK_STATUS = '15'
    GO_HOME = '101'
    CLEAN_SPEED = '102'
    FIND_ROBOT = '103'
    BATTERY_LEVEL = '104'
    ERROR_CODE = '106'
    GET_MAP_DATA = '121'
    CALL_METHOD = '124'
    MANUAL_CONTROL = '131'

    power = DeviceProperty(POWER)
    play_pause = DeviceProperty(PLAY_PAUSE)
    direction = DeviceProperty(DIRECTION)
    work_mode = DeviceProperty(WORK_MODE, WorkMode)
    work_status = DeviceProperty(WORK_STATUS, WorkStatus, True)
    go_home = DeviceProperty(GO_HOME)
    clean_speed = DeviceProperty(CLEAN_SPEED, CleanSpeed)
    find_robot = DeviceProperty(FIND_ROBOT)
    battery_level = DeviceProperty(BATTERY_LEVEL, read_only=True)
    error_code = DeviceProperty(ERROR_CODE, ErrorCode, True)
    manual_control = DeviceProperty(MANUAL_CONTROL)

    async def async_play(self, callback=None):
        await self.async_set({self.PLAY_PAUSE: True}, callback)

    async def async_pause(self, callback=None):
        await self.async_set({self.PLAY_PAUSE: False}, callback)

    async def async_start_cleaning(self, callback=None):
        await self.async_set({self.WORK_MODE: str(WorkMode.AUTO)}, callback)

    async def async_go_home(self, callback=None):
        await self.async_set({self.GO_HOME: True}, callback)

    async def async_set_work_mode(self, work_mode, callback=None):
        await self.async_set({self.WORK_MODE: str(work_mode)}, callback)

    async def async_find_robot(self, callback=None):
        await self.async_set({self.FIND_ROBOT: True}, callback)

    async def async_set_clean_speed(self, clean_speed, callback=None):
        await self.async_set({self.CLEAN_SPEED: str(clean_speed)}, callback)

    async def async_get_map_data(self, callback=None):
        map_request = { "type" : "mapData", "id" : self.device_id, "timestamp" : current_milli_time() }
        json_str = json.dumps(map_request, separators=(',',':'))
        base64_str = base64.b64encode(json_str.encode("utf8")).decode("utf8")
        await self.async_set({self.GET_MAP_DATA : base64_str}, callback)
    
    async def async_invoke_method(self, method, data, callback=None):
        method_call = { "method" : method, "data" : data, "timestamp" : current_milli_time()}
        json_str = json.dumps(method_call, separators=(',',':'))
        base64_str = base64.b64encode(json_str.encode("utf8")).decode("utf8")
        await self.async_set({self.CALL_METHOD : base64_str}, callback)

    async def async_clean_rooms(self, room_list, count=1, callback=None):
        clean_request = { "roomIds" : room_list, "cleanTimes" : count }
        await self.async_invoke_method("selectRoomsClean", clean_request)
        
    async def async_clean_spot(self, x, y, count = 1, callback=None):
        spot_clean_request = { "target" : "spot", "cleanTimes" : count, "x" : x, "y" : x }
        await self.async_invoke_method("goto", spot_clean_request)

    async def async_clean_zone(self, zone_points_list, count = 1, callback=None):
        zone_data_list_to_send = []
        id = 128
        for zone_points in zone_points_list:
            zone_request = { "cleanTimes:" : count, "type" : "sweep", "id" : id, "name" : ""}
            zone_request.update(zone_points)
            zone_data_list_to_send.append(zone_request)
            id = id + 1

        zone_clean_request = {"zones" : zone_data_list_to_send }
        await self.async_invoke_method("selectZonesClean", zone_clean_request)

        