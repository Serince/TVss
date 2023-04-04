import struct
import os
import numpy as np


class Anime:
    def __init__(self, fileName):
        self.file = open(fileName, "rb")
        magic = self.integer_read(4)
        self.head = {}
        self.head["time"] = self.integer_read(4)  # time of the file
        self.head["time_text"] = self.file.read(81)  # Time text

        FASTMAGI10 = 0x542C
        if magic == FASTMAGI10:
            current_position = self.header()
        self.body(current_position)
        self.file.close()

    def Ufread(self, Type, numItems, sizeOfItem, column):
        total = sizeOfItem * numItems * column
        pchar = self.file.read(total)
        dtype = np.dtype(Type).newbyteorder("big")
        ret = np.ndarray((numItems, column), dtype=dtype, buffer=pchar)
        return ret

    def integer_read(self, sizeOfItem):
        return int.from_bytes(self.file.read(sizeOfItem), "big")

    def header(self):
        # HEADER
        self.head["modanim_text"] = self.file.read(81)  # ModAnim text
        self.head["radiossRun_text"] = self.file.read(81)  # RadiossRun text

        # array of 10 flags
        #        flagA[0] defines if theflagA mass is saved or not
        #        flagA[1] defines if the node-element numbering arrays are saved or not
        #        flagA[2] defines format :if there is 3D geometry
        #        flagA[3] defines format :if there is 1D geometry
        #        flagA[4] defines hierarchy
        #        flagA[5] defines node/elt list for TH
        #        flagA[6] defines if there is a new skew for tensor 2D
        #        flagA[7] define if there is SPH format
        #        flagA[8] to flagsA[9] are not yet used

        self.head["flagA"] = self.Ufread("i4", 10, 4, 1)
        self.head["nbNodes"] = self.integer_read(4)  # number of nodes
        self.head["nbFacets"] = self.integer_read(
            4)  # number of 4nodes elements
        self.head["nbParts"] = self.integer_read(4)  # number of parts
        self.head["nbFunc"] = self.integer_read(
            4)  # number of nodal scalar values
        self.head["nbEFunc"] = self.integer_read(
            4)  # number of elemt scalar values
        self.head["nbVect"] = self.integer_read(4)  # number of vector values
        self.head["nbTens"] = self.integer_read(4)  # number of tensor values
        # number of skews array of the skew values defined in uint16_t * 3000
        self.head["nbSkew"] = self.integer_read(4)
        return self.file.tell()

    def body(self, position=0):
        self.file.seek(position)
        if self.head["nbSkew"]:
            self.skewValA = self.Ufread(
                "uint16", self.head["nbSkew"], 2, 1) / 3000

        # coordinates array: containing the x,y,z coordinates of each node
        self.coorA = self.Ufread("f", self.head["nbNodes"], 4, 3)

        # element connectivity array with local node numbering [0 to (nbNodes-1)]
        if self.head["nbFacets"]:
            self.connectA = self.Ufread("i", self.head["nbFacets"], 4, 4)

            self.delEltA = self.Ufread("bool", self.head["nbFacets"], 1, 1)
            # deleted elements : the deleted elements stay in their original parts,
            # the delEltA indicates which elements are deleted or not

            self.nbDel2D = 0
            for i in range(self.head["nbFacets"]):
                int2D = self.delEltA[i][0]

                if int2D != 0:
                    self.nbDel2D += 1

        # parts definition: array containing an index on thelast facet which defines each part.
        if self.head["nbParts"]:
            self.defPartA = self.Ufread("i", self.head["nbParts"], 4, 1)
            # part texts which defines the name of each part Each name does not exceed 50 characters.
            self.pTextA = self.Ufread(
                "S50", self.head["nbParts"], 50, 1).astype("U50")

        # array of the norm values for each nodes the norm are defined in uint16_t * 3000
        self.normFloatA = self.Ufread(
            "uint16", self.head["nbNodes"], 2, 3) / 3000

        # scalar values
        if self.head["nbFunc"] + self.head["nbEFunc"]:
            # array of total scalar functions names (nodal +  element)
            self.fTextA = self.Ufread(
                "S81", self.head["nbFunc"] + self.head["nbEFunc"], 81, 1).astype("U81")
            if self.head["nbFunc"]:
                self.funcA = self.Ufread(
                    "f", self.head["nbNodes"] * self.head["nbFunc"], 4, 1)
            if self.head["nbEFunc"]:
                self.eFuncA = self.Ufread(
                    "f", self.head["nbFacets"] * self.head["nbEFunc"], 4, 1)

        # vectors values
        if self.head["nbVect"]:
            # array of vector names
            self.vTextA = self.Ufread(
                "S81", self.head["nbVect"], 81, 1).astype("U81")

        # read the array of x,y,z vector values for each node and compute the norm array
        self.vectValA = self.Ufread(
            "f", self.head["nbNodes"] * self.head["nbVect"], 4, 3)

        # tensors values
        if self.head["nbTens"]:
            # array of tensor names
            self.tTextA = self.Ufread(
                "S81", self.head["nbTens"], 81, 1).astype("U81")
            # read the array of x,y,xy tensor values for each element
            self.tensValA = self.Ufread(
                "f", self.head["nbTens"] * self.head["nbFacets"], 4, 3)

        # mass : elementar and nodal masses
        if self.head["flagA"][0]:
            self.eMassA = self.Ufread("f", self.head["nbFacets"], 4, 1)
            self.nMassA = self.Ufread("f", self.head["nbNodes"], 4, 1)

        # node and element numbering
        if self.head["flagA"][1]:
            self.nodNumA = self.Ufread("i", self.head["nbNodes"], 4, 1)
            self.elNumA = self.Ufread("i", self.head["nbFacets"], 4, 1)
            # contains the internal node-element numbers

        if self.head["flagA"][4]:
            #  hierarchy
            #          array of subset for each part
            self.part2subset2DA = self.Ufread(
                "i", self.head["nbParts"], 4, 1)
            #  array of material for each part
            self.partMaterial2DA = self.Ufread(
                "i", self.head["nbParts"], 4, 1)
            #  array of properties for each part
            self.partProperties2DA = self.Ufread(
                "i", self.head["nbParts"], 4, 1)

        # =============================================================================
        # 3D GEOMETRY
        # =============================================================================

        if self.head["flagA"][2]:
            self.head["nbElts3D"] = self.integer_read(
                4)  # number of  8nodes elements
            self.head["nbParts3D"] = self.integer_read(4)  # number of parts
            # number of vol. elt scalar values
            self.head["nbEFunc3D"] = self.integer_read(4)
            # number of tensor values
            self.head["nbTens3D"] = self.integer_read(4)

            # element connectivity array with local node
            #    numbering [0 to (nbNodes-1)]
            #        first element 1st node, first element 2nd node,
            #        first element 3rd node, first element 4th node,
            #        first element 5th node, first element 6th node,
            #        first element 7th node, first element 8th node,

            #        second element 1st node, second element 2nd node,
            #
            self.connect3DA = self.Ufread("i", self.head["nbElts3D"], 4, 8)

            # As the deleted elements stay in their original
            #    parts,
            #        the delEltA indicates which elements are deleted
            #        or not"""
            self.delElt3DA = self.Ufread("bool", self.head["nbElts3D"], 1, 1)
            self.nbEltDel3D = 0
            for idel in range(self.head["nbElts3D"]):
                if self.delElt3DA[idel]:
                    self.nbEltDel3D += 1

                # parts definition: array containing an index on the
                # last facet
                #         which defines each part.
                #         So the 1st part begins with the facet 0 and ends
                #         with the facet
                #         defPartA[0].
                #         The part number i begins with the facet
                #         "defPartA[i-1]" and ends
                #         with the facet "defPartA[i]".

            self.defPart3DA = self.Ufread("i", self.head["nbParts3D"], 4, 1)

            # Part texts which defines the name of each part
            #  Each name does not exceed 50 characters.
            self.pText3DA = self.Ufread(
                "S50", self.head["nbParts3D"], 50, 1).astype("U50")

            #  scalar values
            if self.head["nbEFunc3D"]:
                #  array of scalar functions names
                self.fText3DA = self.Ufread(
                    "S81", self.head["nbEFunc3D"], 81, 1).astype("U81")
                #  array of nodal,element scalar values
                self.eFunc3DA = self.Ufread(
                    "f", self.head["nbEFunc3D"] * self.head["nbElts3D"], 4, 1)

            # tensors values
            if self.head["nbTens3D"]:
                # array of tensor names
                self.tText3DA = self.Ufread(
                    "S81", self.head["nbTens3D"], 81, 1).astype("U81")
                # read the array of x,y,z,xy,yz,zx tensor values for each element
                self.tensVal3DA = self.Ufread(
                    "f", self.head["nbElts3D"] * self.head["nbTens3D"], 4, 6)
            # mass : nodal, elementar mass
            if self.head["flagA"][0]:
                self.eMass3DA = self.Ufread("f", self.head["nbElts3D"], 4, 1)

            # node and element numbering
            if self.head["flagA"][1]:

                self.elNum3DA = self.Ufread("i", self.head["nbElts3D"], 4, 1)

                # contains the internal node-element numbers

            if self.head["flagA"][4]:

                # hierarchy
                # array of subset for each part
                self.part2subset3DA = self.Ufread(
                    "i", self.head["nbParts3D"], 4, 1)
                # array of material for each part
                self.partMaterial3DA = self.Ufread(
                    "i", self.head["nbParts3D"], 4, 1)
                # array of properties for each part
                self.partProperties3DA = self.Ufread(
                    "i", self.head["nbParts3D"], 4, 1)

        # =============================================================================
        # 1D GEOMETRY
        # =============================================================================
        if self.head["flagA"][3]:

            self.nbElts1D = self.integer_read(4)  # number of 2 nodes elements
            self.head["nbParts1D"] = self.integer_read(4)  # number of parts
            # number of line. elt scalar values
            self.head["nbEFunc1D"] = self.integer_read(4)
            self.head["nbTors1D"] = self.integer_read(
                4)  # number of torseur values
            self.head["isSkew1D"] = self.integer_read(
                4)  # is there any skews
            # element connectivity array with local node
            #            numbering [0 to (nbNodes-1)]
            #    first element 1st node, first element 2nd node,
            #    second element 1st node, second element 2nd node,
            #    ...

            self.connect1DA = self.Ufread("i", self.nbElts1D, 4, 2)

            # As the deleted elements stay in their original parts,
            #    the delEltA indicates which elements are deleted or not
            self.delElt1DA = self.Ufread("bool", self.nbElts1D, 1, 1)

            # parts definition: array containing an index on the
            #    last facet
            #    which defines each part.
            #    So the 1st part begins with the facet 0 and ends
            #    with the facet
            #    defPartA[0].
            #    The part number i begins with the facet
            #    "defPartA[i-1]" and ends
            #    with the facet "defPartA[i]".

            self.defPart1DA = self.Ufread("i", self.head["nbParts1D"], 4, 1)
            # part texts which defines the name of each part
            #    Each name does not exceed 50 characters.
            self.pText1DA = self.Ufread("S50", self.head["nbParts1D"], 50, 1)

            # scalar values
            if self.head["nbEFunc1D"]:

                # array of scalar functions names

                self.fText1DA = self.Ufread(
                    "S81", self.head["nbEFunc1D"], 81, 1).astype("U81")

                # array of nodal,element scalar values
                self.eFunc1DA = self.Ufread(
                    "f", self.nbElts1D * self.head["nbEFunc1D"], 4, 1)

            # tensors values
            if self.head["nbTors1D"]:

                # array of tensor names
                self.tText1DA = self.Ufread(
                    "S81", self.head["nbTors1D"], 81, 1).astype("U81")

                # read the array of x,y,z,xy,yz,zx tensor values for each element
                self.torsVal1DA = self.Ufread(
                    "f", self.nbElts1D * self.head["nbTors1D"], 4, 9)

            if self.head["isSkew1D"]:

                # array of the skew number for each elt
                self.elt2Skew1DA = self.Ufread("i", self.nbElts1D, 4, 1)

            # mass : nodal, elementar mass
            if self.head["flagA"][0]:

                self.eMass1DA = self.Ufread("f", self.nbElts1D, 4, 1)

            # node and element numbering
            if self.head["flagA"][1]:

                self.elNum1DA = self.Ufread("i", self.nbElts1D, 4, 1)

            # contains the internal node-element numbers

            if self.head["flagA"][4]:
                # hierarchy
                # array of subset for each part
                self.part2subset1DA = self.Ufread(
                    "i", self.head["nbParts1D"], 4, 1)

                # array of material for each part
                self.partMaterial1DA = self.Ufread(
                    "i", self.head["nbParts1D"], 4, 1)

                # array of properties for each part
                self.partProperties1DA = self.Ufread(
                    "i", self.head["nbParts1D"], 4, 1)

        # hierarchy
        if self.head["flagA"][4]:

            self.nbSubsets = self.integer_read(4)  # number of subsets
            for i in range(self.nbSubsets):
                # subset name
                self.file.read(50)  # subsetText =

                # parent number
                self.numParent = self.integer_read(4)
                # number of subsets sons
                self.nbSubsetSon = self.integer_read(4)

                # list of son subset
                if self.nbSubsetSon:
                    self.Ufread("i", self.nbSubsetSon, 4, 1)  # subsetSonA =

                # number of 2D SubParts
                self.nbSubPart2D = self.integer_read(4)
                if self.nbSubPart2D:
                    # list of 2D SubParts
                    self.Ufread("i", self.nbSubPart2D, 4, 1)  # subPart2DA =

                # number of 3D SubParts
                self.nbSubPart3D = self.integer_read(4)
                if self.nbSubPart3D:
                    # list of 3D SubParts
                    self.Ufread("i", self.nbSubPart3D, 4, 1)  # subPart3DA =

                # number of 1D SubParts
                self.nbSubPart1D = self.integer_read(4)
                if self.nbSubPart1D:
                    # list of 1D SubParts
                    self.Ufread("i", self.nbSubPart1D, 4, 1)  # subPart1DA =

            # number of Material
            self.nbMaterial = self.integer_read(4)
            # number of Properties
            self.nbProperties = self.integer_read(4)
            # material names
            self.materialTextA = self.Ufread("S50", self.nbMaterial, 50, 1)

            # material types
            self.materialTypeA = self.Ufread("i", self.nbMaterial, 4, 1)
            # properties names
            self.propertiesTextA = self.Ufread("S50", self.nbProperties, 50, 1)

            # properties types
            self.propertiesTypeA = self.Ufread("i", self.nbProperties, 4, 1)

        # =============================================================================
        # NODES/ELTS FOR Time History ( nodes & elems that are also selected for Time History output)
        # =============================================================================
        if self.head["flagA"][5]:

            self.head["nbNodesTH"] = self.integer_read(
                4)  # number of Time History nodes
            # number of Time History 2D elements
            self.nbElts2DTH = self.integer_read(4)
            # number of Time History 3D elements
            self.head["nbElts3DTH"] = self.integer_read(4)
            # number of Time History 1D elements
            self.nbElts1DTH = self.integer_read(4)
            # node list
            self.nodes2THA = self.Ufread("i", self.head["nbNodesTH"], 4, 1)
            # node names
            self.n2thTextA = self.Ufread(
                "S50", self.head["nbNodesTH"], 50, 1)

            # elt 2D list
            self.elt2DTHA = self.Ufread("i", self.nbElts2DTH, 4, 1)
            # elt 2D name
            self.elt2DthTextA = self.Ufread("S50", self.nbElts2DTH, 50, 1)

            # elt 3D list
            self.elt3DTHA = self.Ufread("i", self.head["nbElts3DTH"], 4, 1)
            # elt 3D name
            self.elt3DthTextA = self.Ufread(
                "S50", self.head["nbElts3DTH"], 50, 1)

            # elt 1D list
            self.elt1DTHA = self.Ufread("i", self.nbElts1DTH, 4, 1)
            # elt 1D name
            self.elt1DthTextA = self.Ufread("S50", self.nbElts1DTH, 50, 1)

        # =============================================================================
        # READ SPH PART */
        # =============================================================================
        if self.head["flagA"][7]:
            self.head["nbEltsSPH"] = self.integer_read(4)
            self.head["nbPartsSPH"] = self.integer_read(4)
            self.head["nbEFuncSPH"] = self.integer_read(4)
            self.head["nbTensSPH"] = self.integer_read(4)

            if self.head["nbEltsSPH"]:
                self.connecSPH = self.Ufread(
                    "i", self.head["nbEltsSPH"], 4, 1)
                self.delEltSPH = self.Ufread(
                    "bool", self.head["nbEltsSPH"], 1, 1)

            if self.head["nbPartsSPH"]:

                self.defPartSPH = self.Ufread(
                    "i", self.head["nbPartsSPH"], 4, 1)

                # part texts which defines the name of each part
                #  Each name does not exceed 50 characters.
                self.pTextSPH = self.Ufread(
                    "S50", self.head["nbPartsSPH"], 50, 1)

            if self.head["nbEFuncSPH"]:

                self.scalTextSPH = self.Ufread(
                    "S81", self.head["nbEFuncSPH"], 81, 1).astype("U81")

                self.eFuncSPH = self.Ufread(
                    "f", self.head["nbEFuncSPH"] * self.head["nbEltsSPH"], 4, 1)

            if self.head["nbTensSPH"]:
                # SPH tensors are just like 3D tensors
                self.tensTextSPH = self.Ufread(
                    "S81", self.head["nbTensSPH"], 81, 1).astype("U81")
                self.tensValSPH = self.Ufread(
                    "f", self.bEltsSPH * self.head["nbTensSPH"], 4, 6)

            # sph mass
            if self.head["flagA"][0]:
                self.eMassSPH = self.Ufread(
                    "f", self.head["nbEltsSPH"], 4, 1)

            # sph numbering
            if self.head["flagA"][1]:
                self.nodNumSPH = self.Ufread(
                    "i", self.head["nbEltsSPH"], 4, 1)

            # SPH HIERARCHY
            if self.head["flagA"][4]:

                # parent number
                self.numParentSPH = self.Ufread(
                    "i", self.head["nbPartsSPH"], 4, 1)
                self.matPartSPH = self.Ufread(
                    "i", self.head["nbPartsSPH"], 4, 1)
                self.propPartSPH = self.Ufread(
                    "i", self.head["nbPartsSPH"], 4, 1)


