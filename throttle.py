import asyncio
from datetime import datetime, timedelta
from functools import partial
import math

class FuelTank(object):
    def __init__(self, volume = None, quota=1, unit="seconds", loop=None):

        # Burst rate
        self.volume = volume

        # Number of tokens per delta
        self.quota = quota

        # Tokens consumed in this delta
        self.consumed = 0

        # Time till tank refueled
        self.delta = timedelta(**{unit: quota})

        # Last time the tank was refueled
        self.last_refuel = datetime.utcnow()

        # The event loop
        self.loop = loop if loop else asyncio.get_event_loop()

    @property
    def level(self):
        return self.quota - self.consumed

    @level.setter #lol
    def level(self,value):
        self.consumed = this.quota - value

    @asyncio.coroutine
    def burn(self,fuel,fn):
        # If the tank has unlimited volume, who cares how much we burn?
        # The EPA, that's who!
        if not self.volume:
            return self.loop.call_soon(destination)

        if fuel > self.volume:
            raise Exception('Not enough fuel: Requested fuel, %d, exceeds tank volume, %d' % (fuel,self.volume))

        self.refuel()

        if fuel > self.level:
            return defer();

        self.consumed += 1
        return self.loop.call_soon(fn)

        def defer():
            delay = math.ceil((fuel - self.level) * (self.delta / self.quota))
            return self.loop.call_later(delay,self.burn(fuel,fn))

    def refuel(self):
        if not self.quota:
            self.consumed = 0
        else:
            now = datetime.utcnow()
            current_delta = max(now - self.last_refuel,timedelta(seconds=0))
            self.last_drip = now

            fuel = current_delta/self.delta * (self.quota)
            self.level = min(self.level + fuel, self.volume)

class Governor(FuelTank):
    """
        Like a fuel tank, but with the concept of time, measured via odometer.
        Sure, an odometer displays a distance, but if time is money, knowledge
        is power, and power is equal to energy over time, doesn't that mean that
        money is inversely proportional to knowledge? Knowing that, aren't you
        glad you took the time to read this? Deep stuff.
    """
    def __init__(self, quota=1, unit="seconds", loop=None):
        super().__init__(quota,quota,unit,loop)

        # Beginning of the current interval
        self.trip_start = datetime.utcnow()

        self.trip_fuel = 0

    def throttle(self,fuel):
        def decorator(fn):
            """
            Wraps a function, removing tokens from tank on function calls and delays if none available
            """
            @asyncio.coroutine
            def wrapper(*args,**kwargs):
                # The function that gets called when ready... Where we headed, boss?
                destination = partial(fn,*args,**kwargs)

                # If we don't have a big enough tank to get there anyway, why go?
                if fuel > self.volume:
                    raise Exception('Not enough fuel: Requested fuel, %d, exceeds tank volume, %d' % (fuel,self.volume))

                # Current odometer reading
                odometer = datetime.utcnow()

                # If we've finished our trip, let's start another and refuel
                if odometer - self.trip_start >= self.delta:
                    self.trip_start = odometer
                    self.trip_fuel = 0

                if fuel > self.quota - self.trip_fuel:
                    delay = math.ceil(self.trip_start + self.delta - odometer)
                    return self.loop.call_later(delay, self.burn, fuel, after_trip_reset);
                else:
                    return self.loop.call_soon(self.burn, fuel, after_trip_reset);

                def after_trip_reset():
                    self.trip_fuel += 1
                    destination()
            return wrapper
        return decorator
