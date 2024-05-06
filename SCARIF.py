"""
The command line tool of SCARIF
"""
import os
"""----------
Parse the command line
----------"""
import argparse
parser = argparse.ArgumentParser(
    description="The command line tool of SCARIF")
#Required server config
parser.add_argument('-c','--cpu_core_num', type=int, required=True, help="the total number of CPU cores")
parser.add_argument('-d','--dram', type=int, required=True, help="the size of DRAM [GB]")
parser.add_argument('-s','--ssd', type=int, required=True, help="the size of SSD [GB]")
parser.add_argument('-hd','--hdd', type=int, required=True, help="the size of HDD [GB]")
parser.add_argument('-y','--year', type=int, required=True, help="release year of the server [20xx]")

#Optional Acc config
parser.add_argument('-at','--acc_tech_node', type=int,
                    help="the technology node/ fabrication process of the accelerator [nm], please use together with --acc_chip_area")
parser.add_argument('-aa','--acc_chip_area', type=int, 
                    help="the chip area of the accelerator [mm^2], please use together with --acc_tech_node")

#Optional server config
parser.add_argument('--vendor', type=str, default="HP", help="specify the server vendor to adjust model parameters, won't work if a config is specified")
parser.add_argument('--config', type=str, help="<<<WARNING: this flag haven't be implemented.>>> the path to a predictor config file with json format")

#Optional Acc config
parser.add_argument('--acc_config', type=str, help="<<<WARNING: this flag haven't be implemented.>>> the path to a predictor config file with json format")

args = parser.parse_args()

"""----------
init the predictor
----------"""
#determine to use acc or not
ESTIMATE_ACC = False
if (args.acc_tech_node is not None) and (args.acc_chip_area is not None):
    print("Optional Acc. configs found, will estimate server carbon with Acc.")
    ESTIMATE_ACC = True
else:
    print("Optional Acc. configs not found or incomplete, will estimate server carbon without Acc.")

#get original workdir
basedir = os.getcwd()
#get dir of SCARIF, 
filedir = os.path.dirname(__file__)
#change the workdir since the ACT is sensitive to the work dir
os.chdir(filedir)

#instantiate the predictor
import SCARIF_class
assert args.vendor in SCARIF_class.accepted_vendors, \
    "Error: the vendor {} is not supported currently, accepted vendors: {}" \
    .format(args.vendor,SCARIF_class.accepted_vendors)

predictor = SCARIF_class.predictor(D=SCARIF_class.vendor_to_intercept[args.vendor])

#TODO: add config loader in the scarif class, and implement config loading here

"""----------
perform prediction
----------"""
predictor.setup(args.cpu_core_num,args.dram,args.ssd,args.hdd,args.year,\
                acc_tech_node=args.acc_tech_node, acc_chip_area=args.acc_chip_area)

"""----------
print results
----------"""
print(predictor)
