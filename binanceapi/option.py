
import requests
import time
import hmac
import hashlib
from enum import Enum
from threading import Lock

from binanceapi.constant import RequestMethod, Interval, OrderSide, OrderStatus, OrderType

class OptionClient(object):

    def __init__(self, api_key=None, api_secret=None, host=None, timeout=5, try_counts=5):
        self.api_key = api_key
        self.api_secret = api_secret
        self.host = host if host else 'https://testnet.binanceops.com'
        self.recv_window = 10000
        self.timeout = timeout
        self.order_count_lock = Lock()
        self.order_count = 1_000_000
        self.try_counts = try_counts  # 失败尝试的次数.

    def build_parameters(self, params: dict):
        keys = list(params.keys())
        keys.sort()
        return '&'.join([f"{key}={params[key]}" for key in params.keys()])

    def request(self, req_method: RequestMethod, path: str, params=None, verify=False):
        url = self.host + path

        if verify:
            query_str = self._sign(params)
            url += '?' + query_str
        elif params:
            url += '?' + self.build_parameters(params)
        headers = {"X-MBX-APIKEY": self.api_key}

        for i in range(0, self.try_counts):
            try:
                response = requests.request(req_method.value, url=url, headers=headers, timeout=self.timeout)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(response.json(), response.status_code)
            except Exception as error:
                print(f"请求:{path}, 发生了错误: {error}")
                time.sleep(3)

    def get_ping(self):
        """
        check the connection
        :return:
        """
        path = "/api/v1/ping"
        return self.request(req_method=RequestMethod.GET, path=path)

    def get_server_time(self):
        """
        get the server time.
        :return:
        """
        path = '/api/v1/time'
        return self.request(req_method=RequestMethod.GET, path=path)

    def get_option_info(self):

        """
        get the option info
        """

        path = '/api/v1/optionInfo'
        return self.request(req_method=RequestMethod.GET, path=path)

    def get_exchange_info(self):

        """
        get the exchange info
        """

        path = '/api/v1/exchangeInfo'
        return self.request(req_method=RequestMethod.GET, path=path)

    def get_index(self, underlying='BTCUSDT'):
        """
        get the spot index, you may use as reference
        :return:
        """
        path = "/api/v1/index"
        params = {
            'underlying': underlying
        }
        return self.request(req_method=RequestMethod.GET, path=path, params=params)

    def get_ticker(self, symbol=None):
        path = "/api/v1/ticker"

        params = {}
        if symbol is not None:
            params['symbol'] = symbol

        return self.request(req_method=RequestMethod.GET, path=path, params=params)

    def get_mark(self, symbol=None):
        path = '/api/v1/mark'
        params = {}
        if symbol is not None:
            params['symbol'] = symbol

        return self.request(req_method=RequestMethod.GET, path=path, params=params)

    def get_order_book(self, symbol, limit=10):
        """
        :param symbol: BTCUSDT, BNBUSDT ect, 交易对.
        :param limit: market depth.
        :return: return order_book in json 返回订单簿，json数据格式.
        """
        limits = [10, 20, 50, 100, 1000]

        if limit not in limits:
            limit = 10

        path = "/api/v1/depth"
        params = {"symbol": symbol,
                  "limit": limit
                  }

        print(params)

        return self.request(RequestMethod.GET, path, params)

    def get_kline(self, symbol, interval: Interval, start_time=None, end_time=None, limit=500):
        """
        获取K线数据.
        :param symbol:
        :param interval:
        :param start_time:
        :param end_time:
        :param limit:
        :param max_try_time:
        :return:
        """
        path = "/api/v1/klines"

        if limit not in [500, 1500]:
            limit = 500

        params = {
            "symbol": symbol,
            "interval": interval.value,
            "limit": limit
        }

        if start_time:
            params['startTime'] = start_time

        if end_time:
            params['endTime'] = end_time

        return self.request(RequestMethod.GET, path, params)

    def get_trades(self, symbol, limit=100):
        path = "/api/v1/trades"
        if limit not in [100, 500]:
            limit = 100

        params = {
            "symbol": symbol,
            "limit": limit
        }

        return self.request(RequestMethod.GET, path, params)

    def get_historical_trades(self, symbol, from_id=None, limit=100):
        path = '/api/v1/historicalTrades'
        if limit not in [100, 500]:
            limit = 100
        params = {'symbol': symbol, 'limit': limit}
        if from_id is not None:
            params['fromId'] = from_id

        return self.request(RequestMethod.GET, path, params)

    def get_client_order_id(self):
        """
        generate the client_order_id for user.
        :return:
        """
        with self.order_count_lock:
            self.order_count += 1
            return "x-A6SIDXVS" + str(self.get_timestamp()) + str(self.order_count)

    def get_timestamp(self):
        """
        获取系统的时间.
        :return:
        """
        return int(time.time() * 1000)

    def _sign(self, params):
        """
        签名的方法， signature for the private request.
        :param params: request parameters
        :return:
        """
        query_string = self.build_parameters(params)
        hex_digest = hmac.new(self.api_secret.encode('utf8'), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
        return query_string + '&signature=' + str(hex_digest)

    def get_listen_key(self):
        path = "/api/v1/userDataStream"
        params = {
            'recvWindow': 5000,
            'timestamp': self.get_timestamp()
        }

        return self.request(RequestMethod.POST, path, params, verify=True)

    def extend_listen_key(self, listen_key):
        """
        :param listen_key:
        :return:
        """
        path = "/api/v1/userDataStream"
        params = {
            'recvWindow': 5000,
            'timestamp': self.get_timestamp(),
            'listenKey': listen_key
        }
        return self.request(RequestMethod.PUT, path, params, verify=True)

    def delete_listen_key(self):
        pass

    def place_order(self, symbol: str, order_side: OrderSide, order_type: OrderType, quantity: float, price: float,
                    client_order_id: str = None, time_inforce="GTC", stop_price=0):
        """

        :param symbol: 交易对名称
        :param order_side: 买或者卖， BUY or SELL
        :param order_type: 订单类型 LIMIT or other order type.
        :param quantity: 数量
        :param price: 价格.
        :param client_order_id: 用户的订单ID
        :param time_inforce:
        :param stop_price:
        :return:
        """

        path = '/api/v1/order'

        if client_order_id is None:
            client_order_id = self.get_client_order_id()

        params = {
            "symbol": symbol,
            "side": order_side.value,
            "type": order_type.value,
            "quantity": quantity,
            "price": price,
            "recvWindow": self.recv_window,
            "timestamp": self.get_timestamp(),
            "newClientOrderId": client_order_id
        }

        if order_type == OrderType.LIMIT:
            params['timeInForce'] = time_inforce

        if order_type == OrderType.MARKET:
            if params.get('price'):
                del params['price']

        if order_type == OrderType.STOP:
            if stop_price > 0:
                params["stopPrice"] = stop_price
            else:
                raise ValueError("stopPrice must greater than 0")

        return self.request(RequestMethod.POST, path, params, verify=True)

    def get_order(self, symbol: str, client_order_id: str):
        """
        获取订单状态.
        :param symbol:
        :param client_order_id:
        :return:
        """
        path = "/api/v1/order"
        prams = {"symbol": symbol, "timestamp": self.get_timestamp(), "origClientOrderId": client_order_id}

        return self.request(RequestMethod.GET, path, prams, verify=True)

    def cancel_order(self, symbol, client_order_id):
        """
        撤销订单.
        :param symbol:
        :param client_order_id:
        :return:
        """
        path = "/api/v1/order"
        params = {"symbol": symbol, "timestamp": self.get_timestamp(),
                  "origClientOrderId": client_order_id
                  }

        for i in range(0, 3):
            try:
                order = self.request(RequestMethod.DELETE, path, params, verify=True)
                return order
            except Exception as error:
                print(f'cancel order error:{error}')
        return

    def get_open_orders(self, symbol=None):
        """
        获取所有的订单.
        :param symbol: BNBUSDT, or BTCUSDT etc.
        :return:
        """
        path = "/api/v1/openOrders"

        params = {"timestamp": self.get_timestamp()}
        if symbol:
            params["symbol"] = symbol

        return self.request(RequestMethod.GET, path, params, verify=True)

    def cancel_open_orders(self, symbol):
        """
        撤销某个交易对的所有挂单
        :param symbol: symbol
        :return: return a list of orders.
        """
        path = "/api/v1/openOrders"

        params = {"timestamp": self.get_timestamp(),
                  "recvWindow": self.recv_window,
                  "symbol": symbol
                  }

        return self.request(RequestMethod.DELETE, path, params, verify=True)

    def get_account_info(self):
        """

        :return:
        """
        path = "/api/v1/account"
        params = {"timestamp": self.get_timestamp(),
                  "recvWindow": self.recv_window
                  }
        return self.request(RequestMethod.GET, path, params, verify=True)
