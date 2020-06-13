import requests
from bs4 import BeautifulSoup

from crypto_crawler.common import convert_as_number, get_system_milli
from crypto_crawler.const import TARGET_EXCHANGE_SET, TARGET_COIN_PAIR, COIN_NAME_BITCOIN
from crypto_crawler.data_model import CryptoPrice


def map_list_to_price(line):
    """
    expected line:
        ['1', 'BKEX', 'BTC/USDT', '$404,691,250', '$8105.52', '2.81%', 'Spot', 'Percentage', 'Recently']
    :param line: list
    :return: CryptoPrice
    """
    return CryptoPrice(exchange=line[1],
                       coin_name=COIN_NAME_BITCOIN,
                       price=convert_as_number(line[3]),
                       pricing_time=get_system_milli(),
                       volume=convert_as_number(line[4]),
                       volume_p=convert_as_number(line[6]) / 100,
                       fee_type=line[8],
                       coin_pair=line[2])


def filter_coin_row(line, target_exchanges, target_pairs):
    return line[2] in target_pairs


def get_web_content(url, target_exchanges=TARGET_EXCHANGE_SET, target_pairs=TARGET_COIN_PAIR):
    """
    request for crypto price page and convert to dict of CryptoPrice
    :param url:                 price url to crawl
    :param target_exchanges:    internal set to filter needed information
    :param target_pairs:        internal set to filter coin pair
    :return:                    list<CryptoPrice>
    """
    code = requests.get(url)
    plain = code.text
    s = BeautifulSoup(plain, "html.parser")

    exchange_price = []
    price_table = s.find_all('tbody')[0].contents
    for row in price_table:
        if len(row) > 1:
            line = row.contents
            filtered_line = [i.text for i in line]
            # check if the exchange we want
            if filter_coin_row(filtered_line, target_exchanges, target_pairs):
                try:
                    exchange_price.append(map_list_to_price(filtered_line))
                except Exception as e:
                    print(e)
    return exchange_price
