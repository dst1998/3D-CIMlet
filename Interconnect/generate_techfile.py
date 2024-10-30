import math,sys

technode = 65
R = 606.321 # float, [Ohm] ( D1=1um Inverter)
MetalPitch_32nm = 0.000100

if technode == 130:
    wireWidth = 175
    vdd = 1.3
    MetalPitch = 340e-06
elif technode == 90:
    wireWidth = 110
    vdd = 1.2
    MetalPitch = 240e-06
elif technode == 65:
    wireWidth = 105
    vdd = 1.1
    MetalPitch = 180e-06
elif technode == 45:
    wireWidth = 80
    vdd = 1.0
    MetalPitch = 160e-06
elif technode == 40:
    wireWidth = 70
    vdd = 0.9
    MetalPitch = 120e-06
elif technode == 32:
    wireWidth = 56
    vdd = 0.9
    MetalPitch = 100e-06
elif technode == 28:
    wireWidth = 50
    vdd = 0.9
    MetalPitch = 100e-06
elif technode == 22:
    wireWidth = 40
    vdd = 0.85
    MetalPitch = 80e-06
elif technode == 16:
    wireWidth = 30
    vdd = 0.8
    MetalPitch = 64e-06
elif technode == 14:
    wireWidth = 25
    vdd = 0.8
    MetalPitch = 64e-06
elif technode == 10:
    vdd = 0.75
    wireWidth = 18
    MetalPitch = 44e-06
elif technode == 7:
    vdd = 0.7
    wireWidth = 18
    MetalPitch = 40e-06
else:
    wireWidth = -1 # Ignore wire resistance or user define
    print("technode:",technode)
    sys.exit("Wire width out of range")

# 其他固定值
IoffSRAM = 0.00000032
IoffP = 0.00000102
IoffN = 0.00000102
Cg_pwr = 0.000000000000000534 * MetalPitch / MetalPitch_32nm
Cd_pwr = 0.000000000000000267 * MetalPitch / MetalPitch_32nm
Cgdl = 0.0000000000000001068 * MetalPitch / MetalPitch_32nm
Cg = 0.000000000000000534 * MetalPitch / MetalPitch_32nm
Cd = 0.000000000000000267 * MetalPitch / MetalPitch_32nm
LAMBDA = technode /2 * 0.001
Rw = 0.720044 * MetalPitch / MetalPitch_32nm
Cw_gnd = 0.000000000000267339 * MetalPitch / MetalPitch_32nm
Cw_cpl = 0.000000000000267339 * MetalPitch / MetalPitch_32nm
wire_length = 2.0 * math.sqrt(technode/32)

# 准备要写入文件的内容
content = f"""// project from '2007 ITRS predictions for a 32nm high-performance library' in booksim
H_INVD2  = 8;//int
W_INVD2  = 3;//int
H_DFQD1  = 8;//int
W_DFQD1  = 16;//int
H_ND2D1  = 8;//int
W_ND2D1  = 3;//int
H_SRAM  = 8;//int
W_SRAM  = 6;//int
Vdd  = {vdd};//float
R  = {R:.3f};//float
IoffSRAM  = {IoffSRAM};//float
// 70 C
IoffP  = {IoffP};//float
IoffN  = {IoffN};//float
Cg_pwr  = {Cg_pwr};//float
Cd_pwr  = {Cd_pwr};//float
Cgdl  = {Cgdl};//float
Cg  = {Cg};//float
Cd  = {Cd};//float
LAMBDA  = {LAMBDA};//float
MetalPitch  = {MetalPitch};//float
Rw  = {Rw};//float
Cw_gnd  = {Cw_gnd};//float
Cw_cpl  = {Cw_cpl};//float
wire_length  = {wire_length};//float
"""

techfile_path = '/home/du335/simulator/Interconnect/techfile_' + str(technode) + 'nm.txt'
with open(techfile_path, 'w') as file:
    file.write(content)

print("New tech file generated successfully.")