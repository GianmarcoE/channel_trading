from utilities.data_ops import data_prep, trend_finder, recommendations, show, final_verdict


def main(df, live_price, whole_df=False, show_graph=True, own_it="No"):
    # settings = DevSettings() if dev_run else ProdSettings()

    # df = settings.df
    # live_price = settings.live_price

    if not whole_df:
        trend_counter = 0
        trends = []
        figs = []
        iterations = 0
        for i in range(20, len(df), 20):
            iterations += 1
            df_slice = df.tail(i)
            df_slice = data_prep(df_slice)
            trend, df_slice, channel_lines, current_channel_limits = trend_finder(df_slice, 4.3, 6)
            if trend:
                trend_counter += 1
                df_slice, live_price_col, advice = recommendations(live_price, current_channel_limits, df_slice, own_it)
                # print(F"Trend identified: {advice}")
                trends.append(advice)
                fig = show(df_slice, live_price, show_graph, live_price_col, channel_lines)
                figs.append(fig)
            else:
                pass
                # print("No trend")
                # show(df_slice, live_price, show_graph)
        verdict = final_verdict(trends)
        # print(f"Found {trend_counter} trends out of {iterations} iterations")
        # print(f"Overall recommendation: {verdict}")
        return figs, trends, verdict
    # else:
    #     df = data_prep(df)
    #     trend, df, channel_lines, current_channel_limits = trend_finder(df, 4.3, 2)
    #     if trend:
    #         print("Trend identified")
    #         df, live_price_col = recommendations(live_price, current_channel_limits, df)
    #         show(df, live_price, show_graph, live_price_col, channel_lines)
    #         print(df)
    #     else:
    #         print("No trend")
    #         show(df, live_price, show_graph)
    #         print(df)


# if __name__ == '__main__':
#     main(dev_run=False, whole_df=False, show_graph=True, own_it="Yes")
