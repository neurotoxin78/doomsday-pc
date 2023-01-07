#!/usr/bin/env python3
import asyncio
from evdev import InputDevice, categorize, ecodes


dev = InputDevice('/dev/input/event5')

async def helper(dev):
    async for ev in dev.async_read_loop():
        #print(ev.value)
        if ev.value == 1:
            print(">")
        elif ev.value == -1:
            print("<")
        else:
            pass
def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(helper(dev))

if __name__ == '__main__':
    main()
