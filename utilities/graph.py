import numpy as np
import matplotlib.pyplot as plt


# Plot
def plot(df, live_price, live_price_col="black", channel_lines=None):
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Extreme'], marker='o')

    # keep at most ~10 labels
    step = max(1, len(df) // 10)
    plt.xticks(
        df.index[::step],
        df['Datetime'].dt.strftime("%Y-%m-%d %H:%M")[::step],
        rotation=45
    )

    # live price point
    live_x = df.index.max() + 1
    plt.scatter(live_x, live_price, color=live_price_col)

    # channel lines if present
    if channel_lines:
        for x_vals, y_vals in channel_lines:
            # extend slope to one more index (live_x)
            slope = (y_vals[-1] - y_vals[0]) / (x_vals[-1] - x_vals[0])
            intercept = y_vals[0] - slope * x_vals[0]
            x_extended = np.append(x_vals, live_x)
            y_extended = slope * x_extended + intercept
            plt.plot(x_extended, y_extended, 'r-')

    plt.grid()
    plt.tight_layout()
    plt.show()


def find_channel_lines(df, match, ref_idx):
    ref_val = df.loc[ref_idx, "Extreme"]

    # furthest match
    match_idx = match.index[0]
    match_val = df.loc[match_idx, "Extreme"]

    # reference and match points in index-space (no datetime gaps)
    x1, y1 = ref_idx, ref_val
    x2, y2 = match_idx, match_val

    # slope and intercept
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - slope * x1

    # full x-axis
    x_full = df.index.to_numpy()
    y_full = slope * x_full + intercept
    return x_full, y_full, slope


def draw_channel_lines(match_peak, match_valley, df, peak_idx, valley_idx, peak_row, valley_row):
    channel_lines = []
    peak_done = False
    valley_done = False
    slope = None  # will store slope for reuse

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

            # parallel line through peak
            y_intercept = peak_row['Extreme'] - slope * peak_idx
            x_full = df.index.to_numpy()
            y_top = slope * x_full + y_intercept
            top_channel_line = [x_full, y_top]
            channel_lines.append(top_channel_line)
            peak_done = True

    if match_valley is not None and not valley_done:
        x, y, slope = find_channel_lines(df, match_valley, valley_idx)
        bottom_channel_line = [x, y]
        channel_lines.append(bottom_channel_line)
    elif peak_done:
        # parallel line through valley
        y_intercept = valley_row['Extreme'] - slope * valley_idx
        x_full = df.index.to_numpy()
        y_bottom = slope * x_full + y_intercept
        bottom_channel_line = [channel_lines[0][0], y_bottom]
        channel_lines.append(bottom_channel_line)

    return channel_lines if channel_lines else None
