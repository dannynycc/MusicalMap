# -*- coding: utf-8 -*-
"""中國城市 中文→英文 對照（各中國來源 scraper 共用）。

原本 damai / juooo / ypiao / poly 各自帶一份表，內容逐漸漂移（2026-08-12 實測
68 / 36 / 12 / n 個），同一座城市在不同來源會一個出英文、一個出中文——英文站就
直接顯示中文城市名。合成單一權威表後，新增城市只要改這裡一處。

新增城市時：鍵用大麥／聚橙 API 回傳的簡體字面，值用該市通用英文名（漢語拼音，
不含省份後綴）。`scrapers/` 一定在 sys.path（同 _run.py 的 `import usage`），
所以各 scraper 直接 `from _cn_cities import CITY_EN` 即可。
"""

CITY_EN = {
    "北京": "Beijing", "长春": "Changchun", "长沙": "Changsha", "常熟": "Changshu",
    "常州": "Changzhou", "成都": "Chengdu", "重庆": "Chongqing", "慈溪": "Cixi",
    "大连": "Dalian", "大庆": "Daqing", "德州": "Dezhou", "东莞": "Dongguan",
    "佛山": "Foshan", "福州": "Fuzhou", "赣州": "Ganzhou", "广州": "Guangzhou",
    "桂林": "Guilin", "贵阳": "Guiyang", "海口": "Haikou", "杭州": "Hangzhou",
    "哈尔滨": "Harbin", "合肥": "Hefei", "衡阳": "Hengyang", "淮安": "Huai'an",
    "黄冈": "Huanggang", "嘉兴": "Jiaxing", "济南": "Jinan", "晋城": "Jincheng",
    "金华": "Jinhua", "昆明": "Kunming", "昆山": "Kunshan", "廊坊": "Langfang",
    "临平": "Linping", "临沂": "Linyi", "丽水": "Lishui", "柳州": "Liuzhou",
    "马鞍山": "Ma'anshan", "中国澳门": "Macau", "南昌": "Nanchang", "南充": "Nanchong",
    "南京": "Nanjing", "南宁": "Nanning", "南通": "Nantong", "宁波": "Ningbo",
    "鄂尔多斯": "Ordos", "潜江": "Qianjiang", "启东": "Qidong", "青岛": "Qingdao",
    "泉州": "Quanzhou", "衢州": "Quzhou", "上海": "Shanghai", "绍兴": "Shaoxing",
    "沈阳": "Shenyang", "深圳": "Shenzhen", "苏州": "Suzhou", "太原": "Taiyuan",
    "台州": "Taizhou", "泰州": "Taizhou", "天津": "Tianjin", "潍坊": "Weifang",
    "温州": "Wenzhou", "武汉": "Wuhan", "无锡": "Wuxi", "西安": "Xi'an",
    "厦门": "Xiamen", "西宁": "Xining", "徐州": "Xuzhou", "延边": "Yanbian",
    "延吉": "Yanji", "烟台": "Yantai", "银川": "Yinchuan", "张家港": "Zhangjiagang",
    "郑州": "Zhengzhou", "中山": "Zhongshan", "周口": "Zhoukou", "珠海": "Zhuhai",
    "诸暨": "Zhuji", "淄博": "Zibo",
}
