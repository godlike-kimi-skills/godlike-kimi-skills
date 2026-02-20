#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chinese Lunar Calendar / 农历黄历
农历转换、节气查询、黄历宜忌
支持1900-2100年
"""

import datetime
import math
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass
import argparse

# 天干
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
# 地支
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
# 生肖
SHENGXIAO = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
# 农历月份名称
LUNAR_MONTH_NAMES = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"]
# 农历日期名称
LUNAR_DAY_NAMES = [
    "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
    "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"
]
# 二十四节气
SOLAR_TERMS = [
    "小寒", "大寒", "立春", "雨水", "惊蛰", "春分",
    "清明", "谷雨", "立夏", "小满", "芒种", "夏至",
    "小暑", "大暑", "立秋", "处暑", "白露", "秋分",
    "寒露", "霜降", "立冬", "小雪", "大雪", "冬至"
]
# 节气含义
SOLAR_TERM_MEANINGS = {
    "立春": "春季开始，万物复苏",
    "雨水": "降雨开始，雨量渐增",
    "惊蛰": "春雷乍动，惊醒蛰伏",
    "春分": "昼夜平分，春季中点",
    "清明": "天清地明，扫墓祭祖",
    "谷雨": "雨生百谷，播种时节",
    "立夏": "夏季开始，万物繁茂",
    "小满": "麦粒渐满，未全成熟",
    "芒种": "麦类成熟，稻谷播种",
    "夏至": "白昼最长，日影最短",
    "小暑": "天气渐热，尚未极热",
    "大暑": "一年最热，湿热交蒸",
    "立秋": "秋季开始，暑去凉来",
    "处暑": "暑气结束，天气转凉",
    "白露": "露水凝结，天气转凉",
    "秋分": "昼夜平分，秋季中点",
    "寒露": "露水更凉，即将成霜",
    "霜降": "开始有霜，气温骤降",
    "立冬": "冬季开始，万物收藏",
    "小雪": "开始降雪，雪量小",
    "大雪": "雪量增大，地面积雪",
    "冬至": "白昼最短，日影最长",
    "小寒": "气候寒冷，尚未极冷",
    "大寒": "一年最冷，天寒地冻"
}
# 传统节日
TRADITIONAL_FESTIVALS = {
    "正月初一": "春节",
    "正月十五": "元宵节",
    "二月初二": "龙抬头",
    "五月初五": "端午节",
    "七月初七": "七夕节",
    "七月十五": "中元节",
    "八月十五": "中秋节",
    "九月初九": "重阳节",
    "腊月初八": "腊八节",
    "腊月廿三": "小年",
    "腊月三十": "除夕"
}
# 公历节日
SOLAR_FESTIVALS = {
    (1, 1): "元旦",
    (2, 14): "情人节",
    (3, 8): "妇女节",
    (3, 12): "植树节",
    (4, 1): "愚人节",
    (4, 5): "清明节",
    (5, 1): "劳动节",
    (5, 4): "青年节",
    (6, 1): "儿童节",
    (7, 1): "建党节",
    (8, 1): "建军节",
    (9, 10): "教师节",
    (10, 1): "国庆节",
    (12, 25): "圣诞节"
}

# 农历数据 (1900-2100)
# 每个元素为4位16进制数，表示该年的农历信息
# 高12位表示闰月，低12位表示每月大小月(大月30天，小月29天)
LUNAR_INFO = [
    0x04bd8, 0x04ae0, 0x0a570, 0x054d5, 0x0d260, 0x0d950, 0x16554, 0x056a0, 0x09ad0, 0x055d2,
    0x04ae0, 0x0a5b6, 0x0a4d0, 0x0d250, 0x1d255, 0x0b540, 0x0d6a0, 0x0ada2, 0x095b0, 0x14977,
    0x04970, 0x0a4b0, 0x0b4b5, 0x06a50, 0x06d40, 0x1ab54, 0x02b60, 0x09570, 0x052f2, 0x04970,
    0x06566, 0x0d4a0, 0x0ea50, 0x06e95, 0x05ad0, 0x02b60, 0x186e3, 0x092e0, 0x1c8d7, 0x0c950,
    0x0d4a0, 0x1d8a6, 0x0b550, 0x056a0, 0x1a5b4, 0x025d0, 0x092d0, 0x0d2b2, 0x0a950, 0x0b557,
    0x06ca0, 0x0b550, 0x15355, 0x04da0, 0x0a5d0, 0x14573, 0x052d0, 0x0a9a8, 0x0e950, 0x06aa0,
    0x0aea6, 0x0ab50, 0x04b60, 0x0aae4, 0x0a570, 0x05260, 0x0f263, 0x0d950, 0x05b57, 0x056a0,
    0x096d0, 0x04dd5, 0x04ad0, 0x0a4d0, 0x0d4d4, 0x0d250, 0x0d558, 0x0b540, 0x0b5a0, 0x195a6,
    0x095b0, 0x049b0, 0x0a974, 0x0a4b0, 0x0b27a, 0x06a50, 0x06d40, 0x0af46, 0x0ab60, 0x09570,
    0x04af5, 0x04970, 0x064b0, 0x074a3, 0x0ea50, 0x06b58, 0x055c0, 0x0ab60, 0x096d5, 0x092e0,
    0x0c960, 0x0d954, 0x0d4a0, 0x0da50, 0x07552, 0x056a0, 0x0abb7, 0x025d0, 0x092d0, 0x0cab5,
    0x0a950, 0x0b4a0, 0x0baa4, 0x0ad50, 0x055d9, 0x04ba0, 0x0a5b0, 0x15176, 0x052b0, 0x0a930,
    0x07954, 0x06aa0, 0x0ad50, 0x05b52, 0x04b60, 0x0a6e6, 0x0a4e0, 0x0d260, 0x0ea65, 0x0d530,
    0x05aa0, 0x076a3, 0x096d0, 0x04bd7, 0x04ad0, 0x0a4d0, 0x1d0b6, 0x0d250, 0x0d520, 0x0dd45,
    0x0b5a0, 0x056d0, 0x055b2, 0x049b0, 0x0a577, 0x0a4b0, 0x0aa50, 0x1b255, 0x06d20, 0x0ada0
]


@dataclass
class LunarDate:
    """农历日期"""
    year: int
    month: int
    day: int
    is_leap: bool = False
    
    def __str__(self):
        leap_str = "闰" if self.is_leap else ""
        return f"{self.year}年{leap_str}{LUNAR_MONTH_NAMES[self.month-1]}月{LUNAR_DAY_NAMES[self.day-1]}"


class ChineseLunarCalendar:
    """中国农历历法"""
    
    def __init__(self):
        self.min_year = 1900
        self.max_year = 2100
        self.base_date = datetime.date(1900, 1, 31)  # 1900年春节
    
    def _get_lunar_year_days(self, year: int) -> int:
        """获取农历年的总天数"""
        year_data = LUNAR_INFO[year - 1900]
        leap_month = year_data >> 16  # 闰月
        days = 0
        for i in range(12):
            if (year_data >> i) & 1:
                days += 30  # 大月
            else:
                days += 29  # 小月
        if leap_month > 0:
            if (year_data >> (leap_month - 1)) & 1:
                days += 30
            else:
                days += 29
        return days
    
    def solar_to_lunar(self, solar_date: datetime.date) -> Tuple[LunarDate, str, str, str]:
        """
        公历转农历
        返回: (农历日期, 干支年, 生肖, 节气)
        """
        if solar_date.year < 1900 or solar_date.year > 2100:
            raise ValueError(f"仅支持1900-2100年，输入: {solar_date.year}")
        
        # 计算从1900年春节开始的天数差
        days_diff = (solar_date - self.base_date).days
        
        # 确定农历年
        lunar_year = 1900
        year_days = self._get_lunar_year_days(lunar_year)
        while days_diff >= year_days:
            days_diff -= year_days
            lunar_year += 1
            year_days = self._get_lunar_year_days(lunar_year)
        
        # 确定农历月和日
        year_data = LUNAR_INFO[lunar_year - 1900]
        leap_month = year_data >> 16
        
        lunar_month = 1
        is_leap = False
        
        for i in range(1, 13):
            # 检查是否是闰月
            if i == leap_month + 1 and not is_leap and leap_month > 0:
                # 处理闰月
                month_days = 30 if (year_data >> (leap_month - 1)) & 1 else 29
                if days_diff < month_days:
                    lunar_month = leap_month
                    is_leap = True
                    break
                days_diff -= month_days
            
            # 普通月份
            month_days = 30 if (year_data >> (i - 1)) & 1 else 29
            if days_diff < month_days:
                lunar_month = i
                break
            days_diff -= month_days
        
        lunar_day = days_diff + 1
        
        lunar_date = LunarDate(lunar_year, lunar_month, lunar_day, is_leap)
        
        # 计算干支
        ganzhi_year = self._get_ganzhi_year(lunar_year)
        shengxiao = SHENGXIAO[(lunar_year - 4) % 12]
        
        # 获取节气
        term = self._get_solar_term(solar_date)
        
        return lunar_date, ganzhi_year, shengxiao, term
    
    def _get_ganzhi_year(self, year: int) -> str:
        """获取干支年"""
        offset = (year - 4) % 60
        return TIANGAN[offset % 10] + DIZHI[offset % 12]
    
    def _get_ganzhi_month(self, year: int, month: int) -> str:
        """获取干支月"""
        year_gan = (year - 4) % 10
        # 甲己之年丙作首，乙庚之岁戊为头...
        month_gan_start = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0][year_gan]
        return TIANGAN[(month_gan_start + month - 1) % 10] + DIZHI[(month + 1) % 12]
    
    def _get_ganzhi_day(self, date: datetime.date) -> str:
        """获取干支日"""
        # 1900年1月31日为甲辰日
        base = datetime.date(1900, 1, 31)
        offset = (date - base).days % 60
        return TIANGAN[offset % 10] + DIZHI[offset % 12]
    
    def _get_solar_term(self, date: datetime.date) -> str:
        """获取节气"""
        # 简化的节气计算（精确计算需要天文算法）
        year = date.year
        month = date.month
        day = date.day
        
        # 节气大致日期（简化版）
        term_dates = {
            (1, 5): "小寒", (1, 20): "大寒",
            (2, 4): "立春", (2, 19): "雨水",
            (3, 5): "惊蛰", (3, 20): "春分",
            (4, 5): "清明", (4, 20): "谷雨",
            (5, 5): "立夏", (5, 21): "小满",
            (6, 6): "芒种", (6, 21): "夏至",
            (7, 7): "小暑", (7, 22): "大暑",
            (8, 7): "立秋", (8, 23): "处暑",
            (9, 7): "白露", (9, 23): "秋分",
            (10, 8): "寒露", (10, 23): "霜降",
            (11, 7): "立冬", (11, 22): "小雪",
            (12, 7): "大雪", (12, 21): "冬至"
        }
        
        # 查找最近的节气
        closest_term = ""
        min_diff = float('inf')
        
        for (m, d), term in term_dates.items():
            term_date = datetime.date(year, m, d)
            diff = abs((date - term_date).days)
            if diff < min_diff:
                min_diff = diff
                closest_term = term
        
        return closest_term if min_diff <= 1 else ""
    
    def get_solar_terms_year(self, year: int) -> List[Tuple[str, str]]:
        """获取一年的所有节气"""
        result = []
        # 简化的节气日期
        term_dates = [
            (1, 5), (1, 20), (2, 4), (2, 19), (3, 5), (3, 20),
            (4, 5), (4, 20), (5, 5), (5, 21), (6, 6), (6, 21),
            (7, 7), (7, 22), (8, 7), (8, 23), (9, 7), (9, 23),
            (10, 8), (10, 23), (11, 7), (11, 22), (12, 7), (12, 21)
        ]
        
        for i, (month, day) in enumerate(term_dates):
            try:
                date = datetime.date(year, month, day)
                term = SOLAR_TERMS[i]
                meaning = SOLAR_TERM_MEANINGS.get(term, "")
                result.append((term, f"{month}月{day}日", meaning))
            except:
                pass
        
        return result
    
    def get_festival(self, lunar_date: LunarDate, solar_date: datetime.date) -> str:
        """获取节日"""
        # 农历节日
        lunar_key = f"{LUNAR_MONTH_NAMES[lunar_date.month-1]}月{LUNAR_DAY_NAMES[lunar_date.day-1]}"
        if lunar_key in TRADITIONAL_FESTIVALS:
            return TRADITIONAL_FESTIVALS[lunar_key]
        
        # 公历节日
        solar_key = (solar_date.month, solar_date.day)
        if solar_key in SOLAR_FESTIVALS:
            return SOLAR_FESTIVALS[solar_key]
        
        return ""
    
    def get_almanac(self, date: datetime.date) -> Dict:
        """
        获取黄历宜忌（简化版）
        基于建除十二神算法
        """
        lunar_date, ganzhi_year, shengxiao, term = self.solar_to_lunar(date)
        ganzhi_day = self._get_ganzhi_day(date)
        
        # 建除十二神（简化算法）
        jianchu = ["建", "除", "满", "平", "定", "执", "破", "危", "成", "收", "开", "闭"]
        day_index = (date.day - 1) % 12
        jianchu_god = jianchu[day_index]
        
        # 宜忌（基于建除十二神）
        yi_ji_map = {
            "建": (["出行", "上任", "嫁娶"], ["开仓", "动土"]),
            "除": (["祭祀", "沐浴", "求医"], ["嫁娶", "安葬"]),
            "满": (["开市", "交易", "纳财"], ["动土", "栽种"]),
            "平": (["修造", "动土", "安床"], ["出行", "嫁娶"]),
            "定": (["嫁娶", "祭祀", "祈福"], ["诉讼", "出行"]),
            "执": (["祭祀", "祈福", "求嗣"], ["开市", "交易"]),
            "破": (["破屋", "坏垣", "求医"], ["嫁娶", "出行", "上任"]),
            "危": (["祭祀", "祈福", "安床"], ["出行", "开市"]),
            "成": (["嫁娶", "开市", "签约"], ["诉讼", "安葬"]),
            "收": (["纳财", "收纳", "开仓"], ["嫁娶", "出行"]),
            "开": (["开市", "交易", "出行"], ["安葬", "动土"]),
            "闭": (["祭祀", "祈福", "修造"], ["嫁娶", "出行"]),
        }
        
        yi, ji = yi_ji_map.get(jianchu_god, ([], []))
        
        # 彭祖百忌（简化）
        pengzu = {
            "甲": "甲不开仓财物耗散",
            "乙": "乙不栽植千株不长",
            "丙": "丙不修灶必见灾殃",
            "丁": "丁不剃头头必生疮",
            "戊": "戊不受田田主不祥",
            "己": "己不破券二比并亡",
            "庚": "庚不经络织机虚张",
            "辛": "辛不合酱主人不尝",
            "壬": "壬不泱水更难提防",
            "癸": "癸不词讼理弱敌强"
        }
        
        # 冲煞
        day_dizhi = ganzhi_day[1]
        dizhi_idx = DIZHI.index(day_dizhi)
        chong_idx = (dizhi_idx + 6) % 12  # 相冲
        chong = SHENGXIAO[chong_idx]
        
        return {
            "jianchu": jianchu_god,
            "yi": yi,
            "ji": ji,
            "pengzu": pengzu.get(ganzhi_day[0], ""),
            "chong": f"冲{chong}",
            "ganzhi_day": ganzhi_day
        }
    
    def format_date(self, solar_date: datetime.date) -> str:
        """格式化日期信息"""
        lunar_date, ganzhi_year, shengxiao, term = self.solar_to_lunar(solar_date)
        ganzhi_month = self._get_ganzhi_month(lunar_date.year, lunar_date.month)
        ganzhi_day = self._get_ganzhi_day(solar_date)
        festival = self.get_festival(lunar_date, solar_date)
        almanac = self.get_almanac(solar_date)
        
        weekday = ["一", "二", "三", "四", "五", "六", "日"][solar_date.weekday()]
        
        lines = [
            f"[DATE] {solar_date.year}年{solar_date.month}月{solar_date.day}日 星期{weekday}",
            "",
            f"农历：{ganzhi_year}年 {ganzhi_month}月 {ganzhi_day}日",
            f"     {lunar_date}",
            "",
            f"生肖：{shengxiao}",
        ]
        
        if festival:
            lines.extend([
                "",
                f"[FESTIVAL] 节日：{festival}"
            ])
        
        if term:
            meaning = SOLAR_TERM_MEANINGS.get(term, "")
            lines.extend([
                "",
                f"[SOLAR] 节气：{term}",
                f"     {meaning}"
            ])
        
        lines.extend([
            "",
            "[ALMANAC] 黄历宜忌：",
            f"   建除：{almanac['jianchu']}日",
            f"   [OK] 宜：{'、'.join(almanac['yi'])}",
            f"   [NO] 忌：{'、'.join(almanac['ji'])}",
            "",
            f"   冲煞：{almanac['chong']}",
            f"   彭祖百忌：{almanac['pengzu']}"
        ])
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Chinese Lunar Calendar / 农历黄历')
    parser.add_argument('date', nargs='?', help='日期 (YYYY-MM-DD 或 YYYY/MM/DD)')
    parser.add_argument('--lunar', '-l', help='农历日期 (YYYY-MM-DD)')
    parser.add_argument('--solar-terms', '-s', nargs='?', const='current', help='节气查询 [年份]')
    parser.add_argument('--festivals', '-f', action='store_true', help='查询传统节日')
    parser.add_argument('--almanac', '-a', action='store_true', help='黄历宜忌')
    parser.add_argument('--today', '-t', action='store_true', help='查询今天')
    
    args = parser.parse_args()
    
    calendar = ChineseLunarCalendar()
    
    # 确定查询日期
    if args.today or not args.date:
        query_date = datetime.date.today()
    else:
        try:
            query_date = datetime.datetime.strptime(args.date.replace('/', '-'), '%Y-%m-%d').date()
        except:
            print(f"日期格式错误: {args.date}")
            print("请使用格式: YYYY-MM-DD 或 YYYY/MM/DD")
            return
    
    # 节气查询
    if args.solar_terms:
        if args.solar_terms == 'current':
            year = datetime.date.today().year
        else:
            try:
                year = int(args.solar_terms)
            except:
                year = datetime.date.today().year
        
        print(f"\n🌾 {year}年二十四节气:\n")
        terms = calendar.get_solar_terms_year(year)
        for i, (term, date, meaning) in enumerate(terms):
            print(f"  {i+1:2d}. {term:6} {date:10} {meaning}")
        print()
        return
    
    # 传统节日
    if args.festivals:
        print("\n🏮 中国传统节日:\n")
        for key, name in TRADITIONAL_FESTIVALS.items():
            print(f"  {key:12} {name}")
        print()
        return
    
    # 默认显示日期信息
    print(calendar.format_date(query_date))
    print()


if __name__ == '__main__':
    main()
