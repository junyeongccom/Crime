from com.junyeongc.models.datareader import DataReader
from com.junyeongc.models.dataset import Dataset
import pandas as pd
import os

from com.junyeongc.models.googlemap_singleton import ApiKeyManager

class CrimeService:
    dataset = Dataset()
    datareader = DataReader()

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

    def preprocess(self, *args) -> object:
        print(f"------------모델 전처리 시작-----------")
        temp = []
        for i in args:
            temp.append(i)

        this = self.dataset
        this.cctv = self.new_model(temp[0])
        this = self.cctv_ratio(this)
        this.crime = self.new_model(temp[1])
        #this = self.crime_ratio(this)
        this.pop = self.new_model(temp[2])
        this = self.pop_ratio(this)
        DataReader.google_api()
        return this

    @staticmethod
    def cctv_ratio(this) -> object:
        cctv = this.cctv
        cctv.rename(columns = {'2013년도 이전':'2012년도 이전', '2014년':'2013년', 
                             '2015년':'2014년', '2016년':'2015년'}, inplace=True)
        print(f"😄cctv 데이터 확인:\n{cctv.head()}")
        CrimeService.null_count(cctv)
        return this

    @staticmethod
    def crime_ratio(this) -> object:
        crime = this.crime
        print(f"😄crime 데이터 확인:\n{crime.head()}")
        CrimeService.null_count(crime)
        station_names = [] # 경찰서 관서명 리스트
        for name in crime['관서명']:
            station_names.append('서울' + str(name[:-1]) + '경찰서')
        print(f"😄관서명 리스트:{station_names}")
        station_addrs = []
        station_lats = []
        station_lngs = []
        gmaps = DataReader.google_api()
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
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 현재 .py 파일 기준 디렉터리
        SAVE_DIR = os.path.join(BASE_DIR, '..', 'saved_data')  # 한 단계 상위로 올라가서 saved_data
        os.makedirs(SAVE_DIR, exist_ok=True)  # 폴더가 없으면 생성
        csv_file_path = os.path.join(SAVE_DIR, 'police_position.csv')
        crime.to_csv(csv_file_path)
        return this
    
    @staticmethod
    def pop_ratio(this) -> object:
        pop = this.pop
        pop.rename(columns = {
            #pop.columns[0]:'자치구', #변경하지 않음
            pop.columns[1]: '인구수',
            pop.columns[2]: '한국인',
            pop.columns[3]: '외국인',
            pop.columns[4]: '고령자'}, inplace=True)
        print(f"😄pop 데이터 확인:\n{pop.head()}")
        CrimeService.null_count(pop)
        return this

    @staticmethod
    def null_count(df) -> object:
        total_nulls = df.isnull().sum().sum()
        if total_nulls == 0:
            print(f"⚠️ 컬럼 결측값이 존재하지 않습니다!")
        else:
            print(f"⚠️ 컬럼 결측값 개수:{total_nulls}")
        return df
    
    #@staticmethod
    #def check_api():
    #    s1 = ApiKeyManager()
    #    s2 = ApiKeyManager()
    #    s1.set_api_key("set_api_key")
    #    print(f"s1의 api_key: {s1.get_api_key()}")
    #    print(f"s2의 api_key: {s2.get_api_key()}")
    #    print(f"😶s1 is s2 => {s1 is s2}")
    #    print(f"s1의 id => {id(s1)}")
    #    print(f"s2의 id => {id(s2)}")
    
