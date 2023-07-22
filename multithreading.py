import logging
import requests
from time import time
from threading import Thread
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

proxy_lum = {'http': 'http://127.0.0.1:24000','https': 'http://127.0.0.1:24000'}

def validate_FBL(index,shopid,sellerid,total_count):
    logger.info("Now in thread:" + str(index))
    FBL_api = 'https://www.lazada.com.my/shop/site/api/seller/products?shopId={shopid}&sellerId={sellerid}'.format(shopid=shopid,sellerid=sellerid)
    retries = 0
    while retries <= 6:
        try:
            response = requests.get(FBL_api,proxies=proxy_lum).json()
            items = response["result"]
            try:
                total_count[index] = items["total"]
            except:
                pass
            break
        except Exception as ex:
                logger.info("trying again... {} / {}. {} in {}".format(retries, 6, ex,index))
                retries += 1
                continue
    return True

if __name__ == "__main__":
    path = r"C:\Users\kelvin.leong\Desktop\Lazada\11.11 Scrape list_output (After remove duplicate).csv"
    df = pd.read_csv(path)
    df = df.loc[:3000][["Shop ID","Seller ID"]]
    print(df)

    total_count = [-1]*len(df)
    
    threads = []

    start = time()

    for index,row in df.iterrows():
        logger.info("Now processing row:" + str(index))
        process = Thread(target=validate_FBL,args=[index,row["Shop ID"],row["Seller ID"],total_count])
        process.start()
        threads.append(process)

    for process in threads:
        process.join()

    logger.info("Total time taken:" + str(time()-start))

    print(len(total_count))
