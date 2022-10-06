import numpy as np
import struct


# I think there is an error in original c file at the line of NUMGEO

# def unpack(numItems, file):
#     return struct.unpack("s" * numItems, file.read(numItems))
def names(title, ICODE):
    variables = ["IE", "KE", "XMOM", "YMOM", "ZMOM", "MASS", "HE", "TURBKE", "XCG", "YCG", "ZCG", "XXMOM", "YYMOM",
                 "ZZMOM", "IXX", "IYY", "IZZ", "IXY", "IYZ", "IZX", "RIE", "KERB", "RKERB", "RKE", "HEAT", "ZZMOM", "ZZMOM", "HEAT"]
    if 1 <= ICODE <= 28:
        name = title + " " + variables[ICODE + 1]
    else:
        name = title + " empty"
    return name


def Ufread(Type, numItems, sizeOfItem, column, file):
    total = sizeOfItem * numItems * column
    pchar = file.read(total)
    dtype = np.dtype(Type).newbyteorder("big")
    ret = np.ndarray((numItems, column), dtype=dtype, buffer=pchar)
    return ret


fileName = "Cell_Phone_DropT01"

file = open(fileName, "rb")


length = int.from_bytes(file.read(4), "big")
thicode = int.from_bytes(file.read(4), "big")


if thicode >= 4021:
    titleLength = 100

elif thicode >= 3041:
    titleLength = 80

else:
    titleLength = 40


ccode = file.read(80)
length = int.from_bytes(file.read(4), "big")
length = int.from_bytes(file.read(4), "big")
ccode = file.read(80)
length = int.from_bytes(file.read(4), "big")

# #-------ADDITIONAL RECORDS------------*/
if thicode > 3050:
    # "ADDITIONAL RECORDS\n");
    length = int.from_bytes(file.read(4), "big")
    icode = int.from_bytes(file.read(4), "big")
    length = int.from_bytes(file.read(4), "big")

    # 1ST RECORD : title length*/
    length = int.from_bytes(file.read(4), "big")
    icode = int.from_bytes(file.read(4), "big")
    length = int.from_bytes(file.read(4), "big")

    # 2ND RECORD : FAC_MASS,FAC_LENGTH,FAC_TIME */

    length = int.from_bytes(file.read(4), "big")
    rcode = struct.unpack(">f", file.read(4))
    rcode = struct.unpack(">f", file.read(4))
    rcode = struct.unpack(">f", file.read(4))
    length = int.from_bytes(file.read(4), "big")

# #-------HIERARCHY INFO------------*/
# #        printf("*********************************\n");
#         printf("HIERARCHY INFO_\n");

length = int.from_bytes(file.read(4), "big")
NPART_NTHPART = int.from_bytes(file.read(4), "big")
NUMMAT = int.from_bytes(file.read(4), "big")
NUMGEO = int.from_bytes(file.read(4), "big")
NSUBS = int.from_bytes(file.read(4), "big")
NTHGRP2 = int.from_bytes(file.read(4), "big")
NGLOB = int.from_bytes(file.read(4), "big")
# TODO   Delete below line
nbglobVar = NGLOB
length = int.from_bytes(file.read(4), "big")
NVAR_PART = np.zeros(NPART_NTHPART, dtype="i")
NBELEM_THGRP = np.zeros(NTHGRP2)
NVAR_THGRP = np.zeros(NTHGRP2)
if NGLOB > 0:
    length = int.from_bytes(file.read(4), "big")
    for i in range(NGLOB):
        ICODE = int.from_bytes(file.read(4), "big")

    length = int.from_bytes(file.read(4), "big")
# -------PART DESCRIPTION------------*/
#        printf("*********************************\n");
#        printf("PART DESCRIPTION reading part _%d_\n",NPART_NTHPART);
#        printf("*********************************\n");*/
NVAR_PART_TOT = 0
cptThPartNames = 0
ThPartNames = []
if NPART_NTHPART > 0:
    for i in range(NPART_NTHPART):
        length = int.from_bytes(file.read(4), "big")
        ICODE = int.from_bytes(file.read(4), "big")
        title = file.read(titleLength)
        ICODE = int.from_bytes(file.read(4), "big")
        ICODE = int.from_bytes(file.read(4), "big")
        ICODE = int.from_bytes(file.read(4), "big")
        NVAR = int.from_bytes(file.read(4), "big")
        length = int.from_bytes(file.read(4), "big")

        NVAR_PART[i] = NVAR
        NVAR_PART_TOT = NVAR_PART_TOT + NVAR

        for j in range(NVAR):
            if j == 0:
                length = int.from_bytes(file.read(4), "big")
            ICODE = int.from_bytes(file.read(4), "big")
            if j == NVAR - 1:
                length = int.from_bytes(file.read(4), "big")
            ThPartNames = names(title, ICODE)

# -------MATER DESCRIPTION------------*/
#        printf("*********************************\n");
# printf("MATER DESCRIPTION _%d_\n",NUMMAT);
# printf("*********************************\n");*/
if NUMMAT > 0:

    for i in range(NUMMAT):
        length = int.from_bytes(file.read(4), "big")
        ICODE = int.from_bytes(file.read(4), "big")
        CCODE = file.read(titleLength)
        length = int.from_bytes(file.read(4), "big")
