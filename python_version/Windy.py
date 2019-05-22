# -*- coding: UTF-8 -*-

import json
import math

class Windy:
    '单风层数据类'

    MIN_VELOCITY_SPEED = 0.2 # m/s
    EVOLVE_STEP = 500 # path step limit
    MIN_SEARCH_ZONE = 0.5 # degree
    MAX_SEARCH_ZONE = 5 # degree
    SCALE = 2000 # velocity keep frame
    Data = []
    Builder = [] # one wind grid
    Grid = [] # all grid
    Path = {} # all layers path
    lo1 = la1 = dy = dx = nx = ny = 0

    def __init__(self,DATA):
        self.Data = DATA
        self.Grid = self.__buildGrid(self.Data)
        # wind = self.evolvePath(39, 112, self.GRID['2019050706_10m.json'], 50, 200)
        # wind = self.__field(39.00000876234756, 112.00025601980208, grid_250mb)

    '======================================== PRIVATE ==============================='
    def __createBuilder(self,data):
        uComp = vComp = scalar = {}
        for record in data:
            parCategory = str(record['header']['parameterCategory'])
            parNumber = str(record['header']['parameterNumber'])
            case = parCategory + ',' + parNumber
            if(case == '1,2' or case == '2,2'):
                uComp = record
            elif(case == '1,3' or case == '2,3'):
                vComp = record
            else:
                scalar = record
        return self.__createWindBuilder(uComp, vComp)

    def __createWindBuilder(self, uComp, vComp):
        uData = uComp['data']
        vData = vComp['data']
        data = []

        for i in range(max(len(uData), len(vData))):
            data.insert(i, [uData[i], vData[i]])
        return {
            'header': uComp['header'],
            'data': data,
            'interpolate': self.__bilinearInterpolateVector
        }

    def __bilinearInterpolateVector(self, x, y, g00, g10, g01, g11):
        rx = 1 - x; ry = 1 - y
        a = rx * ry; b = x * ry; c = rx * y; d = x * y
        u = g00[0] * a + g10[0] * b + g01[0] * c +g11[0] *d
        v = g00[1] * a + g10[1] * b + g01[1] * c +g11[1] *d
        m = math.sqrt(u * u + v * v)
        return [u, v, m]

    def __buildGrid(self,data):
        builder = self.__createBuilder(data)
        header = builder['header']
        self.lo1 = header['lo1']
        self.la1 = header['la1']
        self.dy = header['dy']
        self.dx = header['dx']
        self.nx = header['nx']
        self.ny = header['ny']

        isContinuous = math.floor(self.nx * self.dx) >= 360
        grid = []
        p = 0
        for j in range(self.ny):
            row = []
            for i in range(self.nx):
                row.insert(i, builder['data'][p])
                p +=1
            if(isContinuous):
                row.append(row[0])
                grid.insert(j, row)
        return grid

    def __interpolateField(self):
        projection = {}
        columns = []
        pass

    def __interpolate(self, lat, lng):
        # if(Grid['grid'] == []):
        #     return
        dlng = lng - self.lo1
        i = dlng - math.floor(dlng / 360) * 360
        j = (self.la1 - lat) / self.dy
        fi = int(math.floor(i)); ci = fi + 1
        fj = int(math.floor(j)); cj = fj + 1

        if(self.Grid[fj]):
            row = self.Grid[fj]
            g00 = row[fi]; g10 = row[ci]
            if(g00 and g10 and self.Grid[cj]):
                row = self.Grid[cj]
                g01 = row[fi]
                g11 = row[ci]
                if(g01 and g11):
                    return self.__bilinearInterpolateVector(
                        i - fi,
                        j - fj,
                        g00, g10, g01, g11
                    )
        return

    def __field(self, lat, lng):
        ''''大地坐标系资料WGS-84
            长半径a=6378137 短半径b=6356752.3142 扁率f=1/298.2572236
            地球周长40075016m
        '''
        a = 6378137
        b = 6356752.3142
        avgR = 6371229
        f = 1 / 298.2572236
        pi = math.pi
        distance = self.__interpolate(lat, lng)
        disX = distance[0]; disY = distance[1]
        # degreeLat = b * pi / 180
        # degreeLng = a * pi / 180
        # dLat = (disY / degreeLat) * self.scale + lat
        # dLng = (disX / (degreeLng * math.cos(self.deg2rad(lat)))) * self.scale + lng
        degree = self.deg2rad(avgR)
        dLat = (disY / degree) * self.SCALE + lat
        dLng = (disX / (degree * math.cos(self.deg2rad(lat)))) * self.SCALE + lng
        return [dLat, dLng, distance[2]]

    def __distance(self, lat, lng, dLat, dLng):
        x = dLat - lat; y = dLng - lng
        return math.hypot(x, y)

    '======================================== PUBLIC ==============================='
    def deg2rad(self, deg):
        return deg / 180 * math.pi

    def rad2deg(self, rad):
        return rad / (math.pi / 180)

    def evolvePath(self, lat, lng, deslat = -1, deslng = -1):

        path = []
        closePoint = []

        guilder = [lat, lng, self.__interpolate(lat, lng)[2]]
        min_distance = self.__distance(guilder[0], guilder[1], deslat, deslng)
        cursor = 0
        while(guilder[2] >= self.MIN_VELOCITY_SPEED and cursor <= self.EVOLVE_STEP):
            path.append(guilder)
            cursor += 1
            guilder = self.__field(guilder[0], guilder[1])
            if(deslat != -1 and deslng != -1):
                cur_distance = self.__distance(guilder[0], guilder[1], deslat, deslng)
                if(cur_distance < min_distance):
                    min_distance = cur_distance
                    closePoint = [guilder[0], guilder[1], cursor, min_distance]
        return {
            'path': path,
            'closePoint': closePoint
        }

    def searchZone(self,path, closePoint, pointNumber):
        pass



