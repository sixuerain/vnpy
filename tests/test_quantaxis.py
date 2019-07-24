# here put the import lib
import QUANTAXIS as QA
from QUANTAXIS.QAUtil.QAParameter import (
    FREQUENCE
)
from QUANTAXIS.QAIndicator.base import MAX,MIN,REF,CROSS,HHV,LLV,AVEDEV,ABS,BARSLAST
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from MagicNum.MagicUtil.DaShu import DaShu,Calc_Dashu
from MagicNum.MagicUtil.MGAngle import MGAngle
from MagicNum.Point.GuaiPoint import CalcPoint
from MagicNum.MagicUtil.Balance import Calc_DaShuGoldNum_Balance_bool


class MagicNumContext():
    '''
    use to calc mid-variable one time to save time
    '''
    def __init__(self,kbardf):
        self.kbardf = kbardf
        self.ODS = pd.Series()
        self.HDS = pd.Series()
        self.LDS = pd.Series()
        self.CDS = pd.Series()
        self.guai = pd.Series()

    def CalcDS(self):
        O = self.kbardf['open']
        H = self.kbardf['high']
        L = self.kbardf['low']
        C = self.kbardf['close']
        
        self.ODS = Calc_Dashu(O)
        self.HDS = Calc_Dashu(H)
        self.LDS = Calc_Dashu(L)
        self.CDS = Calc_Dashu(C)

    def CalcGuai(self):
        #calc one time
        self.guai = CalcPoint( self.kbardf )

    def Calc(self):
        self.CalcDS()
        self.CalcGuai()


def REFBOOL(s1,N):
    return s1.shift(-N)

def GetHighFreqOHLC(magicnumCtx,xls ):
    PHAO = Calc_DaShuGoldNum_Balance_bool(magicnumCtx.ODS,xls)
    PHAH = Calc_DaShuGoldNum_Balance_bool(magicnumCtx.HDS,xls)
    PHAL = Calc_DaShuGoldNum_Balance_bool(magicnumCtx.LDS,xls)
    PHAC = Calc_DaShuGoldNum_Balance_bool(magicnumCtx.CDS,xls)

    PH = np.logical_or( np.logical_or( np.logical_or(PHAO,PHAH),PHAL ),PHAC )

    conA1 = np.logical_and( np.logical_and( REFBOOL(magicnumCtx.guai,xls),REFBOOL(PH,xls) ), PHAO)
    conA2 = np.logical_and( np.logical_and( REFBOOL(magicnumCtx.guai,xls),REFBOOL(PH,xls) ), PHAH)
    conA3 = np.logical_and( np.logical_and( REFBOOL(magicnumCtx.guai,xls),REFBOOL(PH,xls) ), PHAL)
    conA4 = np.logical_and( np.logical_and( REFBOOL(magicnumCtx.guai,xls),REFBOOL(PH,xls) ), PHAC)

    tja = pd.Series([len(np.where(conA1)[0]),len(np.where(conA2)[0]),len(np.where(conA3)[0]),len(np.where(conA4)[0]) ] ).max()

    return tja

'''
//输入三组序列数
A1:=45;B1:=72;C1:=79;D1:=113;E1:=122;F1:=131;G1:=163;H1:=174;K1:=186;
A21:=37;B21:=84;C21:=128;D21:=138;E21:=194;F21:=218;G21:=232;H21:=273;K21:=288; 
A31:=47;B31:=66;C31:=97;D31:=106;E31:=125;F31:=155;G31:=166;H31:=202;K31:=214;
'''

def SearchHFxls(kbardf,myCtx):
    '''
    calc the highest xls with highest freq
    '''
    XLS = [
     [45,72,79,113,122,131,163,174,186],
     [37,84,128,138,194,218,232,273,288],
     [47,66,97,106,125,155,166,202,214] ]
    
    cid = pd.DataFrame(columns=['xls','freq'])
    cid_list = []

    print("total kbar len:{}".format(len(myCtx.ODS)))

    for xls_arr in XLS:
        for xls in xls_arr:
            freq = GetHighFreqOHLC(myCtx,xls)
            #print("xls:{} freq:{}".format(xls,freq))
            cid_list.append({'xls':xls,'freq':freq})
    
    cid = pd.DataFrame(cid_list)
    cid1 = cid.sort_values(['freq'],ascending=False).reset_index(drop=True)
    #print(cid1)

    high_cid = cid1['freq'].iloc[0]
    print("freq highest:{}".format( high_cid))

    #if more than 1 xls have same freq , get the highest xls
    cid2 = cid1.loc[ cid1['freq'] == high_cid]
    cid2 = cid2.sort_values(['xls'],ascending=False).reset_index(drop=True)
    #print(cid2)

    high_xls = cid2['xls'].iloc[0]
    print("XLS highest:{}".format( high_xls))

    return high_xls

def CurkBalance(magicnumCtx,xls):
    #cur kbar balance
    PHAO = Calc_DaShuGoldNum_Balance_bool(magicnumCtx.ODS,xls)
    PHAH = Calc_DaShuGoldNum_Balance_bool(magicnumCtx.HDS,xls)
    PHAL = Calc_DaShuGoldNum_Balance_bool(magicnumCtx.LDS,xls)
    PHAC = Calc_DaShuGoldNum_Balance_bool(magicnumCtx.CDS,xls)
    PH = np.logical_or( np.logical_or( np.logical_or(PHAO,PHAH),PHAL ),PHAC )
    return PH

def CheckDaYao(kbardf):
    #calc info : DS / GuaiPoint
    myCtx = MagicNumContext(kbardf)
    myCtx.Calc()

    #search xls
    xls = SearchHFxls(kbardf,myCtx)

    PH1 = CurkBalance(myCtx,xls)

    zeng = BARSLAST(PH1)
    SHU2 = zeng + xls

    PH2 = CurkBalance(myCtx,SHU2)


if __name__ == '__main__':
    code = '000001'
    # 获取one stock 2019-03-29的Day data
    day_data=QA.QA_fetch_stock_day_adv(code,'2006-07-20','2019-06-28',FREQUENCE.DAY)

    CheckDaYao(day_data)
    
    #GetHighFreqOHLC(day_data,45)
    #SearchHFxls( day_data)


