#The upgrade version for SCARIF v0.2
# - the upgraded flow simplifies the code length a lot

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
# --> compare 1x server 1 running at full utilization with 1x server 2 runing at 0.6 utilization

# operational carbon
# system2 running at 0.62 utilization
# kWh to KgCO2e: TX: 0.438, AZ: 0.395, CA: 0.234, NY: 0.188 KgCO2e/Kwh

#----------------------------------------------use SCARIF to estimate system cost-----------------------------------------------#
#######
# get system carbon w/o Acc.
#######
import SCARIF_class
sys1 = SCARIF_class.Dell_predictor()
sys1.setup(2*28,64,0,1000,2017,acc_tech_node=14,acc_chip_area=815)
sys1_no_acc_carbon = sys1.carbon

sys2 = SCARIF_class.Dell_predictor()
sys2.setup(2*32,64,0,1000,2020,acc_tech_node=7,acc_chip_area=826)
sys2_no_acc_carbon = sys2.carbon

print("----- system carbon costs -----")
print("system 1:\n",sys1,"\nsystem 2:\n",sys2)

sys2_total_carbon = sys2.total_carbon

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