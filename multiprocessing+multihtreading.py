import pandas as pd
import numpy as np
import requests
from threading import Thread
from multiprocessing.pool import ThreadPool as Pool
import logging
from time import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

proxy_lum = {'http': 'http://127.0.0.1:24000','https': 'http://127.0.0.1:24000'}

def validate_FBL(index,shopid,sellerid,total_count):
    logger.info("Now in thread:" + str(index))
    FBL_api = FNCTION STARTS HERE
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

final_result = []

def split_df_validate_LazBonus(df):
    result = [-1]*len(df)
    threads = []
    for index,row in df.iterrows():
        logger.info("Now processing row:" + str(index))
        process = Thread(target=validate_FBL,args=[index,row["Shop ID"],row["Seller ID"],result])
        process.start()
        threads.append(process)
    for process in threads:
        process.join()
    return result

def collect_LazBonus_result(result):
    global final_result
    final_result.extend(result)

if __name__ == "__main__":
    path = {FILE_PATH}
    df = pd.read_csv(path)
    df = df.loc[:3000][["Shop ID","Seller ID"]]
    print(df)
    
    start = time()

    with Pool(4) as pool:
        for i in np.array_split(df,4):
            pool.apply_async(split_df_validate_LazBonus,args=(i,),callback=collect_LazBonus_result)
        pool.close()
        pool.join()

    logger.info("Total time taken:" + str(time()-start))

    final_result = np.reshape(final_result,(-1,1))
    final_result = pd.DataFrame(final_result,columns=["total_count"])
    print(len(final_result))