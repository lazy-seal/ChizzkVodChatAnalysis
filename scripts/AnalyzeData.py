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
    plt.savefig(f"Graphs/{title}_plot")
    plt.clf()

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
    
    chats_per_minute_per_streamer: dict[str, int] = {}
    donation_per_hour: dict[int, int] = defaultdict(int)     # 5000 묶음 당 해당되는 스트리머의 수
    
    for record in res:
        if record['total_chat_count']:
            total_chat_count += record['total_chat_count']#if record['total_chat_count'] else 0
            total_donation_amount += record['total_donation_amount']#if record['total_donation_amount'] else 0
            
            chats_per_minute_per_streamer[record['streamer']] = record['chats_per_minute']
            
            # calculate the wage category the streamer fits in, and then add the count of the category
            dph: float = record['donation_per_hour']
            dph_category: int = int(dph / 5000)
            donation_per_hour[dph_category] += 1

    # pprint(chats_per_minute_per_streamer)
    
    # 채팅 화력
    # simple_bar([i for i in range(len(chats_per_minute_per_streamer))], 
    #             chats_per_minute_per_streamer.values(),
    #             xlabel='스트리머',
    #             ylabel='채팅 화력 (분당 채팅 수)',
    #             title='스트리머별 채팅 화력')
    
    # 평균 시급
    # 5000원 단위로 묶어서 바 그래프로 계산
    max_wage_category = max(donation_per_hour.keys())
    x: list[str] = [f"₩{5000 * i}~\n₩{5000 * (i+1) - 1}" for i in range(0, max_wage_category)]
    y: list[int] = [donation_per_hour[i] for i in range(len(x))]
    print(x)
    print()
    print(y)
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
        await general_statistics_per_streamer(db)
        


    
if __name__ == "__main__":
    # start_date              = datetime(2026, 3, 1)
    # end_date                = datetime(2026, 3, 31)
    st = time.time()
    asyncio.run(main())
    elapsed = time.time() - st
    print(f"Total Execution Time: {int(elapsed // 60)}m {int(elapsed % 60)}s")
    # logger.info(f"Total Execution Time: {int(elapsed // 60)}m {int(elapsed % 60)}s")
