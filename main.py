import requests
import pickle
import os.path
from time import sleep
from bs4 import BeautifulSoup


def e_ketalog_price(link, headers):
    """
    Поиск на e-katalog

    Arguments:
    link -- ссылка на товар с e-katalog
    headers -- данные пользователя для сайта

    Returns:
    result -- число (минимальная цена товара)
    """
    full_page = requests.get(link, headers=headers)
    soup = BeautifulSoup(full_page.content, 'html.parser')
    convert = (soup.findAll("div", {"class": "desc-big-price ib", }))[0].text
    convert = ''.join(convert.split('до')[0])
    res = [int(i) for i in convert.split() if i.isdigit()]
    result = 0
    for i in res:
        result = result * 1000 + i
    return result


def avito_offers(link, headers):
    """
    Поиск всех предложений на avito

    Arguments:
    link -- ссылка на товар с avito
    headers -- данные пользователя для сайта

    Returns:
    result -- множество set (множество ссылок на предложения)
    """
    offersAvito = set()

    full_page = requests.get(link, headers=headers)
    soup = BeautifulSoup(full_page.content, 'html.parser')
    for oneOffer in soup.findAll("div", {"data-marker": "catalog-serp"})[0].findAll('a', {
        "class": "iva-item-sliderLink-2hFV_"}):
        offersAvito.add("https://www.avito.ru/" + str(oneOffer.attrs['href']))
    return offersAvito


# ссылки на нужные ресурсы. Данные юзера-агента
E_KATALOG_POKE = "https://www.e-katalog.ru/prices/onyx-boox-poke-3/"
E_KATALOG_NOVA = "https://www.e-katalog.ru/prices/onyx-boox-nova-3/"
AVITO_POKE = "https://www.avito.ru/rossiya/planshety_i_elektronnye_knigi?q=ONYX+BOOX+Poke+3"
AVITO_NOVA = "https://www.avito.ru/rossiya/planshety_i_elektronnye_knigi?q=ONYX+BOOX+Nova+3"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'}
offers = {}

offers['AVITO_POKE'] = avito_offers(AVITO_POKE, headers)
offers['E_KATALOG_POKE'] = e_ketalog_price(E_KATALOG_POKE, headers)
offers['E_KATALOG_NOVA'] = e_ketalog_price(E_KATALOG_NOVA, headers)
sleep(10) #that sleep is for tricking the avito-anti bot system
offers['AVITO_NOVA'] = avito_offers(AVITO_NOVA, headers)

offersDataFile = 'ebookOffers.data'
if os.path.exists(offersDataFile) is False:
    fileData = open(offersDataFile, 'wb')
    pickle.dump(offers, fileData)
    fileData.close()
    print("New file created. Data saved")
else:
    fileData = open(offersDataFile, 'rb')
    previousData = pickle.load(fileData)

    for key, value in previousData.items():
        if isinstance(value, int):
            if previousData[key] == offers[key]:
                print(key, "offers didn't changed")
            else:
                print(key, "get new price:", value, ". Was", offers[key])
        if isinstance(value, set):
            if offers[key] == value:
                print(key, "didn't get new offers")
            else:
                print(key, "get new offers. Was in file:", value, ". New offers: ", offers[key])
    fileData.close()

    fileData = open(offersDataFile, 'wb')
    pickle.dump(offers, fileData)
    fileData.close()

del offers
