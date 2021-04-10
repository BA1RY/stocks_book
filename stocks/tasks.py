import os
from zipfile import BadZipFile
from django.conf import settings
from celery import shared_task
from .utils import download, unzip, get_date_IST, get_csv_data
from .redis_store import RedisStore


@shared_task
def get_bhav_copy():
    BSE_URL = 'https://www.bseindia.com/download/BhavCopy/Equity/'

    date = get_date_IST()

    zip_file_name = f"EQ{date}_CSV.ZIP"
    zip_file_path = os.path.join(settings.BASE_DIR, 'data', zip_file_name)
    csv_file_name = f"EQ{date}.CSV"
    csv_file_path = os.path.join(settings.BASE_DIR, 'data', csv_file_name)
    
    download_url = os.path.join(BSE_URL, zip_file_name)
    download(download_url=download_url, file_path=zip_file_path)

    file = os.path.join(settings.BASE_DIR, 'data', "hello.txt")
    filew = open(file, 'a')
    filew.write(zip_file_name + '\n')
    filew.close()

    try:
        unzip(file_path=zip_file_path)
    except BadZipFile:
        print('Bhavcopy was not uploaded today.')
        return
    finally:
        os.remove(zip_file_path)

    stocks = get_csv_data(
        csv_file_path=csv_file_path,
        usecols=["SC_CODE", "SC_NAME", "OPEN", "HIGH", "LOW", "CLOSE"],
        columns=["code", "name", "open", "high", "low", "close"]
    )
    os.remove(csv_file_path)

    rs = RedisStore(connection_pool=settings.REDIS_CONN_POOL)
    rs.delete_stock_data()
    rs.insert_stock_data(stocks)
