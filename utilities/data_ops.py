import pandas as pd
import numpy as np
from collections import Counter
from utilities import graph


def data_prep(df):
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
    def find_matches(extreme_idx, col_name, is_peak):
        val = df.loc[extreme_idx, col_name]
        mask = (df.index < extreme_idx - time_margin) | (df.index > extreme_idx + time_margin)
        candidates = df.loc[mask, col_name]

        if is_peak:
            matches = candidates[np.abs(candidates - val) / val <= tolerance]
        else:
            matches = candidates[np.abs(candidates - val) / abs(val) <= tolerance]

        if matches.empty:
            return None

        # furthest match
        furthest_idx = max(matches.index, key=lambda i: abs(i - extreme_idx))
        return matches.loc[[furthest_idx]]  # still a Series

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

    if channel_lines:
        current_channel_limits = [float(channel_lines[0][-1][-1]), float(channel_lines[1][-1][-1])]
        return True, df, channel_lines, current_channel_limits
    else:
        return False, df, None, None


def recommendations(live_price, current_channel_limits, df, own_it):
    def sell():
        print("Sell")
        return "Sell", 'red'

    def buy():
        print("Buy")
        return "Buy", "#21d952"

    def hold():
        print("Hold")
        return "Hold", "grey"
    lower_line, upper_line = sorted(current_channel_limits)

    if live_price < lower_line:  # below lower line
        if own_it:
            advice, live_price_col = sell()
        else:
            advice, live_price_col = hold()
    elif lower_line <= live_price <= lower_line * 1.003:  # within +0.3% above lower line
        if own_it:
            advice, live_price_col = hold()
        else:
            advice, live_price_col = buy()
    elif live_price >= upper_line:  # above upper line
        if own_it:
            advice, live_price_col = hold()
        else:
            advice, live_price_col = buy()
    elif upper_line > live_price >= upper_line * 0.997:  # within -0.3% below upper line
        if own_it:
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
            graph.plot(df, live_price, live_price_col, channel_lines)
        return True
    else:
        if show_graph:
            graph.plot(df, live_price)
        return False
