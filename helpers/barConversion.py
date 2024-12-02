import re
from alpaca.data.models.bars import Bar

def bars_string_to_BarClass(data):
    # Convert the string to a dictionary
    result_dict = bars_string_to_dict(data)
    # Create an instance of the Bar class
    bar = Bar(
        t=result_dict['timestamp'],
        o=result_dict['open'],
        h=result_dict['high'],
        l=result_dict['low'],
        c=result_dict['close'],
        v=result_dict['volume'],
        n=result_dict['trade_count'],
        vw=result_dict['vwap']
    )
    return bar

def bars_string_to_dict(data):

    # Regular expression to match key-value pairs
    pattern = r"(\w+)=('[^']*'|datetime\.datetime\([^\)]*\)|[^ ]+)"

    # Find all matches
    matches = re.findall(pattern, data)

    # Convert matches to dictionary
    result_dict = {}
    for key, value in matches:
        if key == 'timestamp':
            # Evaluate the timestamp string to convert it to a datetime object
            value = eval(value)
        result_dict[key] = value
    
    return result_dict