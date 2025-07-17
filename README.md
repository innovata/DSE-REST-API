# DSE-REST-API
NETVIBES / Data Science Experience REST API




<!-- ############################################################ -->
## 1. INTRODUCTION  
<!-- ############################################################ -->

DSE-Agent 패키지는 클라이언트 사이드에서 클라우드 솔루션인 DSE 사용을 지원하는 몇가지 기능을 제공합니다.
'DSE (Data Science Experience)' 는 NETVIBES 브랜드의 솔루션 포르폴리오 중 하나인 솔루션명 입니다.  


<!-- ############################################################ -->
## 2. 환경구성 
<!-- ############################################################ -->

### [1] 파이썬 가상환경 구성 (Setup Python Virtual Environment) 

다음 링크의 가이드를 참조하세요.  

https://github.com/innovata/DevDocs/blob/main/PythonEnv.md  


### [2] dsx-agent 패키지 설치 

파이썬 가상환경에서, 다음 커멘드를 실행하여 패키지 설치.

    pip install dse-agent

    (pip install -r requirements.txt)




<!-- ############################################################ -->
## 3. 사용법 설명 
<!-- ############################################################ -->

본 패키지는 공식적으로 제공되는 프로그램이 아닙니다.  
다쏘시스템에서는 다음 링크에서 공식적인 REST API를 제공합니다.  
        https://media.3ds.com/support/documentation/developer/Cloud/en/DSDoc.htm?show=CAADocQuickRefs/DSDocHome.htm 

REST API를 활용하여 직접 클라이언트를 개발하는 것을 권장하며, 본 패키지는 편의를 위해 제공할 뿐이며 사용 기능 개선 및 버그에 대한 후속 작업을 지원하지 않습니다.  
커맨드 라인 사용법은 지원하지 않으며, 본 패키지를 임포트하여 클라이언트를 개발하길 바랍니다.  







<!-- ############################################################ -->
## 4. 사용 예제 | CLM Agent 생성 
<!-- ############################################################ -->

CLM Agent ID/Password 생성 방법은 다음의 영상가이드를 참조하세요.


        import os, sys 
        
        os.environ["CLM_AGENT_ID"] = "YOUR_ID"
        os.environ["CLM_AGENT_PASSWORD"] = "YOUR_PASSWORD"
        <!-- 또는 -->
        os.environ["CLM_AGENT_CREDENTIAL_PATH"] = "JSON_FILE_PATH_INCLUDING_ID_PW"

        os.environ["3DX_PLATFORM_TENANT_URI"] = "YOUR_3DX_PLATFORM_TENANT_URI" # 예시: "https://r1132100527066-apk2-sgi.3dexperience.3ds.com:443"

        from dsxagent import restapi 







<!-- ############################################################ -->
## 5. 사용 예제 | REST API Use Case
<!-- ############################################################ -->


### [1.1] dserestapi.Storages 

1.1.1. 모든 스토리지 가져오기

        from dserestapi import Storages 
        api = Storages()
        res = api.get()
        data = res.json() 

data 샘플:  
./How to use APIs/01_Storages/Storages List.json 파일을 참조하세요.  



1.1.2.  스토리지 검색 

        from dserestapi import Storages
        api = Storages()
        res = api.search_by_name(name="TestDATASET-01", workspace_id="dw-global-000000-default")
        dic = res.json()
        cards = dic["cards"]
        if len(cards) == 1: 
                cards[0]
        else:
                print("검색 범위를 좁히세요. 또는 추가로 코드를 작성하세요.")

cards[0] 샘플 데이터 -->

        {
                "id": "0a28ee53-4def-4c92-ba75-87537d83185f",
                "resourceId": "TestDATASET-01",
                "projectId": "dp-global-000000",
                "resourceUUID": "0a28ee53-4def-4c92-ba75-87537d83185f",
                "workspaceId": "dw-global-000000-default",
                "name": "TestDATASET-01",
                "creator": "jle69_gmail",
                "kind": "Storage",
                "type": "ObjectStorage",
                "created": 1751954756480,
                "lastModified": 1751954756485,
                "permissions": {
                        "read": true,
                        "write": true,
                        "execute": true
                }
        }


추가 예제는 ./How to use APIs/01_Storages/01_get_storages_list.py 을 참조하세요.  


### [1.2] dserestapi.ObjectStorage 

1.2.1. 파일 업로드 

앞서 설명한 1.1.2. 에서 resourceUUID 를 사용.

        from dserestapi import ObjectStorage
        api = ObjectStorage()
        res = api.upload_files(
                resourceUUID="0a28ee53-4def-4c92-ba75-87537d83185f",
                files=[file1, file2, ... fileN] # file1: 파일절대경로
        )

res에는 JSON Data가 없으므로 다음과 같이 확인합니다.  

        print(res) 
        <!-- <Response [200]> -->


        


### [1.3] dserestapi.SemanticGraphIndex 

1.3.1. 데이터 모델링 

데이터 스키마를 data_modeling_config 와 같이 정의해야 합니다.  
data_modeling_config의 상세 내용은 ./How to use APIs/01_Storages/01_ingest_data.py 을 참조하세요.    

        from dserestapi import Storages
        api = Storages()
        res = api.create(
                stype="IndexUnit",
                name="TestSGI_01_CreatedByRestAPI",
                description="테스트 후 삭제 | SGI 데이터 모델링 테스트",
                config=data_modeling_config
        )


방금 전의 res 로 부터 'resource_uuid' 를 추출하여 데이터 적재 시 사용합니다.  

        resource_uuid = res.json()["resourceUUID"]



1.3.2. 데이터 적재 (Data Ingestion)

        from dserestapi import SemanticGraphIndex
        sgi = SemanticGraphIndex()
        data = [{
                "class": "Rawdata.DummyData",
                "seq": 1,
                "title": "This is a title",
                "_text": "bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla~"
        }]
        res = sgi.ingest(resourceUUID=resource_uuid, data=data)
        print(res) 
        <!-- <Response [200]> -->


추가 예제는 ./How to use APIs/03_SemanticGraphIndex/01_ingest_data.py 을 참조하세요.  





