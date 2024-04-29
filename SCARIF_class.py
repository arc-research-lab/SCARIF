class predictor:
    def __init__(self, K_CPU = 5.01, K_DRAM=0.95, K_SSD=0.16, K_HDD=0.04, K_year=83.08, D=-1100) -> None:
        self.K_CPU = K_CPU
        self.K_DRAM = K_DRAM
        self.K_SSD = K_SSD
        self.K_HDD = K_HDD
        self.K_year = K_year
        self.D = D
        return
    
    def setup(self, cpu_core_num, dram_size, ssd_size, hdd_size, year):
        # self.carbon = self.K_CPU*cpu_core_num +\
        #     self.K_DRAM*dram_size +\
        #     self.K_SSD*ssd_size +\
        #     self.K_HDD*hdd_size +\
        #     self.K_year*(year - 2000) +\
        #     self.D
        self.CPU_cost = self.K_CPU*cpu_core_num
        self.DRAM_cost = self.K_DRAM*dram_size
        self.SSD_cost = self.K_SSD*ssd_size
        self.HDD_cost = self.K_HDD*hdd_size
        self.year_cost = self.K_year*(year - 2000)
        self.carbon = self.CPU_cost + self.DRAM_cost + self.SSD_cost + self.HDD_cost + self.year_cost + self.D
        
def HP_predictor():
    return predictor(D=-1100)
def Dell_predictor():
    return predictor(D=-400)
def Lenovo_predictor():
    return predictor(D=-900)

