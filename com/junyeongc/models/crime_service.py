from com.junyeongc.models.datareader import DataReader
from com.junyeongc.models.dataset import Dataset
import pandas as pd
import os
from com.junyeongc.models import BASE_DIR, SAVE_DIR
from com.junyeongc.models.googlemap_singleton import ApiKeyManager

class CrimeService:
    dataset = Dataset()
    datareader = DataReader()
        

    def preprocess(self, *args) -> object:
        print(f"------------모델 전처리 시작-----------")
        temp = list(args)
        this = self.dataset
        this.cctv = self.new_model(temp[0])
        this = self.save_csv(temp[0], this)
        this.crime = self.new_model(temp[1])
        this = self.save_csv(temp[1], this)
        this.pop = self.new_model(temp[2])
        this = self.save_csv(temp[2], this)
        return this
    
    def new_model(self, fname) -> object:
        reader = self.datareader
        this = self.dataset
        print(f"Dataset 객체 확인: {this}")
        reader.fname = fname
        if reader.fname.endswith(".csv"):
            print(f"📂 CSV 파일 로드: {reader.fname}")
            return reader.csv_to_dframe()
        elif reader.fname.endswith(".xls"):
            print(f"📂 Excel 파일 로드: {reader.fname}")
            return reader.xls_to_dframe(header=2, usecols='B,D,G,J,N')
        else:
            raise ValueError(f"지원하지 않는 파일 형식입니다: {fname}")
 
    def save_csv(self, fname: str, this) -> object:
        base_name = os.path.splitext(fname)[0]     # 🔍 확장자를 제외한 파일명 추출
        existing_files = [os.path.splitext(f)[0] for f in os.listdir(BASE_DIR)] # 🔍 BASE_DIR에 같은 이름의 파일이 존재하는지 확인
        if base_name in existing_files:
            print(f"⚠️ 동일한 이름({base_name})의 파일이 이미 존재합니다. 저장을 건너뜁니다.")
            return this
        keyword = self.extract_keyword_from_fname(fname)
        method = self.get_update_method(keyword)
        if method:
            if isinstance(CrimeService.__dict__.get(method.__name__), staticmethod):
                this = method(this)
            else:
                this = method(self, this) 
        return this
            

    def get_update_method(self, keyword):
        method_name = f"update_{keyword}"
        method = getattr(self, method_name, None)
        print(f"🔍 가져온 메서드: {method_name}")
        return method

    @staticmethod
    def extract_keyword_from_fname(fname):
        """파일명에서 _ 앞의 키워드를 추출"""
        return fname.split("_")[0]


    @staticmethod
    def update_cctv(this) -> object:
        this.cctv = this.cctv.drop(['2013년도 이전', '2014년', '2015년', '2016년'], axis = 1)
        cctv = this.cctv
        cctv = cctv.rename(columns={'기관명': '자치구'})
        cctv.to_csv(os.path.join(SAVE_DIR, "cctv_seoul.csv"), index=False,)
        print(f"😄cctv 데이터 확인:\n{cctv.head()}")
        this.cctv = cctv
        return this

    @staticmethod
    def update_crime(this) -> object:
        crime = this.crime
        print(f"😄crime 데이터 확인:\n{crime.head()}")
        station_names = [] # 경찰서 관서명 리스트
        for name in crime['관서명']:
            station_names.append('서울' + str(name[:-1]) + '경찰서')
        print(f"😄관서명 리스트:{station_names}")
        station_addrs = []
        station_lats = []
        station_lngs = []
        gmaps = ApiKeyManager()
        for name in station_names:
            tmp = gmaps.geocode(name, language = 'ko')
            station_addrs.append(tmp[0].get("formatted_address"))
            print(f"{name}의 검색결과: {tmp[0].get("formatted_address")}")
            tmp_loc = tmp[0].get("geometry")
            station_lats.append(tmp_loc['location']['lat'])
            station_lngs.append(tmp_loc['location']['lng'])
        print(f"😄자치구 리스트: {station_addrs}")    
        gu_names = []
        for addr in station_addrs:
            tmp = addr.split()
            tmp_gu = [gu for gu in tmp if gu[-1] == '구'][0]
            gu_names.append(tmp_gu)
        crime['자치구'] = gu_names
        crime = CrimeService.crime_modify(crime)
        os.makedirs(SAVE_DIR, exist_ok=True)  # 폴더가 없으면 생성
        crime.to_csv(os.path.join(SAVE_DIR, 'crime_seoul.csv'))
        this.crime = crime
        return this
    
    @staticmethod
    def crime_modify(crime_df) :
        print(f"📂 범죄 데이터 로드 중: {crime_df}")
        crime_df["발생 합계"] = crime_df.filter(like="발생").sum(axis=1)
        crime_df["검거 합계"] = crime_df.filter(like="검거").sum(axis=1)
        crime_df = crime_df[["자치구", "발생 합계", "검거 합계"]]
        print(f"😄범죄 데이터 수정 확인:\n{crime_df.head()}")
        return crime_df


    @staticmethod
    def update_pop(this) -> object:
        pop = this.pop
        pop.rename(columns = {
            #pop.columns[0]:'자치구', #변경하지 않음
            pop.columns[1]: '인구수',
            pop.columns[2]: '한국인',
            pop.columns[3]: '외국인',
            pop.columns[4]: '고령자'}, inplace=True)
        pop.to_csv(os.path.join(SAVE_DIR, 'pop_seoul.csv'), index=False)
        print(f"😄pop 데이터 확인:\n{pop.head()}")
        return this
