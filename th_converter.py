import numpy as np
import struct


# I think there is an error in original c file at the line of NUMGEO

class th_reader:
    def __init__(self, fileName):
        self.file = open(fileName, "rb")
        self.read()
        self.file.close()

    def names(self, title, ICODE):
        variables = ["IE", "KE", "XMOM", "YMOM", "ZMOM", "MASS", "HE", "TURBKE", "XCG", "YCG", "ZCG", "XXMOM", "YYMOM",
                     "ZZMOM", "IXX", "IYY", "IZZ", "IXY", "IYZ", "IZX", "RIE", "KERB", "RKERB", "RKE", "HEAT", "ZZMOM", "ZZMOM", "HEAT"]
        if 1 <= ICODE <= 28:
            name = title + " " + variables[ICODE + 1]
        else:
            name = title + " empty"
        return name

    def Ufread(self, Type, numItems, sizeOfItem, column, file):
        total = sizeOfItem * numItems * column
        pchar = self.file.read(total)
        dtype = np.dtype(Type).newbyteorder("big")
        ret = np.ndarray((numItems, column), dtype=dtype, buffer=pchar)
        return ret

    def integer_read(self, sizeOfItem):
        return int.from_bytes(self.file.read(sizeOfItem), "big")

    def float_read(self, sizeOfItem):
        return struct.unpack(">f", self.file.read(sizeOfItem))

    fileName = "Cell_Phone_DropT01"

    def read(self):
        self.file.seek(4, 1)
        thicode = self.integer_read(4)

        if thicode >= 4021:
            titleLength = 100

        elif thicode >= 3041:
            titleLength = 80

        else:
            titleLength = 40

        ccode = self.file.read(80)
        self.file.seek(4, 1)
        self.file.seek(4, 1)
        ccode = self.file.read(80)
        self.file.seek(4, 1)

        # #-------ADDITIONAL RECORDS------------*/
        if thicode > 3050:
            # "ADDITIONAL RECORDS\n");
            self.file.seek(4, 1)
            icode = self.integer_read(4)
            self.file.seek(4, 1)

            # 1ST RECORD : title length*/
            self.file.seek(4, 1)
            icode = self.integer_read(4)
            self.file.seek(4, 1)

            # 2ND RECORD : FAC_MASS,FAC_LENGTH,FAC_TIME */

            self.file.seek(4, 1)
            rcode = self.float_read(4)
            rcode = self.float_read(4)
            rcode = self.float_read(4)
            self.file.seek(4, 1)

        # #-------HIERARCHY INFO------------*/
        # #        printf("*********************************\n");
        #         printf("HIERARCHY INFO_\n");

        self.file.seek(4, 1)
        NPART_NTHPART = self.integer_read(4)
        NUMMAT = self.integer_read(4)
        NUMGEO = self.integer_read(4)
        self.NSUBS = self.integer_read(4)
        NTHGRP2 = self.integer_read(4)
        NGLOB = self.integer_read(4)
        # TODO   Delete below line
        nbglobVar = NGLOB
        self.file.seek(4, 1)
        self.NVAR_PART = np.zeros(NPART_NTHPART, dtype="i")
        NBELEM_THGRP = np.zeros(NTHGRP2)
        self.NVAR_THGRP = np.zeros(NTHGRP2)
        if NGLOB > 0:
            self.file.seek(4, 1)
            for i in range(NGLOB):
                self.file.seek(4, 1)

            self.file.seek(4, 1)
        # -------PART DESCRIPTION------------*/
        #        printf("*********************************\n");
        #        printf("PART DESCRIPTION reading part _%d_\n",NPART_NTHPART);
        #        printf("*********************************\n");*/
        self.NVAR_PART_TOT = 0
        cptThPartNames = 0
        ThPartNames = []
        if NPART_NTHPART > 0:
            for i in range(NPART_NTHPART):
                self.file.seek(4, 1)
                self.file.seek(4, 1)
                title = self.file.read(titleLength)
                self.file.seek(4, 1)
                self.file.seek(4, 1)
                self.file.seek(4, 1)
                self.NVAR = self.integer_read(4)
                self.file.seek(4, 1)

                self.NVAR_PART[i] = self.NVAR
                self.NVAR_PART_TOT = self.NVAR_PART_TOT + self.NVAR

                for j in range(self.NVAR):
                    if j == 0:
                        self.file.seek(4, 1)
                    text = self.integer_read(4)
                    if j == self.NVAR - 1:
                        self.file.seek(4, 1)
                    ThPartNames = self.names(title, text)

        # -------MATER DESCRIPTION------------*/
        #        printf("*********************************\n");
        # printf("MATER DESCRIPTION _%d_\n",NUMMAT);
        # printf("*********************************\n");*/
        if NUMMAT > 0:

            for i in range(NUMMAT):
                self.file.seek(4, 1)
                self.file.seek(4, 1)
                CCODE = self.file.read(titleLength)
                self.file.seek(4, 1)
        # *-------GEO DESCRIPTION------------*/
        # /*        printf("*********************************\n");
        # printf("GEO DESCRIPTION _%d_\n",NUMGEO);
        # printf("*********************************\n");*/
        if NUMGEO > 0:
            for i in range(NUMGEO):
                self.file.seek(4, 1)
                self.file.seek(4, 1)
                CCODE = self.file.read(titleLength)
                self.file.seek(4, 1)

        ThSubsNames = []
        self.NVAR_SUBS = 0
        if self.NSUBS > 0:

            for i in range(self.NSUBS):
                self.file.seek(4, 1)
                self.file.seek(4, 1)

                self.file.seek(4, 1)
                self.NBSUBSF = self.integer_read(4)

                NBPARTF = self.integer_read(4)

                self.NVAR = self.integer_read(4)
                title = self.file.read(titleLength)

                self.file.seek(4, 1)
                if self.NBSUBSF > 0:

                    for j in range(self.NBSUBSF):
                        if j == 0:
                            self.file.seek(4, 1)
                        self.file.seek(4, 1)
                        if j == self.NBSUBSF - 1:
                            self.file.seek(4, 1)
                if NBPARTF > 0:

                    for j in range(NBPARTF):
                        if j == 0:
                            self.file.seek(4, 1)
                        self.file.seek(4, 1)
                        if j == NBPARTF - 1:
                            self.file.seek(4, 1)
                if self.NVAR > 0:

                    for j in range(self.NVAR):
                        if j == 0:
                            self.file.seek(4, 1)
                        text = self.integer_read(4)
                        if j == self.NVAR - 1:
                            self.file.seek(4, 1)
                        self.NVAR_SUBS = self.NVAR_SUBS + 1
                        ThSubsNames = self.names(title, text)

        # *-------TH GROUP------------*/
        # /*        printf("*********************************\n");
        #         printf("TH GROUP_%d_\n",NTHGRP2);
        #         printf("*********************************\n");*/
        ThGroupNames = []
        if NTHGRP2 > 0:
            for i in range(NTHGRP2):
                self.file.seek(4, 1)
                self.file.seek(4, 1)
                self.file.seek(4, 1)
                self.file.seek(4, 1)

                NBELEM = self.integer_read(4)
                NBELEM_THGRP[i] = NBELEM

                self.NVAR = self.integer_read(4)
                self.NVAR_THGRP[i] = self.NVAR

                NameOutput = self.file.read(titleLength)
                self.file.seek(4, 1)

                for j in range(NBELEM):

                    self.file.seek(4, 1)
                    IdRequest = self.integer_read(4)

                    NameRequest = self.file.read(titleLength)

                    self.file.seek(4, 1)

                    for k in range(self.NVAR):
                        ThGroupNames[k] = title

                for j in range(self.NVAR):
                    if j == 0:
                        self.file.seek(4, 1)
                    self.file.seek(4, 1)
                    if j == self.NVAR - 1:
                        self.file.seek(4, 1)

        EndOfFile = 2
        cptData = 0
        self.allData = []
        while EndOfFile == 2:
            # /"*-----------------------------
            #      TIME
            # --------"---------------------*/
            self.file.seek(4, 1)
            code = self.file.read(4)
            if code == b"":
                break
            rcode = struct.unpack(">f", code)
            self.allData.append(rcode)
            cptData += 1
            self.file.seek(4, 1)
            if EndOfFile == 1:
                break
                # //TIME=*RCODE;
            # /*-----------------------------
            #      GLOBAL VARIABLES
            # -----------------------------*/
            nbval = NGLOB
            for i in range(nbval):
                if i == 0:
                    self.file.seek(4, 1)
                code = self.file.read(4)
                if code == b"":
                    break
                rcode = struct.unpack(">f", code)
                self.allData.append(rcode)

                if i == nbval - 1:
                    self.file.seek(4, 1)

        # # /*-----------------------------
        # #      PART VARIABLES
        # # -----------------------------*/
            if (NPART_NTHPART > 0):
                if (self.NVAR_PART_TOT > 0):
                    self.file.seek(4, 1)
                for i in range(NPART_NTHPART):
                    for j in range(self.NVAR_PART[i]):
                        code = self.file.read(4)
                        if code == b"":
                            break
                        rcode = struct.unpack(">f", code)
                        self.allData.append(rcode)

                if (self.NVAR_PART_TOT > 0):
                    self.file.seek(4, 1)

        # # /*-----------------------------
        # #      SUBSET VARIABLES
        # # -----------------------------*/
            if(self.NVAR_SUBS > 0):
                self.file.seek(4, 1)
                for i in range(self.NVAR_SUBS):
                    rcode = self.float_read(4)
                    self.allData.append(rcode)

                self.file.seek(4, 1)

        # # /*-------------------------------------------------------
        # #     TH GROUP
        # # -------------------------------------------------------*/
            for i in range(NTHGRP2):
                self.file.seek(4, 1)
                for j in range(NBELEM_THGRP[i]):
                    for k in range(self.NVAR_THGRP[i]):
                        rcode = self.float_read(4)
                        self.allData.append(rcode)
                self.file.seek(4, 1)
