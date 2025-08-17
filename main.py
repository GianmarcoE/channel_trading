from settings import DevSettings, ProdSettings
from utilities.data_ops import data_prep, trend_finder, recommendations, show


def main(dev_run, whole_df=False, show_graph=True):
    settings = DevSettings() if dev_run else ProdSettings()

    df = settings.df
    live_price = settings.live_price

    if not whole_df:
        trend_counter = 0
        iterations = 0
        for i in range(15, len(df), 20):
            iterations += 1
            df_slice = df.tail(i)
            df_slice = data_prep(df_slice)
            trend, df_slice, channel_lines, current_channel_limits = trend_finder(df_slice, 4.3, 2)
            if trend:
                trend_counter += 1
                print("Trend identified")
                df_slice, live_price_col = recommendations(live_price, current_channel_limits, df_slice)
                show(df_slice, live_price, show_graph, live_price_col, channel_lines)
            else:
                print("No trend")
                show(df_slice, live_price, show_graph)
        print(f"{trend_counter} su {iterations}")
    else:
        df = data_prep(df)
        trend, df, channel_lines, current_channel_limits = trend_finder(df, 4.3, 2)
        if trend:
            print("Trend identified")
            df, live_price_col = recommendations(live_price, current_channel_limits, df)
            show(df, live_price, show_graph, live_price_col, channel_lines)
        else:
            print("No trend")
            show(df, live_price, show_graph)


if __name__ == '__main__':
    main(dev_run=True, whole_df=False, show_graph=False)
