import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# Plot
def plot(df, live_price, live_price_col="black", channel_lines=None):
    plt.figure(figsize=(12, 6))
    plt.scatter(df['Datetime'], df['Extreme'], color='blue', label='Max/Min values')
    plt.scatter(datetime.datetime.now(), live_price, color=live_price_col)
    # plt.scatter(datetime.datetime.now(), live_price, color=live_price_col)
    if channel_lines:
        plt.plot(channel_lines[0][0], channel_lines[0][1], 'r-')
        plt.plot(channel_lines[1][0], channel_lines[1][1], 'r-')
    plt.legend()
    plt.grid()
    plt.show()


def find_channel_lines(df, match, ref_idx):
    ref_val = df.loc[ref_idx, "Extreme"]

    # furthest match from your function
    match_idx = match.index[0]
    match_val = df.loc[match_idx, "Extreme"]

    # reference and match points
    x1, y1 = df.loc[ref_idx, "Datetime"], ref_val
    x2, y2 = df.loc[match_idx, "Datetime"], match_val

    # convert datetime to numeric for slope
    x1_num = mdates.date2num(x1)
    x2_num = mdates.date2num(x2)
    slope = (y2 - y1) / (x2_num - x1_num)
    intercept = y1 - slope * x1_num

    # full x-axis
    x_full = df["Datetime"]
    x_full_num = mdates.date2num(x_full)
    y_full = slope * x_full_num + intercept
    return x_full, y_full, slope


def draw_channel_lines(match_peak, match_valley, df, peak_idx, valley_idx, peak_row, valley_row):
    channel_lines = []
    peak_done = False
    valley_done = False

    if match_peak is not None:
        x_top, y_top, slope = find_channel_lines(df, match_peak, peak_idx)
        top_channel_line = [x_top, y_top]
        channel_lines.append(top_channel_line)
        peak_done = True
    else:
        if match_valley is not None:
            x_bottom, y_bottom, slope = find_channel_lines(df, match_valley, valley_idx)
            bottom_channel_line = [x_bottom, y_bottom]
            channel_lines.append(bottom_channel_line)
            valley_done = True
            y_intercept = peak_row['Extreme'] - slope * mdates.date2num(peak_row["Datetime"])
            x_full = df["Datetime"]
            x_full_num = mdates.date2num(x_full)
            y_top = slope * x_full_num + y_intercept
            top_channel_line = [x_bottom, y_top]
            channel_lines.append(top_channel_line)
            peak_done = True

    if match_valley is not None and not valley_done:
        x, y, slope = find_channel_lines(df, match_valley, valley_idx)
        bottom_channel_line = [x, y]
        channel_lines.append(bottom_channel_line)
    elif peak_done:
        y_intercept = valley_row['Extreme'] - slope * mdates.date2num(valley_row["Datetime"])
        x_full = df["Datetime"]
        x_full_num = mdates.date2num(x_full)
        y_bottom = slope * x_full_num + y_intercept
        bottom_channel_line = [channel_lines[0][0], y_bottom]
        channel_lines.append(bottom_channel_line)

    if channel_lines:
        return channel_lines
    else:
        return None
