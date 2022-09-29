import numpy as np


class Anime:
    def __init__(self, fileName):
        self.file = file = open(fileName, "rb")
        self.read()
        self.file.close()

    def Ufread(self, Type, numItems, sizeOfItem, column):
        total = sizeOfItem * numItems * column
        pchar = self.file.read(total)
        dtype = np.dtype(Type).newbyteorder("big")
        ret = np.ndarray((numItems, column), dtype=dtype, buffer=pchar)
        return ret

    def read(self):
        # HEADER
        magic = int.from_bytes(self.file.read(4), "big")
        FASTMAGI10 = 0x542C
        if magic == FASTMAGI10:
            self.time = int.from_bytes(self.file.read(4), "big")  # time of the file
            self.time_text = self.file.read(81)  # Time text
            self.modanim_text = self.file.read(81)  # ModAnim text
            self.radiossRun_text = self.file.read(81)  # RadiossRun text

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

            self.flagA = self.Ufread("i4", 10, 4, 1)
            self.nbNodes = int.from_bytes(self.file.read(4), "big")  # number of nodes
            self.nbFacets = int.from_bytes(
                self.file.read(4), "big"
            )  # number of 4nodes elements
            self.nbParts = int.from_bytes(self.file.read(4), "big")  # number of parts
            self.nbFunc = int.from_bytes(
                self.file.read(4), "big"
            )  # number of nodal scalar values
            self.nbEFunc = int.from_bytes(
                self.file.read(4), "big"
            )  # number of elemt scalar values
            self.nbVect = int.from_bytes(
                self.file.read(4), "big"
            )  # number of vector values
            self.nbTens = int.from_bytes(
                self.file.read(4), "big"
            )  # number of tensor values
            self.nbSkew = int.from_bytes(
                self.file.read(4), "big"
            )  # number of skews array of the skew values defined in uint16_t * 3000

        if self.nbSkew:
            self.skewValA = self.Ufread("uint16", self.nbSkew, 2, 1) / 3000

        # coordinates array: containing the x,y,z coordinates of each node
        self.coorA = self.Ufread("f", self.nbNodes, 4, 3)

        # element connectivity array with local node numbering [0 to (nbNodes-1)]
        if self.nbFacets:
            self.connectA = self.Ufread("i", self.nbFacets, 4, 4)

            self.delEltA = self.Ufread("S1", self.nbFacets, 1, 1)
            # deleted elements : the deleted elements stay in their original parts,
            # the delEltA indicates which elements are deleted or not

            self.nbDel2D = 0
            for i in range(self.nbFacets):
                int2D = self.delEltA[i]
                if int2D != 0:
                    self.nbDel2D += 1

        # parts definition: array containing an index on thelast facet which defines each part.
        if self.nbParts:
            self.defPartA = self.Ufread("i", self.nbParts, 4, 1)
            # part texts which defines the name of each part Each name does not exceed 50 characters.
            self.pTextA = self.Ufread("S50", self.nbParts, 50, 1)

        # array of the norm values for each nodes the norm are defined in uint16_t * 3000
        self.normFloatA = self.Ufread("uint16", self.nbNodes, 2, 3) / 3000

        # scalar values
        if self.nbFunc + self.nbEFunc:
            # array of total scalar functions names (nodal +  element)
            self.ftextA = self.Ufread("S81", self.nbFunc + self.nbEFunc, 81, 1)
            if self.nbFunc:
                self.funcA = self.Ufread("f", self.nbNodes * self.nbFunc, 4, 1)
            if self.nbEFunc:
                self.eFuncA = self.Ufread("f", self.nbFacets * self.nbEFunc, 4, 1)

        # vectors values
        if self.nbVect:
            # array of vector names
            self.vTextA = self.Ufread("S81", self.nbVect, 81, 1)

        # read the array of x,y,z vector values for each node and compute the norm array
        self.vectValA = self.Ufread("f", self.nbNodes * self.nbVect, 4, 3)

        # tensors values
        if self.nbTens:
            # array of tensor names
            self.tTextA = self.Ufread("S81", self.nbTens, 81, 1)
            # read the array of x,y,xy tensor values for each element
            self.tensValA = self.Ufread("f", self.nbTens * self.nbFacets, 4, 3)

        # mass : elementar and nodal masses
        if self.flagA[0]:
            self.eMassA = self.Ufread("f", self.nbFacets, 4, 1)
            self.nMassA = self.Ufread("f", self.nbNodes, 4, 1)

        # node and element numbering
        if self.flagA[1]:
            self.nodNumA = self.Ufread("i", self.nbNodes, 4, 1)
            self.elNumA = self.Ufread("i", self.nbFacets, 4, 1)
            # contains the internal node-element numbers

        if self.flagA[4]:
            #  hierarchy
            #          array of subset for each part
            self.part2subset2DA = self.Ufread("i", self.nbParts, 4, 1)
            #  array of material for each part
            self.partMaterial2DA = self.Ufread("i", self.nbParts, 4, 1)
            #  array of properties for each part
            self.partProperties2DA = self.Ufread("i", self.nbParts, 4, 1)

        # =============================================================================
        # 3D GEOMETRY
        # =============================================================================

        if self.flagA[2]:
            self.nbElts3D = int.from_bytes(
                self.file.read(4), "big"
            )  # number of  8nodes elements
            self.nbParts3D = int.from_bytes(
                self.file.read(4), "big"
            )  #  number of parts
            self.nbEFunc3D = int.from_bytes(
                self.file.read(4), "big"
            )  #  number of vol. elt scalar values
            self.nbTens3D = int.from_bytes(
                self.file.read(4), "big"
            )  #  number of tensor values

            # element connectivity array with local node
            #    numbering [0 to (nbNodes-1)]
            #        first element 1st node, first element 2nd node,
            #        first element 3rd node, first element 4th node,
            #        first element 5th node, first element 6th node,
            #        first element 7th node, first element 8th node,

            #        second element 1st node, second element 2nd node,
            #
            self.connect3DA = self.Ufread("i", self.nbElts3D, 4, 8)

            # As the deleted elements stay in their original
            #    parts,
            #        the delEltA indicates which elements are deleted
            #        or not"""
            self.delElt3DA = self.Ufread("bool", self.nbElts3D, 1, 1)
            self.nbEltDel3D = 0
            for idel in range(self.nbElts3D):
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

            self.defPart3DA = self.Ufread("i", self.nbParts3D, 4, 1)

            # Part texts which defines the name of each part
            #  Each name does not exceed 50 characters.
            self.pText3DA = self.Ufread("S50", self.nbParts3D, 50, 1)

            #  scalar values
            if self.nbEFunc3D:
                #  array of scalar functions names
                self.fText3DA = self.Ufread("S81", self.nbEFunc3D, 81, 1)
                #  array of nodal,element scalar values
                self.eFunc3DA = self.Ufread("f", self.nbEFunc3D * self.nbElts3D, 4, 1)

            # tensors values
            if self.nbTens3D:
                # array of tensor names
                self.tText3DA = self.Ufread("S81", self.nbTens3D, 81, 1)
                # read the array of x,y,z,xy,yz,zx tensor values for each element
                self.tensVal3DA = self.Ufread("f", self.nbElts3D * self.nbTens3D, 4, 6)
            # mass : nodal, elementar mass
            if self.flagA[0]:
                self.eMass3DA = self.Ufread("f", self.nbElts3D, 4, 1)

            # node and element numbering
            if self.flagA[1]:

                self.elNum3DA = self.Ufread("i", self.nbElts3D, 4, 1)

                # contains the internal node-element numbers

            if self.flagA[4]:

                # hierarchy
                # array of subset for each part
                self.part2subset3DA = self.Ufread("i", self.nbParts3D, 4, 1)
                # array of material for each part
                self.partMaterial3DA = self.Ufread("i", self.nbParts3D, 4, 1)
                # array of properties for each part
                self.partProperties3DA = self.Ufread("i", self.nbParts3D, 4, 1)

        # =============================================================================
        # 1D GEOMETRY
        # =============================================================================
        if self.flagA[3]:

            self.nbElts1D = int.from_bytes(
                self.file.read(4), "big"
            )  # number of 2 nodes elements
            self.nbParts1D = int.from_bytes(self.file.read(4), "big")  # number of parts
            self.nbEFunc1D = int.from_bytes(
                self.file.read(4), "big"
            )  # number of line. elt scalar values
            self.nbTors1D = int.from_bytes(
                self.file.read(4), "big"
            )  # number of torseur values
            self.isSkew1D = int.from_bytes(
                self.file.read(4), "big"
            )  # is there any skews
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

            self.defPart1DA = self.Ufread("i", self.nbParts1D, 4, 1)
            # part texts which defines the name of each part
            #    Each name does not exceed 50 characters.
            self.pText1DA = self.Ufread("S50", self.nbParts1D, 50, 1)

            # scalar values
            if self.nbEFunc1D:

                # array of scalar functions names

                self.fText1DA = self.Ufread("S81", self.nbEFunc1D, 81, 1)

                # array of nodal,element scalar values
                self.eFunc1DA = self.Ufread("f", self.nbElts1D * self.nbEFunc1D, 4, 1)

            # tensors values
            if self.nbTors1D:

                # array of tensor names
                self.tText1DA = self.Ufread("S81", self.nbTors1D, 81, 1)

                # read the array of x,y,z,xy,yz,zx tensor values for each element
                self.torsVal1DA = self.Ufread("f", self.nbElts1D * self.nbTors1D, 4, 9)

            if self.isSkew1D:

                # array of the skew number for each elt
                self.elt2Skew1DA = self.Ufread("i", self.nbElts1D, 4, 1)

            # mass : nodal, elementar mass
            if self.flagA[0]:

                self.eMass1DA = self.Ufread("f", self.nbElts1D, 4, 1)

            # node and element numbering
            if self.flagA[1]:

                self.elNum1DA = self.Ufread("i", self.nbElts1D, 4, 1)

            # contains the internal node-element numbers

            if self.flagA[4]:
                # hierarchy
                # array of subset for each part
                self.part2subset1DA = self.Ufread("i", self.nbParts1D, 4, 1)

                # array of material for each part
                self.partMaterial1DA = self.Ufread("i", self.nbParts1D, 4, 1)

                # array of properties for each part
                self.partProperties1DA = self.Ufread("i", self.nbParts1D, 4, 1)

        # hierarchy
        if self.flagA[4]:

            self.nbSubsets = int.from_bytes(
                self.file.read(4), "big"
            )  # number of subsets
            for i in range(self.nbSubsets):
                # subset name
                self.file.read(50)  # subsetText =

                # parent number
                self.numParent = int.from_bytes(self.file.read(4), "big")
                # number of subsets sons
                self.nbSubsetSon = int.from_bytes(self.file.read(4), "big")

                # list of son subset
                if self.nbSubsetSon:
                    self.Ufread("i", self.nbSubsetSon, 4, 1)  # subsetSonA =

                # number of 2D SubParts
                self.nbSubPart2D = int.from_bytes(self.file.read(4), "big")
                if self.nbSubPart2D:
                    # list of 2D SubParts
                    self.Ufread("i", self.nbSubPart2D, 4, 1)  # subPart2DA =

                # number of 3D SubParts
                self.nbSubPart3D = int.from_bytes(self.file.read(4), "big")
                if self.nbSubPart3D:
                    # list of 3D SubParts
                    self.Ufread("i", self.nbSubPart3D, 4, 1)  # subPart3DA =

                # number of 1D SubParts
                self.nbSubPart1D = int.from_bytes(self.file.read(4), "big")
                if self.nbSubPart1D:
                    # list of 1D SubParts
                    self.Ufread("i", self.nbSubPart1D, 4, 1)  # subPart1DA =

            # number of Material
            self.nbMaterial = int.from_bytes(self.file.read(4), "big")
            # number of Properties
            self.nbProperties = int.from_bytes(self.file.read(4), "big")
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
        if self.flagA[5]:

            self.nbNodesTH = int.from_bytes(
                self.file.read(4), "big"
            )  # number of Time History nodes
            self.nbElts2DTH = int.from_bytes(
                self.file.read(4), "big"
            )  # number of Time History 2D elements
            self.nbElts3DTH = int.from_bytes(
                self.file.read(4), "big"
            )  # number of Time History 3D elements
            self.nbElts1DTH = int.from_bytes(
                self.file.read(4), "big"
            )  # number of Time History 1D elements
            # node list
            self.nodes2THA = self.Ufread("i", self.nbNodesTH, 4, 1)
            # node names
            self.n2thTextA = self.Ufread("S50", self.nbNodesTH, 50, 1)

            # elt 2D list
            self.elt2DTHA = self.Ufread("i", self.nbElts2DTH, 4, 1)
            # elt 2D name
            self.elt2DthTextA = self.Ufread("S50", self.nbElts2DTH, 50, 1)

            # elt 3D list
            self.elt3DTHA = self.Ufread("i", self.nbElts3DTH, 4, 1)
            # elt 3D name
            self.elt3DthTextA = self.Ufread("S50", self.nbElts3DTH, 50, 1)

            # elt 1D list
            self.elt1DTHA = self.Ufread("i", self.nbElts1DTH, 4, 1)
            # elt 1D name
            self.elt1DthTextA = self.Ufread("S50", self.nbElts1DTH, 50, 1)

        # =============================================================================
        # READ SPH PART */
        # =============================================================================
        if self.flagA[7]:
            self.nbEltsSPH = int.from_bytes(self.file.read(4), "big")
            self.nbPartsSPH = int.from_bytes(self.file.read(4), "big")
            self.nbEFuncSPH = int.from_bytes(self.file.read(4), "big")
            self.nbTensSPH = int.from_bytes(self.file.read(4), "big")

            if self.nbEltsSPH:
                self.connecSPH = self.Ufread("i", self.nbEltsSPH, 4, 1)
                self.delEltSPH = self.Ufread("bool", self.nbEltsSPH, 1, 1)

            if self.nbPartsSPH:

                self.defPartSPH = self.Ufread("i", self.nbPartsSPH, 4, 1)

                # part texts which defines the name of each part
                #  Each name does not exceed 50 characters.
                self.pTextSPH = self.Ufread("S50", self.nbPartsSPH, 50, 1)

            if self.nbEFuncSPH:

                self.scalTextSPH = self.Ufread("S81", self.nbEFuncSPH, 81, 1)

                self.eFuncSPH = self.Ufread("f", self.nbEFuncSPH * self.nbEltsSPH, 4, 1)

            if self.nbTensSPH:
                # SPH tensors are just like 3D tensors
                self.tensTextSPH = self.Ufread("S81", self.nbTensSPH, 81, 1)
                self.tensValSPH = self.Ufread("f", self.bEltsSPH * self.nbTensSPH, 4, 6)

            # sph mass
            if self.flagA[0]:
                self.eMassSPH = self.Ufread("f", self.nbEltsSPH, 4, 1)

            # sph numbering
            if self.flagA[1]:
                self.nodNumSPH = self.Ufread("i", self.nbEltsSPH, 4, 1)

            # SPH HIERARCHY
            if self.flagA[4]:

                # parent number
                self.numParentSPH = self.Ufread("i", self.nbPartsSPH, 4, 1)
                self.matPartSPH = self.Ufread("i", self.nbPartsSPH, 4, 1)
                self.propPartSPH = self.Ufread("i", self.nbPartsSPH, 4, 1)


import os

animation = []
for i in os.listdir():
    if i[-4] == "A" and i[-3:].isnumeric():
        animation.append(Anime(i))