animation = []
for i in os.listdir():
    if i[-4] == "A" and i[-3:].isnumeric():
        animation.append(Anime(i))
        ali = Anime(i)
        break

# %%


with open("anime.vtk", "w") as file:

    file.write("# vtk DataFile Version 3.0\n")
    file.write("vtk output\n")
    file.write("ASCII\n")
    file.write("DATASET UNSTRUCTURED_GRID\n")

    file.write("FIELD FieldData 2\n")
    file.write("TIME 1 1 double\n")
    file.write(str(ali.head["time"]))
    file.write("\nCYCLE 1 1 int"+"\n")
    file.write("0")

    # nodes
    file.write(f"\nPOINTS {ali.head['nbNodes']} float\n")
    np.savetxt(file, ali.coorA, delimiter=" ", fmt="%f")
    file.write("\n")
    # elements connectivity

    for i in range(4):
        # defining nonexisting element types as 0
        try:
            cellNumber = ali.head["nbElts1D"]+ali.head["nbFacets"] + \
                ali.head["nbElts3D"]+ali.head["nbEltsSPH"]
            break
        except Exception as e:
            ali.head[e.args[0]] = 0

    pointnumber = 3 * ali.head["nbElts1D"]+5*ali.head["nbFacets"] + \
        9*ali.head["nbElts3D"]+2 * ali.head["nbEltsSPH"]
    file.write(f"CELLS {cellNumber} {pointnumber}\n")
    if ali.head["nbElts1D"]:
        stack = np.hstack(
            (2*np.ones((len(ali.connect1DA), 1)), ali.connect1DA))
        np.savetxt(file, stack, delimiter=" ", fmt="%i")
    if ali.head["nbFacets"]:
        stack = np.hstack((4*np.ones((len(ali.connectA), 1)), ali.connectA))
        np.savetxt(file, stack, delimiter=" ", fmt="%i")
    if ali.head["nbElts3D"]:
        stack = np.hstack(
            (8*np.ones((len(ali.connect3DA), 1)), ali.connect3DA))
        np.savetxt(file, stack, delimiter=" ", fmt="%i")
    if ali.head["nbEltsSPH"]:
        stack = np.hstack(
            np.ones((len(ali.connecSPH), 1)), ali.connecSPH)
        np.savetxt(file, stack, delimiter=" ", fmt="%i")

    # elements type
    file.write(f"CELL_TYPES {cellNumber}\n")
    if ali.head["nbElts1D"]:
        np.savetxt(file, 3*np.ones((len(ali.connect1DA), 1), dtype="i"),
                   delimiter=" ", fmt="%i")
    if ali.head["nbFacets"]:
        np.savetxt(file, 9*np.ones((len(ali.connectA), 1), dtype="i"),
                   delimiter=" ", fmt="%i")
    if ali.head["nbElts3D"]:
        np.savetxt(file, 12*np.ones((len(ali.connect3DA), 1), dtype="i"),
                   delimiter=" ", fmt="%i")
    if ali.head["nbEltsSPH"]:
        np.savetxt(file, np.ones((len(ali.connecSPH), 1), dtype="i"),
                   delimiter=" ", fmt="%i")

    # // nodal scalars & vectors
    file.write(f"POINT_DATA {ali.head['nbNodes']}\n")
    # // node id
    file.write("SCALARS NODE_ID int 1\n")
    file.write("LOOKUP_TABLE default\n")

    np.savetxt(file, ali.nodNumA, delimiter=" ", fmt="%i")
    # try:
    funcA = ali.funcA.reshape((ali.head["nbFunc"], ali.head["nbNodes"]))
    for i in range(len(funcA)):
        fTextA = ali.fTextA[i][0].replace(" ", "_")
        file.write(f"SCALARS {fTextA} float 1\n")
        file.write("LOOKUP_TABLE default\n")
        np.savetxt(file, funcA[i], delimiter=" ", fmt="%i")
    # except:
    #     pass

    # try:
    vectValA = np.array_split(ali.vectValA, 3)
    for i in range(len(ali.vTextA)):
        vTextA = ali.vTextA[i][0].replace(" ", "_")
        file.write(f"VECTORS {vTextA} float 1\n")
        np.savetxt(file, vectValA[i], delimiter=" ", fmt="%f")
    # except:
    #     pass
    file.write(f"CELL_DATA {cellNumber}\n")
