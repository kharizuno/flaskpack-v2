# -*- coding: utf-8 -*-
import calendar
import time
import pytz
from datetime import datetime


def str2datetime(timestr, timeformat="%Y-%m-%d"):
    dt = datetime.strptime(timestr, timeformat)
    return dt


def get_ts() -> int:
    """
    Get timestamp pakai format yang di pakai di JVM.
    """
    return int(time.time() * 1000)


def get_current_datetime() -> datetime:
    return datetime.now()


def get_current_epoch() -> int:
    """return current timestamp in UTC"""
    d = datetime.now(tz=pytz.timezone('UTC'))
    ts = calendar.timegm(d.timetuple())
    return int(datetime.fromtimestamp(ts).timestamp())


def datetime2epoch(dt) -> int:
    """Convert python `class`datetime.datetime to epoch (GMT +0)

    :param dt: datetime to be converted
    :type dt: datetime
    """

    def fix_epoch(h, m):
        """fix epoch

        :param h: hour
        :param m: minute
        :return:
        """
        m = m + 7
        if m > 59:
            h = h + 1
            if h > 23:
                h = h - 23

            m = m - 59
            if m < 0:
                m = 0

        return h, m

    if not dt.tzinfo:
        dt = pytz.utc.localize(dt)
        #: dirty-hack to correct minute
        hour, minute = fix_epoch(dt.hour, dt.minute)
        dt = dt.replace(tzinfo=pytz.timezone('Asia/Jakarta'), minute=minute, hour=hour)

    if dt.tzinfo != pytz.timezone('UTC'):
        dt = dt.astimezone(pytz.timezone('UTC'))

    ts = calendar.timegm(dt.timetuple())
    return int(datetime.fromtimestamp(ts).timestamp())


def epoch2datetime(e) -> datetime:
    """Convert UTC epoch to UTC datetime

    :param e:
    :type e: str|int|mongoengine.LongField
    """
    if isinstance(e, str):
        e = int(e)

    t = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(e))
    d = datetime.strptime(t, "%a, %d %b %Y %H:%M:%S +0000")
    return d
