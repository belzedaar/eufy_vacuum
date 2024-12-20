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

import asyncio
import logging
import pprint
import sys

from eufy_vacuum.robovac import Robovac


logging.basicConfig(level=logging.DEBUG)


async def connected_callback(message, device):
    print("Connected. Current device state:")
    pprint.pprint(device.state)


async def cleaning_started_callback(message, device):
    print("Cleaning started.")

async def clean_callback(message, device):
    print("Clean!")
    print(message)
    
    

async def async_main(device_id, ip, local_key=None, *args, **kwargs):
    r = Robovac(device_id, ip, local_key, *args, **kwargs)

    await r.async_connect(connected_callback)

    await asyncio.sleep(1)

    #await r.async_get_map_data(clean_callback)
    #await r.async_clean_rooms([2], 1, clean_callback)
    
    zone_list = [{"x0":-2702,"y0":-388,"x1":188,"y1":-388,"x2":188,"y2":-3369,"x3":-2702,"y3":-3369}]
    
    await r.async_clean_zone(zone_list, 1)
    await asyncio.sleep(5)

    print("Disconnecting...")
    await r.async_disconnect()


def main(*args, **kwargs):
    if not args:
        args = sys.argv[1:]
    asyncio.run(async_main(*args, **kwargs))
    

if __name__ == '__main__':
    main(*sys.argv[1:])
