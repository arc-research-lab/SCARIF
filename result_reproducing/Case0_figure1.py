# compute the break-even time of upgrading servers
import SCARIF_class
#system1: HP DL380 base
pred1 = SCARIF_class.HP_predictor()
pred1.setup(44,256,4800,0,2017)
print("HP Proliant DL 380:",pred1.carbon,"KgCO2e vs. Report: 1529 KgCO2e")

#system2:Dell R740
pred2 = SCARIF_class.Dell_predictor()
pred2.setup(44,32,0,4800,2017)
print("Dell R740:",pred2.carbon,"KgCO2e vs. Report: 1313 KgCO2e")

#system3:Dell C4130
pred3 = SCARIF_class.Dell_predictor()
pred3.setup(44,16,200,0,2016)
print("Dell C4130:",pred3.carbon,"KgCO2e vs. Report: 1206 KgCO2e")