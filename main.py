from binance.rest import BinanceOpsHttp, Interval

if __name__ == '__main__':
    api_key = "8844177a-b838-478e-afec-5370ca624b19"
    api_secret = "e8dc31b7-26f2-42b3-a356-c2a4eb816950"

    binance_ops = BinanceOpsHttp(api_key=api_key, api_secret=api_secret)

    # print(binance_ops.get_ping())

    # print(binance_ops.get_server_time())

    # print(binance_ops.get_option_info())

    # print(binance_ops.get_exchange_info())

    # print(binance_ops.get_index())

    # print(binance_ops.get_ticker('BTCUSDT-201127-15000-C'))

    # print(binance_ops.get_mark())
    # print(binance_ops.get_mark('BTCUSDT-201127-15000-C'))


    # print(binance_ops.get_order_book('BTCUSDT-201127-15000-C', limit=[10,300]))
    # print(binance_ops.get_kline('BTCUSDT-201127-15000-C', Interval.MINUTE_1))
    # print(binance_ops.get_trades('BTCUSDT-201127-15000-C'))

    # print(binance_ops.get_historical_trades('BTCUSDT-201127-15000-C', from_id='1125899906843376090'))

    # print(binance_ops.get_listen_key())
    # {'code': 0, 'msg': 'success', 'data': {'listenKey': 'etJVNvLsUGD73XBhfIHFdkyd8ZRktMy4iDoj3hpi'}}
    print(binance_ops.extend_listen_key('DUEnlKe6vwFY6x1un9Li6af6Bot6koOtnWq3Gud4'))
