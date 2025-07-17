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
res = api.create(
    stype="ObjectStorage",
    name="Test-02.CreatedByRestAPI",
    description="테스트 후 삭제 | 파일 업로드 테스트용"
)
with open(os.path.join(os.path.dirname(__file__), "Create A Storage.json"), "w", encoding="utf-8") as f:
    json.dump(res.json(), f, ensure_ascii=False, indent=2)



from time import sleep 
sleep(5)





api = ObjectStorage()

with open(os.path.join(os.path.dirname(__file__), "Create A Storage.json"), "r", encoding="utf-8") as f:
    info = json.load(f)
    resource_uuid = info["resourceUUID"]

# 파일 업로드
uploading_file = os.path.join(os.path.dirname(__file__), "Create A Storage.json")
res = api.upload(resourceUUID=resource_uuid, file=uploading_file, path=None)
# JSON 데이터 없음
print(res)



# 멀티 파일 업로드
uploading_files = []
_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "01_Storages")
for root, dirs, files in os.walk(_dir):
    for file in files:
        uploading_files.append(os.path.join(root, file))

res_li = api.upload_files(resourceUUID=resource_uuid, files=uploading_files, path=None)
pp.pprint(res_li)



