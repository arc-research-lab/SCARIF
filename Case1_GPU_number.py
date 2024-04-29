
# Reproduce of Case study 1 in SCARIF
# setups:
# 1.(2017 server) DellR740 + 2x Intel Xeon 8180 CPU + 64GB DRAM + 1000GB HDD + 1x Nvidia V100
# 2.(2020 server) DellR750 + 2x Intel Xeon 8375 CPU + 64GB DRAM + 1000GB HDD + 1x Nvidia A100

# Units:
# 1. DellR740 Carbon footprint report(no CPU part name reported, 32 GB DRAM, 1600 GB HDD): https://i.dell.com/sites/csdocuments/CorpComm_Docs/en/carbon-footprint-poweredge-r740.pdf
# 2. Dell R750: not reported by the vendor
# 3. Intel Xeon 8180 CPU: 28 CPU cores, 698 mm2 die size, 14 nm, power: 10(statistic)-250(TDP) W
# 4. Intel Xeon 8375 CPU: 32 CPU cores, 660 mm2 die size, 12 nm, power: 10(statistic)-300(TDP) W
# 5. Nvidia V100: 815 mm2 die size, 12 nm, power: 39(statistic)-250(task) W
# 6. Nvidia A100: 826 mm2 die size, 7nm, power: 53(statistic)-175(task) W

# performance metric:
# server 2 has a 1.61x throughput than server 1 when performing inference of deit-t
# --> compare 1x server 1 with 0.62x server 2

# operational carbon
# system2 running at 0.62 utilization
# kWh to KgCO2e: TX: 0.438, AZ: 0.395, CA: 0.234, NY: 0.188 KgCO2e/Kwh

#----------------------------------------------ACT part for CPU and GPU chip carbon cost-----------------------------------------------#
# estimating the chip carbon for CPUs and GPUs using ACT
import sys
import os
sys.path.append("./ACT")
os.chdir("./ACT")

#######
# setup
#######
from ACT.logic_model  import Fab_Logic
debug = False
xeon_8180 = 6.98 #cm2
xeon_8375 = 6.60 #cm2
v100 = 8.15 #cm2
a100 = 8.26 #cm2
ic_yield = 0.875

#######
# init ACT tool
#######
# the key difference between setup in V100 and 8375 are because V100 are released earlier, so we use the old tech node
# the package carbon cost are ignored since the package numbers are not reported, and this cost is small
xeon_8180_chip = Fab_Logic(gpa  = "95",
                        carbon_intensity = "src_coal",
                        process_node = 14,
                        fab_yield=ic_yield)
Xeon_8375_chip = Fab_Logic(gpa  = "95",
                        carbon_intensity = "src_coal",
                        process_node = 10,
                        fab_yield=ic_yield)#we use 10 nm as the tech node since ACT doesn't include the 12 nm 
v100_chip = Fab_Logic(gpa  = "95",
                        carbon_intensity = "src_coal",
                        process_node = 14,
                        fab_yield=ic_yield)#we use 14 nm as the tech node since ACT doesn't include the 12 nm
a100_chip = Fab_Logic(gpa  = "95",
                        carbon_intensity = "src_coal",
                        process_node = 7,
                        fab_yield=ic_yield)

xeon_8180_chip.set_area(xeon_8180)
Xeon_8375_chip.set_area(xeon_8375)
v100_chip.set_area(v100)
a100_chip.set_area(a100)

#######
# get chip carbon
#######
xeon_8180_carbon = xeon_8180_chip.get_carbon()/1000
xeon_8375_carbon = Xeon_8375_chip.get_carbon()/1000
v100_carbon = v100_chip.get_carbon()/1000
a100_carbon = a100_chip.get_carbon()/1000
# print("----- chip carbon cost from ACT -----")
print("8180:",xeon_8180_carbon,"\n8375:",xeon_8375_carbon,"\nv100:",v100_carbon,"\na100:",a100_carbon)
os.chdir("..")
#----------------------------------------------use SCARIF to estimate system cost-----------------------------------------------#
#######
# get system carbon w/o Acc.
#######
import SCARIF_class
sys1 = SCARIF_class.Dell_predictor()
sys1.setup(2*28,64,0,1000,2017)
sys1_no_acc_carbon = sys1.carbon

sys2 = SCARIF_class.Dell_predictor()
sys2.setup(2*32,64,0,1000,2020)
sys2_no_acc_carbon = sys2.carbon

print("----- system carbon cost w/o Acc. -----")
print("system 1:",sys1_no_acc_carbon," KgCO2e\nsystem 2:",sys2_no_acc_carbon, " KgCO2e")


#######
# get system carbon w/ Acc.
#######
sys1_acc_carbon = sys1.CPU_cost*v100_carbon/(xeon_8180_carbon*2)
sys2_acc_carbon = sys2.CPU_cost*a100_carbon/(xeon_8375_carbon*2)
print("----- system-level Acc. carbon cost -----")
# print(sys1.CPU_cost,sys2.CPU_cost)
print("v100 in system 1:",sys1_acc_carbon," KgCO2e\na100 in system 2:",sys2_acc_carbon," KgCO2e")

sys1_total_carbon = sys1_acc_carbon + sys1_no_acc_carbon
sys2_total_carbon = sys2_acc_carbon + sys2_no_acc_carbon
print("----- system carbon cost w/ Acc. -----")
# print(sys1.CPU_cost,sys2.CPU_cost)
print("system 1:",sys1_total_carbon," KgCO2e\nsystem 2:",sys2_total_carbon, " KgCO2e")

#----------------------------------------------operational power and break-even time-----------------------------------------------#
#######
# yearly energy cost
#######
sys1_util = 1
sys1_TEC = ((1-sys1_util)*(2*10+39) + sys1_util*(2*10+250)) \
            /1000*365*24 #(idle power + task power)* time
sys2_util = 0.62
sys2_TEC = ((1-sys2_util)*(2*10+53) + sys2_util*(2*10+175)) \
            /1000*365*24

#######
# carbon cost
#######
locations = ["TX","AZ","CA","NY"]
grid_mix = [0.438,0.395,0.234,0.188]

print("----- break-even time -----")
for i in range( len(locations)):
    sys1_op_carbon = sys1_TEC *grid_mix[i]
    sys2_op_carbon = sys2_TEC *grid_mix[i]
    saved_op_carbon = sys1_op_carbon - sys2_op_carbon
    break_even_time = sys2_total_carbon / saved_op_carbon
    print("location:",locations[i]," yearly saved carbon:", saved_op_carbon, "break-even time:",break_even_time)