# / element id
    file.write("SCALARS ELEMENT_ID int 1\n")
    file.write("LOOKUP_TABLE default\n")

    if ali.head["nbElts1D"]:
        np.savetxt(file, ali.elNum1DA, delimiter="\n", fmt="%i")
    if ali.head["nbFacets"]:
        np.savetxt(file, ali.elNumA, delimiter="\n", fmt="%i")
    if ali.head["nbElts3D"]:
        np.savetxt(file, ali.elNum3DA, delimiter="\n", fmt="%i")
    if ali.head["nbEltsSPH"]:
        np.savetxt(file, ali.nodNumSPH, delimiter="\n", fmt="%i")

    # // part id
    file.write("SCALARS PART_ID int 1\n")
    file.write("LOOKUP_TABLE default\n")

    # defining nonexisting parts as 0
    try:
        ali.defPart1DA
        for j, i in enumerate(ali.defPart1DA):
            defPart = np.ones((i[0], 1))*int(ali.pText1DA[j][0].split(":")[0])
            np.savetxt(file, defPart, delimiter="\n", fmt="%i")
    except:
        pass

    try:
        for j, i in enumerate(ali.defPartA):
            defPart = np.ones((i[0], 1))*int(ali.pTextA[j][0].split(":")[0])
            np.savetxt(file, defPart, delimiter="\n", fmt="%i")
    except:
        pass

    try:
        for j, i in enumerate(ali.defPart3DA):
            defPart = np.ones((i[0], 1))*int(ali.pText3DA[j][0].split(":")[0])
            np.savetxt(file, defPart, delimiter="\n", fmt="%i")

    except:
        pass

    try:

        for j, i in enumerate(ali.defPartSPH):
            defPart = np.ones((i[0], 1))*int(ali.pTextSPH[j][0].split(":")[0])
            np.savetxt(file, defPart, delimiter="\n", fmt="%i")
    except:
        pass
   # // element erosion status ( 0:off, 1:on )
    file.write("SCALARS EROSION_STATUS int 1\n")
    file.write("LOOKUP_TABLE default\n")

    if ali.head["nbElts1D"]:
        np.savetxt(file, 1*ali.delElt1DA, delimiter="\n", fmt="%i")
    if ali.head["nbFacets"]:
        np.savetxt(file, 1*ali.delEltA, delimiter="\n", fmt="%i")
    if ali.head["nbElts3D"]:
        np.savetxt(file, 1*ali.delElt3DA, delimiter="\n", fmt="%i")
    if ali.head["nbEltsSPH"]:
        np.savetxt(file, 1*ali.delEltSPH, delimiter="\n", fmt="%i")
