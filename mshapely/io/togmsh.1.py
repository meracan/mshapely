
def writeSLF(name):
    command = "gmsh {0}.geo -2 -smooth 10 -renumber -o  {0}.msh".format(name)
    print(ommand)
    subprocess.call(command, shell=True)
    command = "parserGMSH.py msh2slf {0}.msh".format(name)
    print(command)
    subprocess.call(command, shell=True)
    slfPath = "{0}.slf".format(name)
    slf2Path = "{0}.UTM9.slf".format(name)
    slf = SELAFIN(slfPath)

    newcoords = project_array(np.dstack([slf.MESHX, slf.MESHY])[0])
    slf.MESHX = newcoords[:, 0]
    slf.MESHY = newcoords[:, 1]

    z = np.zeros((1, slf.NPOIN2))
    slf.fole.update({'name': slf2Path})
    slf.fole.update({'hook': open(slf2Path, 'wb')})
    slf.appendHeaderSLF()
    slf.appendCoreTimeSLF(0.0)
    slf.appendCoreVarsSLF(z)
    slf.fole['hook'].close()

        with open(geoPath,"w") as geofile:

            points = self.points


            strPoints = ""
            # for point in upoints:
            #     strPoints += "Point({0:n}) = {{{1},{2},{3},{4}}};\n".format(point[0] + 1, point[3], point[4], 0,point[7])
            PID = 1


            strLines = ""
            strLoop = ""
            _strSurface = ""
            strSurface = ""
            strPSurface =""
            LID = 1
            LLID = 0
            polIds = np.unique(points[:, [1]])
            for ipol in polIds:
                ppoints = points[np.where(points[:, [1]] == ipol)[0]]
                for lineId in np.unique(ppoints[:, [2]]):
                    istart=LID
                    _points = ppoints[np.where(points[:, [2]] == lineId)[0]]
                    IPID=PID
                    for i in range(len(_points)-1):
                        p0=_points[i]
                        strPoints += "Point({0:n}) = {{{1},{2},{3},{4}}};\n".format(PID, p0[3], p0[4], 0, p0[7])
                        if(i == len(_points)-2):
                            strLines += "Line({0:n}) = {{{1:n},{2:n}}};\n".format(LID, PID, IPID)
                        else:
                            strLines += "Line({0:n}) = {{{1:n},{2:n}}};\n".format(LID, PID, PID + 1)
                        PID +=1
                        LID +=1


                    iend = LID - 1
                    LLID +=1
                    strLoop += "l{0:n} = newreg; ".format(LLID)
                    strLoop += "Line Loop(l{0:n}) = {{{1:n}:{2:n}}};\n".format(LLID, istart, iend)

                _strSurface += "s{0:n} = newreg;".format(1)
                strTs = ""
                for n in range(1, LLID):
                    strTs += "l{0:n},".format(n)
                strTs = strTs[:-1]
                strSurface += "Plane Surface(s{0}) = {{{1}}};".format(1, strTs)


            # insidePoints = self.savepoints
            # strinsidePoints = []
            # for i, point in enumerate(insidePoints):
            #     strinsidePoints.append("{0}".format(PID))
            #     strPoints += "Point({0:n}) = {{{1},{2},{3},{4}}};\n".format(PID, point[3], point[4], 0, point[7])
            #     PID += 1
            # strinsidePoints = ",".join(strinsidePoints)
            # strPSurface += "Point{{{0}}} In Surface{{s{1}}};".format(strinsidePoints, 1)

            strAttractorTreshold =""
            ATID=1
            strDefault = 'Field[1] = MathEval;Field[1].F = "30000";'
            gATID=[]
            gATID.append(str(1))

            # points[np.where(points[:, 7] <int(np.floor(minDist)))[0],7]=int(np.floor(minDist))
            points[np.where(points[:, 7] > 10000.0),7] =10000.0
            ppoints =points
            # attpoints = points[np.where(points[:, 7] >100.0)[0]]
            # factor = 10
            # uattpoints = np.unique(np.floor(ppoints[:, 7] / factor) * factor)
            uattpoints = np.concatenate([np.arange(10,100,10),np.arange(100,1000,100) , np.arange(1000, 11000, 1000)])

            points1000 = ppoints[np.where(ppoints[:, 7] >= 1000.0)]
            points100 = ppoints[np.where((ppoints[:, 7] < 1000.0) & (ppoints[:, 7] >= 100.0))]
            points10 = ppoints[np.where(ppoints[:, 7] < 100.0)]

            for i,density in enumerate(uattpoints):
                ATID +=1
                if (density < 100.0):
                    nodelist = points10[np.where(np.ceil(points10[:, 7] / 10.0) * 10.0 == density)[0], 0] + 1
                elif(density>=100.0 and density<1000.0):
                    nodelist = points100[np.where(np.ceil(points100[:, 7] / 100.0)*100.0 == density)[0],0]+1
                else:
                    nodelist = points1000[np.where(np.ceil(points1000[:, 7] / 1000.0) * 1000.0 == density)[0],0]+1

                if(len(nodelist)>0):
                    strnodelist = ",".join(["%d" % x for x in nodelist])
                    strAttractorTreshold +="Field[{0}] = Attractor;Field[{0}].NodesList = {{{1}}};".format(ATID,strnodelist)
                    ATID += 1
                    density = density*1.0
                    n = int(np.ceil(np.log2(30000 / density) / np.log2(1.2)))
                    distmax = np.sum(density * np.power(1.2,np.arange(1,n)))
                    strAttractorTreshold +="Field[{0}] = Threshold;Field[{0}].IField = {1};Field[{0}].DistMax = {3};Field[{0}].DistMin = 0;Field[{0}].LcMax = 30000;Field[{0}].LcMin = {2:.1f};\n".format(ATID,ATID-1,density,distmax)
                    gATID.append(str(ATID))

            ATID += 1
            _g = ",".join(gATID)
            strMin = "Field[{0}] = Min;Field[{0}].FieldsList = {{{1}}};\n".format(ATID,_g)
            strMin +="Background Field = {0};\n".format(ATID)
            strMin +="Mesh.LcIntegrationPrecision = 1e-3;\n"
            strMin +="Mesh.CharacteristicLengthExtendFromBoundary = 0;\n"
            strMin += "Mesh.CharacteristicLengthFromPoints = 0;\n"


            geofile.write("{0}\n".format(strPoints))
            geofile.write("{0}\n".format(strLines))

            geofile.write("{0}\n".format(strLoop))
            geofile.write("{0}\n".format(_strSurface))
            geofile.write("{0}\n".format(strSurface))
            geofile.write("{0}\n".format(strPSurface))
            geofile.write("{0}\n".format(strDefault))
            geofile.write("{0}\n".format(strAttractorTreshold))
            geofile.write("{0}\n".format(strMin))







            # groups=[]
            # for i, (points, pointsI) in enumerate(zip(self.polygonsPoints, self.pointsI)):
            #     for j,(pPoints, iPoints) in enumerate(zip(points, pointsI)):
            #         pPoints = np.asarray(pPoints)
            #         dPoints = np.asarray(cPoints[iPoints])
            #         dPoints = dPoints / 3.0
            #         groups[i][j] = np.column_stack((np.append(iPoints,iPoints[0]),pPoints, np.zeros(len(pPoints)), np.append(dPoints,dPoints[0])))
            #
            # lcount=1
            # scount =0
            # for polygons in groups:
            #     for ip, polygon in enumerate(polygons):
            #         istart=lcount
            #         for i,point in enumerate(polygon[:-1]):
            #             strPoints += "Point({0:n}) = {{{1},{2},{3},{4}}};\n".format(point[0]+1, point[1], point[2], point[3],point[4])
            #             strLines += "Line({0:n}) = {{{1:n},{2:n}}};\n".format(lcount, point[0]+1,  polygon[i+1][0]+1)
            #             lcount = lcount + 1
            #         iend = lcount -1
            #
            #         scount += 1
            #         strLoop += "l{0:n} = newreg; ".format(scount)
            #         strLoop += "Line Loop(l{0:n}) = {{{1:n}:{2:n}}};\n".format(scount, istart, iend)
            # _strSurface += "s{0:n} = newreg;".format(1)
            # strTs = ""
            # for n in range(1,scount):
            #     strTs +="l{0:n},".format(n)
            # strTs=strTs[:-1]
            # strSurface += "Plane Surface(s{0}) = {{{1}}};".format(1,strTs)
            #
            # geofile.write("{0}\n".format(strPoints))
            # geofile.write("{0}\n".format(strLines))
            #
            # geofile.write("{0}\n".format(strLoop))
            # geofile.write("{0}\n".format(_strSurface))
            # geofile.write("{0}\n".format(strSurface))