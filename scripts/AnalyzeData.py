from DatabaseManagement import localChzzkDbConnection
from datetime import datetime
import time
import asyncio
from asyncpg import Record
from matplotlib import pyplot as plt
from pprint import pprint
import numpy as np
from collections import defaultdict

# @TODO: export each statistics to csv file
    # list of statistics
    # access data through localChzzkDbConnection
    # for each statistics
        # open file
        # write to it

def simple_plot(x, y, xlabel: str, ylabel: str, title:str):
    plt.plot(x, y, 'o')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(f"Graphs/{title}_plot", bbox_inches='tight')
    plt.clf()

def double_bar(x1, x2, height1, height2, width=1.5, xlabel: str = '', ylabel: str = '', title:str = ''):
    plt.bar(x1, height1, width, color='b', edgecolor='k')
    plt.bar(x2, height2, width, color='r', edgecolor='k')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(f"Graphs/{title}_plot", bbox_inches='tight')
    plt.clf()

def simple_bar(x, height, xlabel: str = '', ylabel: str = '', title:str = ''):
    plt.bar(x, height, edgecolor='k')
    plt.xticks(rotation=15)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(f"Graphs/{title}_bar")
    plt.clf()

async def chat_letter_count_compared(db:localChzzkDbConnection):
    query: str = """SELECT SUM(LENGTH(chat_content)) total_letter_count FROM chats;"""
    res: list[Record] = await db.fetch(query)
    total_letter_count = res[0]['total_letter_count']

    shakespeare_letter_count   = 3_695_990
    토지_letter_count           = 3_780_000
    bible_letter_count         = 1_322_532

    n_shakespeare_works    = total_letter_count // shakespeare_letter_count
    n_토지                  = total_letter_count // 토지_letter_count
    n_bible                = total_letter_count // bible_letter_count

    with open('Graphs\\채팅 총량 비교.txt') as f:
        f.write(f'총 채팅 글자수 약 {total_letter_count}자\n')
        f.write(f'모든 셰익스피어 작품의 글자수: 약 {shakespeare_letter_count}자\n')
        f.write(f'토지 글자수 약 {토지_letter_count}자\n')
        f.write(f'성경 글자수 약 {bible_letter_count}자\n')
        f.write(f'셰익스피어 전집 {n_shakespeare_works}번 만들 수 있음\n')
        f.write(f'토지 {n_토지}권\n')
        f.write(f'성경 {n_bible}권\n')
    

async def general_statistics_per_streamer(db:localChzzkDbConnection):
    query: str = """
    SELECT users.user_nickname AS "streamer", res.*
    FROM (
        SELECT 
            video_streamer_id,
            SUM(video_chat_count) AS "total_chat_count", 
            ROUND(AVG(video_chat_count), 2) AS "average_chat_count_per_vid",
            ROUND(SUM(video_chat_count) / (SUM(video_duration) / 60), 2) AS "chats_per_minute",
            SUM(video_total_donation_amount) AS "total_donation_amount", 
            ROUND(SUM(video_total_donation_amount) / (SUM(video_duration) / 360), 2) AS "donation_per_hour",
            ROUND(AVG(video_total_donation_amount), 2) AS "average_donation_per_video",
            ROUND(AVG(video_active_user_count), 2) AS "average_chat_count_per_video"
        FROM videos
        GROUP BY video_streamer_id
        ORDER BY "chats_per_minute" DESC
    ) AS res, users
    WHERE res.video_streamer_id = users.user_id
    """

    res: list[Record] = await db.fetch(query)
    
    total_donation_amount = 0
    total_chat_count = 0
    
    chats_per_minute: dict[int, int] = defaultdict(int)      # 500 묶음당 해당되는 스트리머의 수
    donation_per_hour: dict[int, int] = defaultdict(int)     # 5000 묶음 당 해당되는 스트리머의 수
    
    for record in res:
        if record['total_chat_count']:
            total_chat_count += record['total_chat_count']#if record['total_chat_count'] else 0
            total_donation_amount += record['total_donation_amount']#if record['total_donation_amount'] else 0
            
            # calculate the cpm (chats_per_minute) category the streamer fits in, and then add the count of the category
            cpm: float = record['chats_per_minute']
            cpm_category: int = int(cpm / 50)
            chats_per_minute[cpm_category] += 1
            
            # calculate the wage category the streamer fits in, and then add the count of the category
            dph: float = record['donation_per_hour']
            dph_category: int = int(dph / 5000)
            donation_per_hour[dph_category] += 1

    
    # 채팅 화력
    # 50cpm 단위로 묶어서 바 그래프로 계산
    max_chat_category = max(chats_per_minute.keys())
    x: list[str] = [f"{50*i}~{50*(i+1)-1}" for i in range(0, max_chat_category)]
    y: list[int] = [chats_per_minute[i] for i in range(len(x))]
    simple_bar(x, y,
               xlabel='분당 채팅 수',
               ylabel='스트리머 수',
               title='채팅 화력 (평균 분당 채팅 수)')
    
    # 평균 시급
    # 5000원 단위로 묶어서 바 그래프로 계산
    max_wage_category = max(donation_per_hour.keys())
    x: list[str] = [f"₩{5000 * i}~\n₩{5000 * (i+1) - 1}" for i in range(0, max_wage_category)]
    y: list[int] = [donation_per_hour[i] for i in range(len(x))]
    simple_bar(x, y, 
               xlabel='시간당 도네이션',
               ylabel='스트리머 수',
               title='시급별 스트리머 수')
    
    # 채팅 화력과 평균 시급의 상관관계

    
async def user_similarity_diagram(db:localChzzkDbConnection):
    # euler radius
    raise NotImplementedError
    query: str = """
    """

    res: list[Record] = await db.fetch(query)
    for record in res:
        for key, value in record.items():
            print(f"{key} = {value}")
        print()
    # plt.plot()
        
async def main():
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False  # keeps minus signs from rendering as boxes
    is_testing = False
    async with localChzzkDbConnection(is_testing) as db:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(general_statistics_per_streamer(db))
            tg.create_task(chat_letter_count_compared(db))
        


    
if __name__ == "__main__":
    # start_date              = datetime(2026, 3, 1)
    # end_date                = datetime(2026, 3, 31)
    st = time.time()
    asyncio.run(main())
    elapsed = time.time() - st
    print(f"Total Execution Time: {int(elapsed // 60)}m {int(elapsed % 60)}s")
    # logger.info(f"Total Execution Time: {int(elapsed // 60)}m {int(elapsed % 60)}s")
