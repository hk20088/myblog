#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Leon Hu'

import www.orm as om, asyncio
from www.models import User, Blog, Comment


async def test(loop):
    await om.create_pool(loop=loop,user='root', password='password', db='awesome')

    u = User(name='Test', email='H@example.com', passwd='1234567890', image='about:blank')

    await u.save()


loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
# loop.run_forever()
# loop.close()
