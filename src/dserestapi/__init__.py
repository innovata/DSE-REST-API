# -*- coding: utf-8 -*-
# DSE(Data Science Experience) APIs 
# https://dsdoc.dsone.3ds.com/devdoccaa/3DEXPERIENCER2024x/en/DSDoc.htm?show=CAADataFactoryStudioWS/datafactorystudio_v1.htm
# REST API functions to interact with 3DS Server related to DSE 



import os, sys 
import pprint 
pp = pprint.PrettyPrinter(indent=2)




import requests
import base64
from pathlib import Path
import threading





############################################################
# 전역변수
############################################################
import json 

try:
    with open(os.environ["CLM_AGENT_CREDENTIAL_PATH"], "r", encoding="utf-8") as f:
        cred = json.load(f)
    agent_id, agent_pw = cred['Agent ID'], cred['Agent Password']
except Exception as e:
    agent_id, agent_pw = os.environ["CLM_AGENT_ID"], os.environ["CLM_AGENT_PASSWORD"]
finally:
    SESS = requests.Session()
    SESS.auth = (agent_id, agent_pw)


try:
    REST_API_URL = os.environ['3DX_PLATFORM_TENANT_URI'] + "/data-factory"
except Exception as e:
    print(f"\nERROR | {e}")






############################################################
# REST APIs
############################################################

def print_response(response):
    print("\n응답코드-->", response.status_code)
    if response.status_code > 399:
        print("\n\n응답코드가 2xx 또는 3xx 대역이 아닐 경우 아래와 같이 표시됩니다-->")
        pp.pprint(response.__dict__)
    return response


class Storages:

    _url = f"{REST_API_URL}/resources/v1/storage"

    # 스토리지 모든 목록 가져오기
    def get(self):
        return SESS.get(self._url)

    # 스토리지 생성
    def create(
        self,
        stype:str, # 스토리지타입: "ObjectStorage", "IndexUnit" 
        name:str,
        description:str="",
        config:dict=None,
    ):

        if stype == 'ObjectStorage':
            config = config if config else {}
        elif stype == 'IndexUnit':
            # SGI 는 반드시 config.datamodel 필드를 추가
            config = config if config else {"datamodel": {}} 

        res = SESS.post(
            self._url,
            json={
                "@class": stype,
                "name": name,
                "description": description,
                "resourceId": name,
                "config": config,
            }
        )
        return print_response(res)

    # 스토리지 검색-1
    def search_by_name(self, name:str, workspace_id:str="dw-global-000000-default"):
        res = SESS.post(
            url=f"{self._url}/filter",
            json={
                "types": [
                    "IndexUnit",
                    "ObjectStorage"
                ],
                "top": 50,
                "skip": 0,
                "nameFilter": name,
                "workspaceId": workspace_id,
            }
        )
        return print_response(res)

    # 스토리지 검색-2
    def search_by_uuid(self, resource_uuid):
        res = SESS.get(
            url=f"{self._url}/{resource_uuid}"
        )
        return print_response(res)
    
    # 스토리지 삭제
    def delete(self, resource_uuid):
        res = SESS.delete(
            url=f"{self._url}/{resource_uuid}"
        )
        return print_response(res)

    # 스토리지 업데이트
    def update(self, resource_uuid):
        res = SESS.put(
            url=f"{self._url}/{resource_uuid}",
            json={

            }
        )
        return print_response(res)
    
    # 스토리지 Import
    def import_storage(self, resource_uuid):
        res = SESS.post(
            url=f"{self._url}/import",
            json={

            }
        )
        return print_response(res)

    # 스토리지 Export
    def export_storage(self, resource_uuid):
        res = SESS.get(
            url=f"{self._url}/{resource_uuid}/export"
        )
        return print_response(res)

    # 스토리지 비움
    def clean_storage(self, resource_uuid):
        res = SESS.get(
            url=f"{self._url}/{resource_uuid}/clear"
        )
        return print_response(res)



