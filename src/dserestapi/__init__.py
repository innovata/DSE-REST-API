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
    # print("\n응답코드-->", response.status_code)
    if response.status_code >= 400:
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
        project_id:str=None,
        workspace_id:str=None,
        config:dict=None
    ):

        # config 핸들러
        if stype == 'ObjectStorage':
            config = config if config else {}
        elif stype == 'IndexUnit':
            # SGI 는 반드시 config.datamodel 필드를 추가
            config = config if config else {"datamodel": {}} 

        params = {
            "@class": stype,
            "name": name,
            "description": description,
            "resourceId": name,
            "config": config,
        }

        if project_id:
            params.update({"projectId": project_id})

        if workspace_id:
            params.update({"workspaceId": workspace_id})


        res = SESS.post(self._url, json=params)
        return print_response(res)

    # 스토리지 검색-1
    def search_by_name(self, name:str, workspace_id="dw-global-000000-default"):
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
    def import_(self, payload:dict):
        res = SESS.post(
            url=f"{self._url}/import",
            json=payload
        )
        return print_response(res)

    # 스토리지 Export Config 
    def export_(self, resource_uuid):
        res = SESS.get(
            url=f"{self._url}/{resource_uuid}/export"
        )
        return print_response(res)

    # 스토리지 비움
    def clear(self, resource_uuid):
        res = SESS.patch(
            url=f"{self._url}/{resource_uuid}/clear"
        )
        return print_response(res)



def delete_sgi(workspace_id:str, sgi_name:str):
    api = Storages()
    res = api.search_by_name(sgi_name, workspace_id)
    cards = res.json()["cards"]
    print(f"\nSGI 정보검색-->")
    pp.pprint(cards)
    if len(cards) == 1:
        uuid = cards[0]["resourceUUID"]
        api.delete(uuid)





from tqdm import tqdm 
from concurrent.futures import ThreadPoolExecutor, as_completed