# *-------GEO DESCRIPTION------------*/
# /*        printf("*********************************\n");
# printf("GEO DESCRIPTION _%d_\n",NUMGEO);
# printf("*********************************\n");*/
if NUMGEO > 0:
    for i in range(NUMGEO):
        length = int.from_bytes(file.read(4), "big")
        ICODE = int.from_bytes(file.read(4), "big")
        CCODE = file.read(titleLength)
        length = int.from_bytes(file.read(4), "big")

ThSubsNames = []
NVAR_SUBS = 0
if NSUBS > 0:

    for i in range(NSUBS):
        length = int.from_bytes(file.read(4), "big")
        ICODE = int.from_bytes(file.read(4), "big")

        ICODE = int.from_bytes(file.read(4), "big")
        NBSUBSF = int.from_bytes(file.read(4), "big")

        NBPARTF = int.from_bytes(file.read(4), "big")

        NVAR = int.from_bytes(file.read(4), "big")
        title = file.read(titleLength)

        length = int.from_bytes(file.read(4), "big")
        if NBSUBSF > 0:

            for j in range(NBSUBSF):
                if j == 0:
                    length = int.from_bytes(file.read(4), "big")
                ICODE = int.from_bytes(file.read(4), "big")
                if j == NBSUBSF - 1:
                    length = int.from_bytes(file.read(4), "big")
        if NBPARTF > 0:

            for j in range(NBPARTF):
                if j == 0:
                    length = int.from_bytes(file.read(4), "big")
                ICODE = int.from_bytes(file.read(4), "big")
                if j == NBPARTF - 1:
                    length = int.from_bytes(file.read(4), "big")
        if NVAR > 0:

            for j in range(NVAR):
                if j == 0:
                    length = int.from_bytes(file.read(4), "big")
                ICODE = int.from_bytes(file.read(4), "big")
                if j == NVAR - 1:
                    length = int.from_bytes(file.read(4), "big")
                NVAR_SUBS = NVAR_SUBS + 1
                ThSubsNames = names(title, ICODE)

# *-------TH GROUP------------*/
# /*        printf("*********************************\n");
#         printf("TH GROUP_%d_\n",NTHGRP2);
#         printf("*********************************\n");*/
ThGroupNames = []
if NTHGRP2 > 0:
    for i in range(NTHGRP2):
        length = int.from_bytes(file.read(4), "big")
        ICODE = int.from_bytes(file.read(4), "big")
        ICODE = int.from_bytes(file.read(4), "big")
        ICODE = int.from_bytes(file.read(4), "big")

        NBELEM = int.from_bytes(file.read(4), "big")
        NBELEM_THGRP[i] = NBELEM

        NVAR = int.from_bytes(file.read(4), "big")
        NVAR_THGRP[i] = NVAR

        NameOutput = file.read(titleLength)
        length = int.from_bytes(file.read(4), "big")

        for j in range(NBELEM):

            length = int.from_bytes(file.read(4), "big")
            IdRequest = int.from_bytes(file.read(4), "big")

            NameRequest = file.read(titleLength)

            length = int.from_bytes(file.read(4), "big")

            for k in range(NVAR):
                ThGroupNames[k] = title

        for j in range(NVAR):
            if j == 0:
                length = int.from_bytes(file.read(4), "big")
            ICODE = int.from_bytes(file.read(4), "big")
            if j == NVAR - 1:
                length = int.from_bytes(file.read(4), "big")

EndOfFile = 2
cptData = 0
allData = []
while EndOfFile == 2:
    # /"*-----------------------------
    #      TIME
    # --------"---------------------*/
    length = int.from_bytes(file.read(4), "big")
    code = file.read(4)
    if code == b"":
        break
    rcode = struct.unpack(">f", code)
    allData.append(rcode)
    cptData += 1
    length = int.from_bytes(file.read(4), "big")
    if EndOfFile == 1:
        break
        # //TIME=*RCODE;
    # /*-----------------------------
    #      GLOBAL VARIABLES
    # -----------------------------*/
    nbval = NGLOB
    for i in range(nbval):
        if i == 0:
            length = int.from_bytes(file.read(4), "big")
        code = file.read(4)
        if code == b"":
            break
        rcode = struct.unpack(">f", code)
        allData.append(rcode)

        if i == nbval - 1:
            length = int.from_bytes(file.read(4), "big")

# # /*-----------------------------
# #      PART VARIABLES
# # -----------------------------*/
    if (NPART_NTHPART > 0):
        if (NVAR_PART_TOT > 0):
            length = int.from_bytes(file.read(4), "big")
        for i in range(NPART_NTHPART):
            for j in range(NVAR_PART[i]):
                code = file.read(4)
                if code == b"":
                    break
                rcode = struct.unpack(">f", code)
                allData.append(rcode)

        if (NVAR_PART_TOT > 0):
            length = int.from_bytes(file.read(4), "big")

# # /*-----------------------------
# #      SUBSET VARIABLES
# # -----------------------------*/
    if(NVAR_SUBS > 0):
        length = int.from_bytes(file.read(4), "big")
        for i in range(NVAR_SUBS):
            rcode = struct.unpack(">f", file.read(4))
            allData.append(rcode)

        length = int.from_bytes(file.read(4), "big")


# # /*-------------------------------------------------------
# #     TH GROUP
# # -------------------------------------------------------*/
    for i in range(NTHGRP2):
        length = int.from_bytes(file.read(4), "big")
        for j in range(NBELEM_THGRP[i]):
            for k in range(NVAR_THGRP[i]):
                rcode = struct.unpack(">f", file.read(4))
                allData.append(rcode)
        length = int.from_bytes(file.read(4), "big")

file.close()
