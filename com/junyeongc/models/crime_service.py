from com.junyeongc.models.datareader import DataReader
from com.junyeongc.models.dataset import Dataset
import pandas as pd
import os

class CrimeService:
    dataset = Dataset()
    datareader = DataReader()
    def new_model(self, fname) -> object:
        reader = self.datareader
        this = self.dataset
        print(f"Dataset 객체 확인: {this}")
        file_path = os.path.join(reader._context, fname)
        if fname.endswith(".csv"):
            print(f"📂 CSV 파일 로드: {file_path}")
            return pd.read_csv(file_path)
        elif fname.endswith(".xls") or fname.endswith(".xlsx"):
            print(f"📂 Excel 파일 로드: {file_path}")
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"지원하지 않는 파일 형식입니다: {fname}")

    def preprocess(self, *args) -> object:
        print(f"------------모델 전처리 시작-----------")
        temp = []
        for i in args:
            temp.append(i)

        this = self.datareader
        this.cctv = self.new_model(temp[0])
        this.crime = self.new_model(temp[1])
        this.pop = self.new_model(temp[2])
        return this