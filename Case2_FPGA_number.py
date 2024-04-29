# Reproduce of Case study 1 in SCARIF
# setups:
# 1.(CPU server) DellR740 + 2x Intel Xeon 8180 CPU + 64GB DRAM + 1000GB HDD 
# 2.(GPU server) DellR740 + 2x Intel Xeon 8180 CPU + 64GB DRAM + 1000GB HDD + 1x Nvidia V100
# 3.(GPU server) DellR740 + 2x Intel Xeon 8180 CPU + 64GB DRAM + 1000GB HDD + 1x Xilinx ZCU102
# 4.(GPU server) DellR740 + 2x Intel Xeon 8180 CPU + 64GB DRAM + 1000GB HDD + 2x Xilinx ZCU102
# 5.(GPU server) DellR740 + 2x Intel Xeon 8180 CPU + 64GB DRAM + 1000GB HDD + 4x Xilinx ZCU102
# 6.(GPU server) DellR740 + 2x Intel Xeon 8180 CPU + 64GB DRAM + 1000GB HDD + 8x Xilinx ZCU102

# Units:
# 1. DellR740 Carbon footprint report(no CPU part name reported, 32 GB DRAM, 1600 GB HDD): https://i.dell.com/sites/csdocuments/CorpComm_Docs/en/carbon-footprint-poweredge-r740.pdf
# 2. Intel Xeon 8180 CPU: 28 CPU cores, 698 mm2 die size, 14 nm, power: 10(statistic)-250(TDP) W
# 3. Intel Xeon 8375 CPU: 32 CPU cores, 660 mm2 die size, 12 nm, power: 10(statistic)-300(TDP) W
# 4. Nvidia V100: 815 mm2 die size, 12 nm, power: 39(statistic)-250(task) W
# 5. Xilinx ZCU102: 245 mm2 die size, 16 nm, power: 0.83(statistic)-25(task) W

# performance metric:
# 1 V100 has the throughput of 11.05x ZCU102, or 1.32 CPU
# --> compare 1.32x server 1 with 1x server 2, 11.05x server 3, 5,52x server 4, 2.76x server 5 and 1.38x server 6
# all systems running at 100% utilization

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
v100 = 8.15 #cm2
zcu102 = 2.45 #cm2

ic_yield = 0.875

#######
# init ACT tool
#######
xeon_8180_chip = Fab_Logic(gpa  = "95",
                        carbon_intensity = "src_coal",
                        process_node = 14,
                        fab_yield=ic_yield)
v100_chip = Fab_Logic(gpa  = "95",
                        carbon_intensity = "src_coal",
                        process_node = 14,
                        fab_yield=ic_yield)#we use 14 nm as the tech node since ACT doesn't include the 12 nm
zcu102_chip = Fab_Logic(gpa  = "95",
                        carbon_intensity = "src_coal",
                        process_node = 14,
                        fab_yield=ic_yield)#we use 14 nm as the tech node since ACT doesn't include the 16 nm

xeon_8180_chip.set_area(xeon_8180)
v100_chip.set_area(v100)
zcu102_chip.set_area(zcu102)

#######
# get chip carbon
#######
xeon_8180_carbon = xeon_8180_chip.get_carbon()/1000
v100_carbon = v100_chip.get_carbon()/1000
zcu102_carbon = zcu102_chip.get_carbon()/1000
# print("----- chip carbon cost from ACT -----")
print("8180:",xeon_8180_carbon,"\nzcu102:",zcu102_carbon,"\nv100:",v100_carbon)
os.chdir("..")

#----------------------------------------------use SCARIF to estimate system cost-----------------------------------------------#
#######
# get system carbon w/o Acc.
#######
import SCARIF_class
r740 = SCARIF_class.Dell_predictor()
r740.setup(2*28,64,0,1000,2017)
r740_no_acc_carbon = r740.carbon

print("----- system carbon cost w/o Acc. -----")
print("r740 server carbon w/o acc:",r740_no_acc_carbon," KgCO2e")

#######
# get system carbon w/o Acc.
#######
gpu_carbon = r740.CPU_cost*v100_carbon/(xeon_8180_carbon*2)
fpga_carbon = r740.CPU_cost*zcu102_carbon/(xeon_8180_carbon*2)
print("----- system-level Acc. carbon cost -----")
# print(sys1.CPU_cost,sys2.CPU_cost)
print("v100 in system 1:",gpu_carbon," KgCO2e\nzcu102 in system 1:",fpga_carbon," KgCO2e")


#######
# get system carbon w/ Acc.
#######
cpu_total_carbon = r740_no_acc_carbon
gpu_total_carbon = r740_no_acc_carbon + gpu_carbon
fpga_total_carbons = []
for i in range(4):
    fpga_total_carbons.append(r740_no_acc_carbon + fpga_carbon*(2**i))

print("----- system carbon cost w/ Acc. -----")
print("system 1:",cpu_total_carbon,"\nsystem 2:",gpu_total_carbon,"\nsystem 3-6:", fpga_total_carbons)

#######
# normalization by performance
#######
cpu_norm_carbon = cpu_total_carbon* 1.315
gpu_norm_carbon = gpu_total_carbon* 1
fpga_norm_carbons = []
for i in range(4):
    fpga_norm_carbons.append(fpga_total_carbons[i]*(11.0541/(2**i)))
print("----- normalized system carbon cost w/ Acc. -----")
print("system 1:",cpu_norm_carbon,"\nsystem 2:",gpu_norm_carbon,"\nsystem 3-6:", fpga_norm_carbons)

#---------------------------------------------- operational costs-----------------------------------------------#
#######
# normailized yearly carbon cost
# using carbon intensity of AZ
#######
carbon_intensity = 0.395
cpu_op_cost = 205*2 /1000*365*24 * 1.315 * carbon_intensity #power *time * normalization_coef
gpu_op_cost = (2*10+250) /1000*365*24 * 1 * carbon_intensity
fpga_op_cost = []
for i in range(4):
    fpga_op_cost.append( (2*10+(2**i)*25) /1000*365*24 * (11.0541/(2**i)) * carbon_intensity)

print("----- yearly operational carbon cost -----")
print("system 1:",cpu_op_cost,"\nsystem 2:",gpu_op_cost,"\nsystem 3-6:", fpga_op_cost)  


years = [1,4, 7,10,20]
print("----- total carbon summary -----")
print("years\tsys1\tsys2\tsys3\tsys4\tsys5\tsys6\t")
for year in years:
    print(year,"\t",
          cpu_norm_carbon + year* cpu_op_cost, '\t',
          gpu_norm_carbon + year* gpu_op_cost, '\t',
          fpga_norm_carbons[0] +year* fpga_op_cost[0],"\t",
          fpga_norm_carbons[1] +year* fpga_op_cost[1],"\t",
          fpga_norm_carbons[2] +year* fpga_op_cost[2],"\t",
          fpga_norm_carbons[3] +year* fpga_op_cost[3],"\t",
          )
