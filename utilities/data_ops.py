import pandas as pd
import numpy as np
from collections import Counter
from utilities import graph


def data_prep(df):
    """
    Prepares the DataFrame to have all needed information.

    Parameters:
        df: File input (DataFrame).

    Return:
        df: Ready DataFrame.
    """
    df = df.drop(['Open', 'Dividends', 'Volume', 'Stock Splits'], axis=1)
    df['Average'] = (df['High'] + df['Low']) / 2
    df['Datetime'] = pd.to_datetime(df['Datetime'])

    # sequential index as x-axis (no gaps)
    df = df.reset_index(drop=True)
    candles = df.index.to_numpy()

    # linear fit on sequential candles
    m, q = np.polyfit(candles, df['Average'], 1)
    fit_values = m * candles + q

    # For graph purposes
    candle_line = np.array([candles.min(), candles.max()])
    fit_values_graph = m * candle_line + q

    df['Delta_Peak'] = df['High'] - fit_values
    df['Delta_Valley'] = df['Low'] - fit_values
    df['Extreme'] = df.apply(
        lambda row: row['Delta_Valley']
        if abs(row['Delta_Valley']) > abs(row['Delta_Peak'])
        else row['Delta_Peak'],
        axis=1,
    )
    df['Extreme'] = fit_values + df['Extreme']

    return df


def trend_finder(df, tolerance, time_margin):
    """
    Finds channels in trading data.

    Parameters:
        df: Input file (DataFrame).
        tolerance: Max channel line sloping variation from interpolation line.
        time_margin: Minimum gap between two peaks.

    Return:
        bool: Whether a trend was found.
        df: DataFrame.
        channel_lines: Values of channel lines.
        current_channel_limits: Most recent values of channel lines (upper and lower limits of channel).
    """
    def find_matches(extreme_idx, col_name, is_peak):
        """
        Finds matching delta points among highs and lows.

        Parameters:
            extreme_idx: Highest/lowest point on graph.
            col_name: Column name for High/Low value.
            is_peak: Whether is High or Low.

        Return:
             Furthest matching point.
        """
        val = df.loc[extreme_idx, col_name]  # value of max/min delta point
        # Exclude records within minimum time gap
        mask = (df.index < extreme_idx - time_margin) | (df.index > extreme_idx + time_margin)
        candidates = df.loc[mask, col_name]  # Delta values to be taken into considerations

        matches = candidates[np.abs(candidates - val) / abs(val) <= tolerance]

        # if is_peak:
        #     matches = candidates[np.abs(candidates - val) / val <= tolerance]
        # else:
        #     matches = candidates[np.abs(candidates - val) / abs(val) <= tolerance]

        if matches.empty:
            return None

        # Furthest match
        furthest_idx = max(matches.index, key=lambda i: abs(i - extreme_idx))
        furthest_val = matches.loc[furthest_idx]

        #  --------TEST IF WORTH KEEPING OR NOT------
        # # Post-check: reject if any delta is outside range line
        # df_excluding_extreme = df.drop(index=extreme_idx)  # Exclude extreme value
        # if (df_excluding_extreme[col_name].abs() > abs(furthest_val)).any():
        #     return None

        return matches.loc[[furthest_idx]]

    tolerance = tolerance/100

    peak = df["Delta_Peak"].nlargest(1)
    peak_idx = peak.index[0]
    peak_row = df.loc[peak_idx]  # full row access

    valley = df["Delta_Valley"].nsmallest(1)
    valley_idx = valley.index[0]
    valley_row = df.loc[valley_idx]  # full row access

    match_peak = find_matches(peak_idx, "Delta_Peak", True)
    match_valley = find_matches(valley_idx, "Delta_Valley", False)

    channel_lines = graph.draw_channel_lines(match_peak, match_valley, df, peak_idx, valley_idx, peak_row, valley_row)

    # upper line check
    if channel_lines is not None:
        x_vals_upper, y_vals_upper = channel_lines[0]
        for x, y in zip(x_vals_upper, y_vals_upper):
            if df.loc[x, "Extreme"] > y:
                channel_lines = None
                break

    # lower line check
    if channel_lines is not None:
        x_vals_lower, y_vals_lower = channel_lines[1]
        for x, y in zip(x_vals_lower, y_vals_lower):
            if df.loc[x, "Extreme"] < y:
                channel_lines = None
                break

    if channel_lines:
        current_channel_limits = [float(channel_lines[0][-1][-1]), float(channel_lines[1][-1][-1])]
        return True, df, channel_lines, current_channel_limits
    else:
        return False, df, None, None


def recommendations(live_price, current_channel_limits, df, own_it):
    def sell():
        return "Sell", 'red'

    def buy():
        return "Buy", "#21d952"

    def hold():
        return "Hold", "grey"
    lower_line, upper_line = sorted(current_channel_limits)
    upper_range_start = lower_line + 0.8 * (upper_line - lower_line)  # 80% of channel range
    lower_range_start = lower_line + 0.2 * (upper_line - lower_line)  # 20% of channel range

    if live_price < lower_line:  # below lower line
        if own_it == "Yes":
            advice, live_price_col = sell()
        else:
            advice, live_price_col = hold()
    elif lower_line <= live_price <= lower_range_start:  # low 0-20% of channel
        if own_it == "Yes":
            advice, live_price_col = hold()
        else:
            advice, live_price_col = buy()
    elif live_price >= upper_line:  # above upper line
        if own_it == "Yes":
            advice, live_price_col = hold()
        else:
            advice, live_price_col = buy()
    elif upper_line >= live_price >= upper_range_start:  # high 80-100% of channel
        if own_it == "Yes":
            advice, live_price_col = sell()
        else:
            advice, live_price_col = hold()
    else:  # in the middle zone
        advice, live_price_col = hold()

    return df, live_price_col, advice


def final_verdict(trends):
    counts = Counter(trends)
    try:
        first, freq1 = counts.most_common(1)[0]
        second, freq2 = counts.most_common(2)[1]
        return f"Strong {first}" if freq1 > 2 * freq2 else first
    except IndexError:
        try:
            first, freq1 = counts.most_common(1)[0]
            return f"Strong {first}"
        except IndexError:
            return "Hold"


def show(df, live_price, show_graph, live_price_col=None, channel_lines=None):
    if channel_lines:
        if show_graph:
            fig = graph.plot(df, live_price, live_price_col, channel_lines)
            return fig
    else:
        if show_graph:
            graph.plot(df, live_price)
        return None
