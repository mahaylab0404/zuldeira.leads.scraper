import asyncio
from apify import Actor
from .main import main

# This is the 'Ignition Switch' for Zuldeira Technologies
if __name__ == '__main__':
    asyncio.run(main())
