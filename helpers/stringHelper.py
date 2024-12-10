from alpaca.data.models.bars import Bar

def bar_to_oneline_string(data: Bar):
    """
     Convert a bar object to a string in the format:
        MM/DD/YYYY HH:MM:SS symbol='SYM' o=O h=H l=L c=C v=V trade_count=TC vwap=VWAP
     Normally a printed bar would look like this:
        symbol='BA' timestamp=datetime.datetime(2024, 12, 10, 14, 36, tzinfo=datetime.timezone.utc) open=161.01 high=161.46 low=161.01 close=161.37 volume=873.0 trade_count=22.0 vwap=161.3075
    """

    the_string = (
        f"{data.timestamp.strftime('%m/%d/%Y %H:%M:%S')} "
        f"symbol='{data.symbol}' "
        f"o={data.open} "
        f"h={data.high} "
        f"l={data.low} "
        f"c={data.close} "
        f"v={data.volume} "
        f"trade_count={data.trade_count} "
        f"vwap={data.vwap}"
    )

    return the_string