# // elemental scalars & tensors
    if ali.head["flagA"][3]:  # if 1D element exist
        eFunc1DA = np.array_split(ali.eFunc1DA, ali.head["nbEFunc1D"])
        for i in range(ali.head["nbEFunc1D"]):
            fText1DA = ali.fText1DA[i][0].replace(" ", "_")
            file.write(f"SCALARS 1DELEM_{fText1DA} float 1\n")
            file.write("LOOKUP_TABLE default\n")
            np.savetxt(file, eFunc1DA[i], delimiter=" ", fmt="%f")
            np.savetxt(file, np.zeros(
                ali.head["nbFacets"]+ali.head["nbElts3D"]+ali.head["nbEltsSPH"]), delimiter="\n", fmt="%i")

    try:
        eFuncA = np.array_split(ali.eFuncA, ali.head["nbEFuncA"])
        for i in range(ali.head["nbEFunc"]):
            fTextA = ali.fTextA[i][0].replace(" ", "_")
            file.write(f"SCALARS 2DELEM_{fTextA} float 1\n")
            file.write("LOOKUP_TABLE default\n")
            np.savetxt(file, np.zeros(
                ali.head["nbElts1D"]), delimiter="\n", fmt="%i")
            np.savetxt(file, eFuncA[i], delimiter=" ", fmt="%f")
            np.savetxt(file, np.zeros(
                ali.head["nbElts3D"]+ali.head["nbEltsSPH"]), delimiter="\n", fmt="%i")
        tensValA = ali.tensValA.reshape((3*ali.head["nbFacets"], 3))
        for i in range(ali.head["nbTens"]):
            tTextA = ali.tTextA[i][0].replace(" ", "_")
            file.write(f"TENSORS 2DELEM_{tTextA} float 1\n")
            file.write("LOOKUP_TABLE default\n")
            np.savetxt(file, np.zeros(
                (3*ali.head["nbElts1D"], 3)), delimiter=" ", fmt="%i")
            np.savetxt(file, tensValA[i], delimiter=" ", fmt="%f")
            np.savetxt(file, np.zeros(
                (3*(ali.head["nbElts3D"]+ali.head["nbEltsSPH"]), 3)), delimiter=" ", fmt="%i")

    except:
        pass

    if ali.head["flagA"][2]:  # if 3d elemnts exist
        eFunc3DA = np.array_split(ali.eFunc3DA, ali.head["nbEFunc3D"])
        for i in range(ali.head["nbEFunc3D"]):
            fText3DA = ali.fText3DA[i][0].replace(" ", "_")
            file.write(f"SCALARS 3DELEM_{fText3DA} float 1\n")
            file.write("LOOKUP_TABLE default\n")
            np.savetxt(file, np.zeros(
                ali.head["nbElts1D"]+ali.head["nbFacets"]), delimiter="\n", fmt="%i")
            np.savetxt(file, eFunc3DA[i], delimiter=" ", fmt="%f")
            np.savetxt(file, np.zeros(
                ali.head["nbEltsSPH"]), delimiter="\n", fmt="%i")
        nbElts3D = ali.head["nbElts3D"]
        tensVal3DA = np.zeros((ali.head["nbTens3D"], nbElts3D*3, 3))

        for k in range(ali.head["nbTens3D"]):
            for i in range(nbElts3D):
                tensVal3DA[k, 3*i, 0] = ali.tensVal3DA[k*nbElts3D+i, 0]
                tensVal3DA[k, 3*i, 1] = ali.tensVal3DA[k*nbElts3D+i, 3]
                tensVal3DA[k, 3*i, 2] = ali.tensVal3DA[k*nbElts3D+i, 4]
                tensVal3DA[k, 3*i+1, 0] = ali.tensVal3DA[k*nbElts3D+i, 3]
                tensVal3DA[k, 3*i+1, 1] = ali.tensVal3DA[k*nbElts3D+i, 1]
                tensVal3DA[k, 3*i+1, 2] = ali.tensVal3DA[k*nbElts3D+i, 5]
                tensVal3DA[k, 3*i+2, 0] = ali.tensVal3DA[k*nbElts3D+i, 4]
                tensVal3DA[k, 3*i+2, 1] = ali.tensVal3DA[k*nbElts3D+i, 5]
                tensVal3DA[k, 3*i+2, 2] = ali.tensVal3DA[k*nbElts3D+i, 2]

        for i in range(ali.head["nbTens3D"]):
            tText3DA = ali.tText3DA[i][0].replace(" ", "_")
            file.write(f"TENSORS 3DELEM_{tText3DA} float 1\n")
            file.write("LOOKUP_TABLE default\n")
            np.savetxt(file, np.zeros(
                (3*(ali.head["nbElts1D"]+ali.head["nbFacets"]), 3)), delimiter=" ", fmt="%i")
            np.savetxt(file, tensVal3DA[i], delimiter=" ", fmt="%f")
            np.savetxt(file, np.zeros(
                (3*ali.head["nbEltsSPH"], 3)), delimiter=" ", fmt="%i")

    if ali.head["flagA"][7]:
        eFuncSPH = np.array_split(ali.eFuncSPH, ali.head["nbEFuncSPH"])
        for i in range(ali.head["nbEFuncSPH"]):
            fTextSPH = ali.fTextSPH[i][0].replace(" ", "_")
            file.write(f"SCALARS 3DELEM_{fTextSPH} float 1\n")
            file.write("LOOKUP_TABLE default\n")
            np.savetxt(file, np.zeros(
                ali.head["nbElts1D"]+ali.head["nbFacets"]+ali.head["nbElts3D"]), delimiter="\n", fmt="%i")
            np.savetxt(file, eFuncSPH[i], delimiter=" ", fmt="%f")

        for i in range(ali.head["nbTensSPH"]):
            tText3DA = ali.tText3DA[i][0].replace(" ", "_")
            file.write(f"TENSORS 3DELEM_{tText3DA} float 1\n")
            file.write("LOOKUP_TABLE default\n")
            np.savetxt(file, np.zeros(
                (3*(ali.head["nbElts1D"]+ali.head["nbFacets"]+ali.head["nbElts3D"]), 3)), delimiter=" ", fmt="%i")
            np.savetxt(file, ali.tensValSPH[i], delimiter=" ", fmt="%f")

    # for i in
    # satır 1147


