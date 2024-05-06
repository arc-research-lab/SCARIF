"""
The core functionality of SCARIF
the units used in this function:
 - carbon cost: KgCO2e
 - dram,ssd,hdd-size: GB
 - year: 20xx
 - chip area: mm^2
"""
import os
from ACT.logic_model  import Fab_Logic

class predictor:
    """
    Predictor used for server-level carbon cost estimation
    """
    def __init__(self, K_CPU = 5.01, K_DRAM=0.95, K_SSD=0.16, K_HDD=0.04, K_year=83.08, D=-1100, acc_pred=None) -> None:
        self.K_CPU = K_CPU
        self.K_DRAM = K_DRAM
        self.K_SSD = K_SSD
        self.K_HDD = K_HDD
        self.K_year = K_year
        self.D = D
        if acc_pred is not None:
            assert isinstance(acc_pred, acc_preditor), "Error: the acc_pred argument must be None or a instance of acc_predictor"
            self.acc_pred = acc_pred
        else:
            self.acc_pred = acc_preditor()
        return
    
    def setup(self, cpu_core_num, dram_size, ssd_size, hdd_size, year, acc_tech_node=None, acc_chip_area=None):

        self.CPU_cost = self.K_CPU*cpu_core_num
        self.DRAM_cost = self.K_DRAM*dram_size
        self.SSD_cost = self.K_SSD*ssd_size
        self.HDD_cost = self.K_HDD*hdd_size
        self.year_cost = self.K_year*(year - 2000)
        self.carbon = self.CPU_cost + self.DRAM_cost + self.SSD_cost + self.HDD_cost + self.year_cost + self.D
        self.total_carbon = self.carbon
        if (acc_tech_node is not None) and (acc_chip_area is not None):#begin to estimate the acc carbon
            self.acc_pred.setup(acc_tech_node,acc_chip_area)
            self.acc_carbon = self.acc_pred.acc_system_carbon
            self.total_carbon = self.carbon+self.acc_carbon
        return
    
    def __str__(self) -> str:
        str_ = ""
        str_ += "system carbon without accelerator: {} KgCO2e".format(self.carbon)
        # if(self.acc_carbon is not None):
        if hasattr(self,"acc_carbon"):
            str_ += "\nsystem accelerator carbon: {} KgCO2e".format(self.acc_carbon)
            str_ += "\nsystem carbon with accelerator: {} KgCO2e".format(self.total_carbon)
        return str_
             
class acc_preditor:
    """
    predictor used for server-level carbon cost estimation for Acc.
    integrated with other open-source tools like ACT and GreenChip
    """
    def __init__(self, ref_tech_node=14, ref_area=698, ref_system_carbon=140.28,tool='ACT') -> None:
        self.ref_tech_node=ref_tech_node
        self.ref_area=ref_area
        self.ref_system_carbon=ref_system_carbon
        '''-------------------- dir. related operations --------------------'''
        #get original workdir
        basedir = os.getcwd()
        #get dir of SCARIF, 
        filedir = os.path.dirname(__file__)
        #change the workdir since the ACT is sensitive to the work dir
        os.chdir(filedir)

        '''-------------------- use open-source tools to estimate the baseline carbon --------------------'''
        #determine the tool to use
        self.availiable_tools = ["ACT"]
        assert tool in self.availiable_tools, \
            "Error: tool '{}' is not supported by SCARIF currently, availiable tools:{}"\
            .format(tool,self.availiable_tools)
        self.tool = tool
        #use the tools
        self.ref_chip_carbon = self.predict(self.ref_tech_node,self.ref_area)
        
        #get back to original dir
        os.chdir(basedir)
        return

    def setup(self, acc_tech_node, acc_area) -> None:
        self.acc_tech_node = acc_tech_node
        self.acc_area = acc_area
        '''-------------------- dir. related operations --------------------'''
        #get original workdir
        basedir = os.getcwd()
        #get dir of SCARIF, 
        filedir = os.path.dirname(__file__)
        #change the workdir since the ACT is sensitive to the work dir
        os.chdir(filedir)
        '''-------------------- use open-source tools to estimate the acc. chip carbon --------------------'''
        self.acc_chip_carbon=self.predict(self.acc_tech_node,self.acc_area)
        '''-------------------- compute the system-level carbon of the acc. --------------------'''
        self.acc_system_carbon = self.ref_system_carbon/self.ref_chip_carbon * self.acc_chip_carbon
        os.chdir(basedir)
        return

    def predict(self, tech_node, area):
        #use the tools
        chip_carbon = None
        if self.tool=="ACT":
            chip_carbon = self.ACT_pred(tech_node,area)
        return chip_carbon
        
    def ACT_pred(self, tech_node, area):
        #enter ACT dir
        os.chdir("./ACT")
        #begin prediction
        # init ACT tool
        ic_yield = 0.875
        chip = Fab_Logic(gpa  = "95",
                        carbon_intensity = "src_coal",
                        process_node = tech_node,
                        fab_yield=ic_yield)
        chip.set_area(area/1000)#the ACT uses cm^2
        # for simplicity, the packing carbon costs are omitted since they usually take <5%, and the package number is hard to get
        chip_carbon = chip.get_carbon()/1000
        os.chdir("..")
        return chip_carbon
        
accepted_vendors = ["HP","Dell","Lenovo"]
vendor_to_intercept = {"HP":-1100,"Dell":-400,"Lenovo":-900}
def HP_predictor():
    return predictor(D=-1100)
def Dell_predictor():
    return predictor(D=-400)
def Lenovo_predictor():
    return predictor(D=-900)