from tqdm import tqdm 
from concurrent.futures import ThreadPoolExecutor, as_completed


# 스토리지 타입: ObjectStorageBucket 에 대한 REST API 
class ObjectStorage:

    _url = f"{REST_API_URL}/resources/v1/objectstorage"

    def multicheckin(self, resourceUUID:str):
        res = SESS.post(
            url=f"{self._url}/{resourceUUID}/multicheckin", 
            json={
                'objects': [
                    {
                        "customAttribute": "binary",
                        "correlationId": "correlation01",
                        "id": "test_rest/file1.json"
                    },
                ]
            } 
        )

    def upload(self, resourceUUID:str, file:str, path:str=None, pbar:object=None):
        # DFS 스토리지상의 파일 절대경로
        path = path if path else str(Path(file).as_posix())

        with open(file, 'rb') as f:
            file_content = f.read()
            encoded_content = base64.b64encode(file_content).decode('utf-8')

        res = SESS.post(
            url=f"{self._url}/{resourceUUID}/upload", 
            json={
                "files": [
                    {
                        "id": path, 
                        "filename": os.path.basename(file),
                        "content": encoded_content,
                        "filesize": os.path.getsize(file)
                    }
                ]
            } 
        )
        if pbar:
            pbar.update(1)
        return print_response(res)

    def upload_files_v1(self, resourceUUID:str, files:list, path:list=None):
        with tqdm(total=len(files), desc="DFS에 파일 업로드") as pbar:
            threads = []
            for file in files:
                th = threading.Thread(target=self.upload, args=(resourceUUID, file, path, pbar))
                th.start()
                threads.append(th)

            for th in threads:
                th.join()

    def upload_files(self, resourceUUID:str, files:list, path:list=None):
        response_li = []
        with ThreadPoolExecutor() as executor:
            # 각 파일에 대해 self.upload 작업 스레드에 제출
            futures = [executor.submit(self.upload, resourceUUID, file, path) for file in files]

            # 각 future가 완료되면 결과(response)를 받아 response_li 리스트에 저장
            # tqdm에 total을 전체 작업 개수로 지정
            for future in tqdm(as_completed(futures), total=len(futures), desc="Uploading"):
                response = future.result()
                response_li.append(response)

        return response_li

    def commit(self, resourceUUID:str):
        pass 



def data_transform_01(action:str, data:list)->list:
    jsondata = []
    for d in data:
        jsondata.append({
            "action": action,
            "item": d
        })
    return jsondata 


class SemanticGraphIndex:

    _url = f"{REST_API_URL}/resources/v1/indexunit"

    def ingest(self, resourceUUID:str, data:list):
        res = SESS.post(
            url=f"{self._url}/{resourceUUID}/ingest",
            json=data_transform_01("AddOrReplaceItem", data)
        )
        return print_response(res) 

    def notification(self, resourceUUID):
        res = SESS.get(
            url=f"{self._url}/{resourceUUID}/notification",
        )
        return print_response(res) 

    def validateItemsEvent(self, resourceUUID:str, action:str, data:list):
        res = SESS.post(
            url=f"{self._url}/{resourceUUID}/validateItemsEvent",
            json=data_transform_01(action=action, data=data)
        )
        return print_response(res) 

    def get_uri(self, resourceUUID):
        res = SESS.get(
            url=f"{self._url}/{resourceUUID}/uri",
        )
        return print_response(res)

    def class_count(self, resourceUUID:str, pkg_name:str, class_name_li:list):
        class_name_li = [f"{pkg_name}.{elem}" for elem in class_name_li]
        res = SESS.get(
            url=f"{self._url}/{resourceUUID}/class/count",
            params={'classNameList': class_name_li, 'offset': 0, 'limit':10}
        )
        return print_response(res)

    def get_index(self, sgi_name:str):
        res = SESS.get(
            url=f"{self._url}/name/{sgi_name}"
        )
        return print_response(res) 

    
