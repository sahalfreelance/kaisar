import requests
import time
import json
from loguru import logger
from fake_useragent import UserAgent
import uuid
import cloudscraper
import asyncio
import os
os.system('clear')
banner = """\033[36m
██╗  ██╗ █████╗ ██╗███████╗ █████╗ ██████╗ 
██║ ██╔╝██╔══██╗██║██╔════╝██╔══██╗██╔══██╗
█████╔╝ ███████║██║███████╗███████║██████╔╝
██╔═██╗ ██╔══██║██║╚════██║██╔══██║██╔══██╗
██║  ██╗██║  ██║██║███████║██║  ██║██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ZeroNode
----------------------------------------------------
              Author : Sahal Pramudya
----------------------------------------------------"""
print(banner)
uid = input("Masukkan token : ")
os.system('clear')
print(banner)
ext_id = str(uuid.uuid4())
useragent = UserAgent().random
url = {
    "claim":"https://zero-api.kaisar.io/mining/claim",
    "mining_point":"https://zero-api.kaisar.io/extension/mining-point",
    "current_ext":f"https://zero-api.kaisar.io/mining/current?extension={ext_id}",
    "start":"https://zero-api.kaisar.io/mining/start",
    "ping":"https://zero-api.kaisar.io/extension/ping"
}
payload = {
    "extension":ext_id
}
headers = {
    "authorization":f"Bearer {uid}",
    "Accept":"application/json, text/plain, */*",
    "User-Agent":useragent
}
async def start():
    scraper = cloudscraper.create_scraper()
    response = scraper.post(url['start'], data=payload, headers=headers)
    try:
        json = response.json()
        if response.status_code == 412:
            cek = json['error']
            if cek['message'] == "Mining is started.":
                logger.info("Miner already started.")
                await checkpoint()
                await curext()
            elif cek['message'] == "Mining is not claim.":
                logger.info("Miner ready to claim. Claiming in 3 second.")
                await asyncio.sleep(3)
                await claim()
            else:
                logger.error(f"Miner status : {cek['message']}")
        elif response.status_code == 200:
            cek = json['data']
            logger.info(f"Mining started. session : {cek['session']}")
            await curext()
        else:
            pass
    except:
        logger.error("Requests error.")
        return await start()
async def checkpoint():
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url['mining_point'], headers=headers)
    try:
        json = response.json()
        json_data = json['data']
        logger.info(f"Score : {json_data['score']} | Points : {json_data['point']}")
    except:
        return await checkpoint()
async def curext():
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url['current_ext'], data=payload, headers=headers)
    try:
        json = response.json()
        data = json['data']
        if data['claim'] == 0:
            logger.debug("Points not ready for claim, Trying to ping")
            for i in range(10):
                await ping()
            return await curext()
        else:
            await claim()
    except:
        return await curext()
async def claim():
    scraper = cloudscraper.create_scraper()
    response = scraper.post(url['claim'], data=payload, headers=headers)
    try:
        json = response.json()
        json_data = json['data']
        logger.info(f"Claimed {json_data['claim']} points.")
        return await start()
    except:
        return await claim()
async def ping():
    scraper = cloudscraper.create_scraper()
    response = scraper.post(url['ping'], data=payload, headers=headers)
    try:
        json = response.json()
        logger.info(f"Ping response : {json['data']}")
        await asyncio.sleep(60)
    except:
        return await ping()
async def main():
    await asyncio.create_task(start())

if __name__ == '__main__':
    asyncio.run(main())
