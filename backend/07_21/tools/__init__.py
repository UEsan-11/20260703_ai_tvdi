import json
from .source import Root,AirSite

# 定義絕對路徑
JSON_PATH = Path(__file__).parent.parent / "空氣品質aqi.json"
   
# 所有測站的列表
with open("空氣品質aqi.json",encoding="utf-8") as file:
    data:dict = json.load(file)
contents:list[dict]= data['records']
root = Root(sites=[AirSite(**item) for item in contents])