# 스토리지 타입: ObjectStorageBucket 에 대한 REST API 
class ObjectStorage:

    _url = f"{REST_API_URL}/resources/v1/objectstorage"

    def multicheckin(self, resource_uuid:str):
        res = SESS.post(
            url=f"{self._url}/{resource_uuid}/multicheckin", 
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

    def upload(self, resource_uuid:str, file:str, path:str=None, pbar:object=None):
        filename = os.path.basename(file)
        
        # DFS 스토리지상의 파일 절대경로
        dfs_abspath = os.path.join(path, filename) if path else str(Path(file).as_posix())

        with open(file, 'rb') as f:
            file_content = f.read()
            encoded_content = base64.b64encode(file_content).decode('utf-8')

        res = SESS.post(
            url=f"{self._url}/{resource_uuid}/upload", 
            json={
                "files": [
                    {
                        "id": dfs_abspath, 
                        "filename": filename,
                        "content": encoded_content,
                        "filesize": os.path.getsize(file)
                    }
                ]
            } 
        )
        if pbar:
            pbar.update(1)
        return print_response(res)

    def upload_files_v1(self, resource_uuid:str, files:list, path:list=None):
        with tqdm(total=len(files), desc="DFS에 파일 업로드") as pbar:
            threads = []
            for file in files:
                th = threading.Thread(target=self.upload, args=(resource_uuid, file, path, pbar))
                th.start()
                threads.append(th)

            for th in threads:
                th.join()

    def upload_files(self, resource_uuid:str, files:list, path:list=None):
        response_li = []
        with ThreadPoolExecutor() as executor:
            # 각 파일에 대해 self.upload 작업 스레드에 제출
            futures = [executor.submit(self.upload, resource_uuid, file, path) for file in files]

            # 각 future가 완료되면 결과(response)를 받아 response_li 리스트에 저장
            # tqdm에 total을 전체 작업 개수로 지정
            for future in tqdm(as_completed(futures), total=len(futures), desc="Uploading"):
                response = future.result()
                response_li.append(response)

        return response_li

    def commit(self, resource_uuid:str):
        pass 



def gen_JsonEventData(action:str, data:list)->list:
    jsondata = []
    for d in data:
        jsondata.append({
            "action": action,
            "item": d
        })
    return jsondata 


class SemanticGraphIndex:

    _url = f"{REST_API_URL}/resources/v1/indexunit"

    def ingest(self, resource_uuid:str, data:list):
        res = SESS.post(
            url=f"{self._url}/{resource_uuid}/ingest",
            json=data
        )
        return print_response(res) 

    def notification(self, resource_uuid):
        res = SESS.get(
            url=f"{self._url}/{resource_uuid}/notification",
        )
        return print_response(res) 

    def validateItemsEvent(self, resource_uuid:str, action:str, data:list):
        res = SESS.post(
            url=f"{self._url}/{resource_uuid}/validateItemsEvent",
            json=gen_JsonEventData(action=action, data=data)
        )
        return print_response(res) 

    def get_uri(self, resource_uuid):
        res = SESS.get(
            url=f"{self._url}/{resource_uuid}/uri",
        )
        return print_response(res)

    def class_count(self, resource_uuid:str, pkg_name:str, class_name_li:list):
        class_name_li = [f"{pkg_name}.{elem}" for elem in class_name_li]
        res = SESS.get(
            url=f"{self._url}/{resource_uuid}/class/count",
            params={'classNameList': class_name_li, 'offset': 0, 'limit':10}
        )
        return print_response(res)

    def get_index(self, sgi_name:str):
        res = SESS.get(
            url=f"{self._url}/name/{sgi_name}"
        )
        return print_response(res) 



"""
응답코드가 2xx 또는 3xx 대역이 아닐 경우 아래와 같이 표시됩니다-->
{ '_content': b'{"type":"about:blank","title":"Payload Too Large","status":4'
              b'13,"detail":"Index unit ingestion input event list is too la'
              b'rge. Max events is 50000 and current value is java.util.stre'
              b'am.ReferencePipeline$Head@2c728462 Index unit ingestion inpu'
              b't event list is too large. Max events is 50000 and current v'
              b'alue is java.util.stream.ReferencePipeline$Head@2c728462","i'
              b'nstance":"/data-factory/api/1/indexunit/4328c165-f473-477d-8'
              b'a79-9885ebcd8008/ingest"}',
  '_content_consumed': True,
  '_next': None,
  'connection': <requests.adapters.HTTPAdapter object at 0x000001A91B8C5F70>,
  'cookies': <RequestsCookieJar[]>,
  'elapsed': datetime.timedelta(seconds=4, microseconds=23094),
  'encoding': None,
  'headers': {'content-type': 'application/problem+json', 'transfer-encoding': 'chunked', 'date': 'Mon, 22 Sep 2025 06:29:11 GMT', 'server': 'Microsoft-IIS/7.0'},
  'history': [],
  'raw': <urllib3.response.HTTPResponse object at 0x000001A94CFD0F70>,
  'reason': 'Request Entity Too Large',
  'request': <PreparedRequest [POST]>,
  'status_code': 413,
  'url': 'https://r1132100527066-apk2-sgi.3dexperience.3ds.com:443/data-factory/resources/v1/indexunit/4328c165-f473-477d-8a79-9885ebcd8008/ingest'}
"""



############################################################
# SGI 모델 정의 및 데이터 업로더 
############################################################

from tqdm import tqdm 
from ipylib.ilist import split_data

# 'SGI 한개'에 대해 모델링 & 데이터 관리 | 멀티 클래스 핸들링 
class SGIModeler:

    def __init__(self, project_id, workspace_id, sgi_name, sgi_desc="", creator="jle69_gmail", dbg_mode=False):
        self.creator = creator 
        self.project_id = project_id 
        self.workspace_id = workspace_id

        self.sgi_name = sgi_name
        self.sgi_desc = sgi_desc
        self._cls_li = [] # [{클래스명: SGIClass객체}]


        self._dbg_mode = dbg_mode 

    # 한 개 클래스&프로퍼티 정의 
    def modeling_a_class(self, pkg_name, cls_name, data, dtypemap:dict=None):
        if len(data) > 0:
            # 클래스에 대한 스키마 정의 | Property 정의
            cls = SGIClass(pkg_name=pkg_name, cls_name=cls_name, dtypemap=dtypemap)
            cls.create_class_conf(data)

            print(f"\nSGI클래스 신규생성 모델링정보-->")
            pp.pprint(cls.creatable_class_conf)

            # 클래스 저장 
            self._cls_li.append(cls)
        else:
            print(f"\nERROR | {[pkg_name, cls_name]} | 데이터가 없으면 모델링할 수 없습니다.")
        
        return self
    
    def create_sgi_define_classes(self):
        if len(self._cls_li) > 0:
            data_modeling_conf = {
                "datamodel": {
                    "classes": [cls.creatable_class_conf for cls in self._cls_li]
                }
            }
            if self._dbg_mode:
                print(f"\nSGI생성시 클래스 모델링 Conf.-->")
                pp.pprint(data_modeling_conf)


            res = Storages().create(
                stype="IndexUnit",
                name=self.sgi_name,
                description=self.sgi_desc,
                project_id=self.project_id,
                workspace_id=self.workspace_id,
                config=data_modeling_conf
            )

            if res.status_code >= 200 and res.status_code < 300:
                print("\nSGI Modeling SUCCESS.", [res, self.sgi_name, self.workspace_id])
                return res.json()
            else: 
                print(f"\nSGI Modeling FAIL.", [res, self.sgi_name, self.workspace_id])
                pp.pprint(res.json())
                print(f"\nSGI 모델링 CONFIG-->")
                pp.pprint(data_modeling_conf)
        else:
            print(f"\nERROR | 클래스&프로퍼티를 먼저 정의하세요.")

    # 기존 SGI에 클래스들을 추가 정의한다
    def add_classes_definition(self, resource_uuid:str):
        if len(self._cls_li) > 0:
            data_modeling_conf = [cls.addable_class_conf for cls in self._cls_li]
            
            if self._dbg_mode:
                print(f"\nSGI클래스 추가 모델링정보-->")
                pp.pprint(data_modeling_conf)
        
            self._upload(resource_uuid, data_modeling_conf)
        else:
            print(f"\nERROR | 클래스&프로퍼티를 먼저 정의하세요.")
    
    # 한 개 클래스의 실데이터를 업로드 
    def upload_data(self, pkg_name, cls_name, data, resource_uuid:str):
        cls = SGIClass(pkg_name=pkg_name, cls_name=cls_name)
        # 클래스의 데이터를 Conf 로 변환
        cls.create_data_conf(data)

        # 5만 라인씩 데이터 분리 
        dataset = split_data(data=cls.data_conf, size=5*pow(10,4))

        # 업로드 
        with tqdm(total=len(dataset), desc="실데이터 업로드중(5만 라인씩)") as pbar:
            for _data in dataset:
                self._upload(resource_uuid, _data)
                pbar.update(1)
        return 
    
    def _upload(self, resource_uuid, json_event_data):
        try:
            api = SemanticGraphIndex()
            res = api.ingest(resource_uuid=resource_uuid, data=json_event_data)
            
            # 응답이 올때까지 기다림
            while True:
                if res:
                    break 
        except Exception as e:
            print(f"\nERROR | {e} | resource_uuid--> {resource_uuid} | json_event_data-->")


    # SGI 데이터만 삭제 | 모델링 유지
    def clear_data(self, resource_uuid:str):
        api = Storages()
        res = api.clear(resource_uuid=resource_uuid)
    
    # SGI 통째로 삭제 
    def delete_sgi(self, resource_uuid:str):
        api = Storages()
        res = api.delete(resource_uuid=resource_uuid)



from datetime import datetime, date
import math 
import pandas as pd 
import numpy as np 

class SGIClass:

    def __init__(self, cls_name, pkg_name="com", dtypemap:dict=None, dbg_mode=False):
        self.pkg_name = pkg_name 
        self.cls_name = cls_name 
        self.cls_fullname = f"{pkg_name}.{cls_name}" 
        self.properties_v1 = []
        self.properties_v2 = []
        self.dtypemap = dtypemap
        self._dbg_mode = dbg_mode 

    # 데이터 청소
    def _clean_data(self, data):
        print(f"데이터 청소 시작 | {datetime.now()}")
        df = pd.DataFrame(data)
        
        # DataFrame 전체를 numpy 배열로 변환 후 무한대 및 NaN 처리
        # cleaned_array = np.nan_to_num(
        #     df.to_numpy(),
        #     nan=0.0,
        #     posinf=sys.float_info.max,
        #     neginf=-sys.float_info.max
        # )
        # # 다시 DataFrame으로 변환 (원래 인덱스와 컬럼 유지)
        # df_cleaned = pd.DataFrame(cleaned_array, index=df.index, columns=df.columns)

        # df = df.fillna(value=None)
        # df_cleaned = df.replace({
        #     np.inf: sys.float_info.max,
        #     -np.inf: -sys.float_info.max,
        # })
        print(sys.float_info.max)
        df_cleaned = df.replace([np.inf, -np.inf], pd.NA).fillna(value=None, method=None)

        print(f"데이터 청소 종료 | {datetime.now()}")
        return df_cleaned.to_dict("records")

    # SGI Class Conf 생성 | 주어진 데이터로 데이터-타입 정의 후 프로퍼티 저장
    def create_class_conf(self, data):

        # data = self._clean_data(data)

        # 데이터-타입 정의를 위한 데이터구조 변환 
        # 클래스 정의시, uri 는 제외한다
        doc = {c: [] for c in list(data[0]) if c not in ["uri"]}
        for d in data:
            for k,v in d.items():
                doc.get(k).append(v)
        if self._dbg_mode:
            print(f"\n변환된 데이터구조-->")
            pp.pprint(doc)

        # 컬럼별 데이터-타입 정의 
        for column, values in doc.items():
            dtype = self.dtypemap[column] if self.dtypemap else None 
            for v in values:
                p = SGIProperty(column, v, dtype)
                dataType, dataStructure = p.dataType, p.dataStructure

                if isinstance(dataType, str) and isinstance(dataStructure, str):
                    # 데이터-타입을 찾았으면 멈춘다
                    self.properties_v1.append(p.property_conf_v1)
                    self.properties_v2.append(p.property_conf_v2)
                    break 

        # SGI 생성용 스키마 Conf. 정의
        self.creatable_class_conf = {
            "name": self.cls_name,
            "parents": [],
            "pkg": self.pkg_name,
            "attributes": self.properties_v1
        }
        if self._dbg_mode:
            print(f"\nSGI 생성용 스키마 Conf. 정의-->")
            pp.pprint(self.creatable_class_conf)

        # SGI 생성후 클래스 추가용 스키마 Conf. 정의
        self.addable_class_conf = {
            "action": "AddOrReplaceClass",
            "classDefinition": {
                "abstract": False,
                "name": self.cls_fullname,
                "parents": ["core.Item"],
                "attributes": self.properties_v2,
                "annotations": []
            }
        }
        if self._dbg_mode:
            print(f"\nSGI 생성후 클래스 추가용 스키마 Conf. 정의-->")
            pp.pprint(self.addable_class_conf)

        return self 

    # 실데이터 Conf. 정의
    def create_data_conf(self, data:list, auto_uri_digit:str=None):
        # 데이터 청소
        # data = self._clean_data(data)

        # SGI uri 값 자동셋팅 변수
        n_digit = auto_uri_digit if auto_uri_digit else len(str(len(data))) + 1
        
        self.data_conf = []

        for i, item in enumerate(data):
            # 패키지명+클래스명 을 합쳐서 클래스명으로 할당해야한다.
            item.update({'class': self.cls_fullname})

            # 원데이터에 'uri'(=id) 가 없다면 시스템에서 자동으로 생성해준다 
            if "uri" not in item:
                item['uri'] = f"{self.cls_fullname}_{str(i).zfill(n_digit)}"

            # 원데이터에 'datetime, date' 객체는 JSON-Serialize 할 수 없으므로 스트링으로 강제변환된다
            # 스키마상 데이터-타입이 'DateTime'으로 정의되어 있다면, 스트링으로 데이터를 업로드하더라도 SGI 안에서 자동으로 파싱된다
            for k,v in item.copy().items():
                if isinstance(v, datetime) or isinstance(v, date):
                    item[k] = datetime_obj_conversion(v)
                elif isinstance(v, list):
                    item[k] = [datetime_obj_conversion(v) for elem in v]
                elif isinstance(v, float):
                    item[k] = not_json_serializable_conversion(v) 
                else:
                    pass 

            self.data_conf.append({
                "action": "AddOrReplaceItem", 
                "item": item
            })
            if self._dbg_mode:
                print(f"\n데이터 업로드 Conf.-->")
                pp.pprint(self.data_conf)

        return self
    
# SGI에 데이터를 업로드할 때 JSON Serialize를 하는데, 변환 불가능한 값을 강제로 바꿔준다
def not_json_serializable_conversion(v):
    if v in [math.nan, np.nan]:
        return None 
    elif v in [math.inf, np.inf]:
        return sys.float_info.max 
    elif v in [-math.inf, -np.inf]:
        return -sys.float_info.max 
    else:
        return v 
    

def datetime_obj_conversion(value):
    if isinstance(value, datetime):
        # '2025-10-18T17:41:00'
        return value.isoformat()[:19]
    elif isinstance(value, date):
        # '2025-10-18'
        return value.isoformat()[:10]
    else:
        return value 

from datetime import datetime, date, timedelta 
import re 

def datetime_obj_conversion_v1(v):
    if isinstance(v, datetime): 
        v1 = v if v < datetime(1970, 1, 1) else v.astimezone()
        if v1.hour == 15:
            v1 += timedelta(hours=+9)
        m = re.search(r"(\d{4}-\d{2}-\d{2})", v1.isoformat())
        if m:
            v2 = m.group(1)
            # v2 = v2.replace("T", "'T'")
            # print("Date타입을 스트링으로-->", [k, v, v1, v2])
            return v2
        else:
            v2 = v1.isoformat()[:10]
            return v2
    elif isinstance(v, date):
        v1 = v if v < date(1970, 1, 1) else v.astimezone()
        return v1.isoformat()
    else:
        return v



from datetime import datetime, date 
from decimal import Decimal 

class SGIProperty:

    # 파이썬 데이터타입 : SGI 데이터타입
    _dmap = {
        "bool": "Boolean",
        "str": "String",
        "int": "Integer",
        "float": "Float",
        "datetime": "DateTime",
        "date": "Date",
        "decimal": "Decimal"
    }

    def __init__(self, name:str, value:any, dtype:str=None):
        self.name = name 
        if dtype is None:
            self.dtype = judge_sgi_dtype(value)
        else:
            if dtype in list(self._dmap):
                self.dtype = self._dmap[dtype]
            else:
                self.dtype = judge_sgi_dtype(value)

        self.dstruc = judge_sgi_dstruc(value)


    def _parse(self, value):  
        dtype = judge_sgi_dtype(value)
        dstruc = judge_sgi_dstruc(value)
        return dtype, dstruc 
    
    # SGI 생성용 클래스 정의를 위한 프로퍼티 Conf. 생성 
    @property 
    def property_conf_v1(self):
        return {
            "name": self.name,
            "type": {
                "dataType": self.dataType,
                "dataStructure": self.dataStructure
            },
            "annotation": {}
        }
    
    # SGI 생성후 클래스 추가용 프로퍼티 Conf. 정의
    @property 
    def property_conf_v2(self):
        return {
            "name": self.name,
            "type": self.dataType,
            "annotations": []
        }


# 'dataType' 결정
def judge_sgi_dtype(value):
    if isinstance(value, bool):
        return "Boolean"
    elif isinstance(value, str):
        # 길이 255자 이하: "String"
        # 255자 초과: "Text"
        return "String" if len(value) <= 256 else "Text"
    elif isinstance(value, int):
        return "Integer"
    elif isinstance(value, float):
        return "Float"
    elif isinstance(value, datetime):
        # datetime도 date를 상속하므로 순서가 중요 (datetime을 먼저 판단해야)
        # tzinfo가 None이면 로컬 날짜시간으로 간주
        if value.tzinfo is None:
            return "LocalDateTime"
        else:
            return "DateTime"
    elif isinstance(value, date):
        return "Date"
    elif isinstance(value, Decimal):
        return "Decimal"
    elif is_embedding_object(value):
        return "Embedding"
    elif is_geo_type(value):
        return "Geo"
    elif is_hierarchical_string(value):
        return "HierarchicalString"
    else:
        # 이외의 모든 경우는 "스트링" 처리
        return "String"


def is_embedding_object(obj, min_dim=5, dtype=(float, int)):
    # 리스트나 튜플이고, 길이가 min_dim 이상이며, 모든 원소가 float 또는 int인 경우 판정
    if isinstance(obj, (list, tuple)) and len(obj) >= min_dim:
        return all(isinstance(x, dtype) for x in obj)
    return False


def is_geo_type(value):
    # (lat, lon) 튜플/리스트
    if isinstance(value, (tuple, list)) and len(value) == 2:
        try:
            lat, lon = float(value[0]), float(value[1])
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return True
        except Exception:
            pass

    # {'lat': x, 'lon':y} 또는 {'latitude': x, 'longitude': y}
    if isinstance(value, dict):
        keys = list(value.keys())
        if ('lat' in keys and 'lon' in keys) or ('latitude' in keys and 'longitude' in keys):
            try:
                lat = float(value.get('lat', value.get('latitude')))
                lon = float(value.get('lon', value.get('longitude')))
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return True
            except Exception:
                pass
        # GeoJSON Point {"type": "Point", "coordinates": [...]}
        if value.get('type') == 'Point' and isinstance(value.get('coordinates'), (list, tuple)):
            coords = value['coordinates']
            if len(coords) == 2:
                try:
                    lon, lat = float(coords[0]), float(coords[1])
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        return True
                except Exception:
                    pass

    # 좌표 문자열 판독 (예: "37.511, 126.982")
    if isinstance(value, str):
        parts = value.split(',')
        if len(parts) == 2:
            try:
                lat, lon = float(parts[0].strip()), float(parts[1].strip())
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return True
            except Exception:
                pass
    return False


def is_hierarchical_string(s):
    if not isinstance(s, str):
        return False
    # 주요 구분자를 포함하고, split 후 2개 이상의 segment가 있을 것!
    delimiters = ['/', '\\', '>']
    for delim in delimiters:
        if delim in s:
            segments = [seg for seg in s.split(delim) if seg]
            if len(segments) >= 2:
                return True
    return False


# 'dataStructure' 결정
def judge_sgi_dstruc(value):
    if isinstance(value, list):
        return "List"
    elif isinstance(value, dict):
        return "Map"
    else:
        return "Singleton"
