# with open("d3plot02", "wb") as file:
#     title = "LS-DYNA keyword deck by LS-PrePost      "  # " "*40
#     one = 1
#     two = 2
#     zero = 0
#     three = 3
#     four = 4
#     file.write(title.encode())
#     file.write(animation[0].header["time"].to_bytes(4, "little"))
#     file.write(one.to_bytes(4, "little"))
#     lsdyna = 971129956
#     file.write(lsdyna.to_bytes(4, "little"))
#     RelNo = "R110"
#     file.write(RelNo.encode())
#     ver = 960.0
#     file.write(struct.pack('<f', ver))
#     file.write(four.to_bytes(4, "little"))
#     # buraya kadar kontrol edildi
#     file.write(animation[0].nbNodes.to_bytes(4, "little"))
#     file.write(two.to_bytes(4, "little"))
#     NGLBV = 6*(1+animation[0].nbMaterial+animation[0].nbSubsets)
#     file.write(NGLBV.to_bytes(4, "little"))
#     file.write(zero.to_bytes(4, "little"))
#     file.write(one.to_bytes(4, "little"))
#     file.write(one.to_bytes(4, "little"))
#     file.write(one.to_bytes(4, "little"))
#     file.write(animation[0].nbElts3D)
#     file.write(animation[0].nbMaterial)
#     file.write(0)
#     file.write(0)
#     file.write(7)
#     file.write(animation[0].nbElts1D)
#     file.write(animation[0].nbMaterial)
#     file.write(6)
#     file.write(animation[0].nbElts2DTH)
#     file.write(animation[0].nbMaterial)
#     file.write(one.to_bytes(4, "big"))
