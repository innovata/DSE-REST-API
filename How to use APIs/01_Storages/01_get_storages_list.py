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

# # 모든 스토리지 리스트 가져오기
# res = api.get()
# with open(os.path.join(os.path.dirname(__file__), "Storages List.json"), "w", encoding="utf-8") as f:
#     json.dump(res.json(), f, ensure_ascii=False, indent=2)


# # 스토리지 생성
res = api.create(
    stype="ObjectStorage",
    name="Test01.CreatedByRestAPI",
    description="테스트 후 삭제"
)
with open(os.path.join(os.path.dirname(__file__), "Create A Storage.json"), "w", encoding="utf-8") as f:
    json.dump(res.json(), f, ensure_ascii=False, indent=2)


# # 스토리지 검색-1
# res = api.search_by_name(name="Test01.CreatedByRestAPI", workspace_id="dw-global-000000-default")
# with open(os.path.join(os.path.dirname(__file__), "Search-1 the Storage.json"), "w", encoding="utf-8") as f:
#     json.dump(res.json(), f, ensure_ascii=False, indent=2)



# # 스토리지 검색-2
with open(os.path.join(os.path.dirname(__file__), "Search-1 the Storage.json"), "r", encoding="utf-8") as f:
    info = json.load(f)
    resource_uuid = info['cards'][0]["resourceUUID"]

# res = api.search_by_uuid(resource_uuid=resource_uuid)

# with open(os.path.join(os.path.dirname(__file__), "Search-2 the Storage.json"), "w", encoding="utf-8") as f:
#     json.dump(res.json(), f, ensure_ascii=False, indent=2)


# 스토리지 삭제
res = api.delete(resource_uuid=resource_uuid)
pp.pprint(res.__dict__)
with open(os.path.join(os.path.dirname(__file__), "Delete the Storage.json"), "w", encoding="utf-8") as f:
    json.dump(res.json(), f, ensure_ascii=False, indent=2)



# # 스토리지 업데이트
# res = api.update(resource_uuid)




# # 스토리지 Import
# res = api.import_storage(resource_uuid)



# # 스토리지 Export
# res = api.export_storage(resource_uuid)



# # 스토리지 비움
# res = api.clean_storage(resource_uuid)




# api = ObjectStorage()


# api = SemanticGraphIndex(agent_id, agent_pw)
# api.ingest()