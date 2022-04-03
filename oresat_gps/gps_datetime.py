from datetime import datetime, timedelta, timezone

GPS_EPOCH = datetime(1980, 1, 5, tzinfo=timezone.utc)
'''Last gps week rollover, note: next is in 2038'''


def gps_datetime(gps_week: int, tow: int) -> float:
    '''Get the time from gps_week and TOW (time of week) as a float similar
    to :py:func:`time.time`
    '''

    usec = tow % 100 * 1000
    # 86400 is number of seconds in a day
    sec = (tow / 100) % 86400
    day = ((tow / 100) / 86400) + (gps_week * 7)
    dt = GPS_EPOCH + timedelta(days=day, seconds=sec, microseconds=usec)

    return dt.timestamp()
