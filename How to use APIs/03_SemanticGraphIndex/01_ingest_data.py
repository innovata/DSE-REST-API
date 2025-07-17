# -*- coding: utf-8 -*-


# 환경셋업
# 방법-1: pip install dserestapi 

# 방법-2: 패키지경로 추가
import os, sys 
sys.path.append(r"D:\pypjts\DSE-REST-API\src")




import json 

credential = r"D:\__ENGINEER_DRIVE__\__CREDENTIALS__\3DEXPREIENCE Platform\CLM Agent\JLE69_GMAIL\CML-Agent ID-PW.json"
with open(credential, "r", encoding='utf-8') as f:
    cred = json.load(f)


import pprint
pp = pprint.PrettyPrinter(indent=2)



####################################################################################################
# 사용 예제 
####################################################################################################


os.environ["CLM_AGENT_ID"] = cred['Agent ID']
os.environ["CLM_AGENT_PASSWORD"] = cred['Agent Password']
os.environ['3DX_PLATFORM_TENANT_URI'] = "https://r1132100527066-apk2-sgi.3dexperience.3ds.com:443"


from dserestapi import Storages, ObjectStorage, SemanticGraphIndex


api = Storages()

# 스토리지 생성
data_modeling_config = {
    "datamodel": {
        "classes": [
            {
                "name": "DummyData",
                "parents": [],
                "pkg": "Rawdata",
                "attributes": [
                    {
                        "name": "seq",
                        "type": {
                            "dataType": "Integer",
                            "dataStructure": "Singleton"
                        },
                        "annotation": {}
                    },
                    {
                        "name": "title",
                        "type": {
                            "dataType": "String",
                            "dataStructure": "Singleton"
                        },
                        "annotation": {}
                    },
                    {
                        "name": "_text",
                        "type": {
                            "dataType": "String",
                            "dataStructure": "Singleton"
                        },
                        "annotation": {}
                    }
                ]
            }
        ]
    }
}

# res = api.create(
#     stype="IndexUnit",
#     name="TestSGI_01_CreatedByRestAPI",
#     description="테스트 후 삭제 | SGI 데이터 모델링 테스트",
#     config=data_modeling_config
# )
# with open(os.path.join(os.path.dirname(__file__), "Create A SGI.json"), "w", encoding="utf-8") as f:
#     json.dump(res.json(), f, ensure_ascii=False, indent=2)



# from time import sleep 
# sleep(5)



sgi = SemanticGraphIndex()



res = sgi.get_index(sgi_name="TestSGI_01_CreatedByRestAPI")
with open(os.path.join(os.path.dirname(__file__), "Get an Index.json"), "w", encoding="utf-8") as f:
    json.dump(res.json(), f, ensure_ascii=False, indent=2)

sgi_info = res.json()
resource_uuid = sgi_info["resourceUUID"]



# # 데이터 주입/적재 
# data = [{
#     "class": "Rawdata.DummyData",
#     "seq": 1,
#     "title": "This is a title",
#     "_text": "bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla~"
# }]
# res = sgi.ingest(resourceUUID=resource_uuid, data=data)
# with open(os.path.join(os.path.dirname(__file__), "Ingest Data.json"), "w", encoding="utf-8") as f:
#     json.dump(res.json(), f, ensure_ascii=False, indent=2)



res = sgi.validateItemsEvent(resourceUUID=resource_uuid)
with open(os.path.join(os.path.dirname(__file__), "Validation Items.json"), "w", encoding="utf-8") as f:
    json.dump(res.json(), f, ensure_ascii=False, indent=2)



res = sgi.get_uri(resourceUUID=resource_uuid)
with open(os.path.join(os.path.dirname(__file__), "SGI URI.json"), "w", encoding="utf-8") as f:
    json.dump(res.json(), f, ensure_ascii=False, indent=2)



res = sgi.notification(resourceUUID=resource_uuid)
with open(os.path.join(os.path.dirname(__file__), "Notification.json"), "w", encoding="utf-8") as f:
    json.dump(res.json(), f, ensure_ascii=False, indent=2)



res = sgi.class_count(resourceUUID=resource_uuid, pkg_name="Rawdata", class_name_li=["DummyData"])
with open(os.path.join(os.path.dirname(__file__), "Class Count.json"), "w", encoding="utf-8") as f:
    json.dump(res.json(), f, ensure_ascii=False, indent=2)



