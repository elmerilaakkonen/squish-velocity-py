'''
Two stroke squish velocity calculator
Based on G.P. Blair's method
("Design and Simulation of Two-Stroke Engines", 1996, p. 325-330)

Copyright 2017 Elmeri Laakkonen

Licensed under GNU GPLv3
'''


from math import *
from tkinter import *
import tkinter.messagebox as mb

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

GAS_R = 287.058
GAMMA = 1.401

class SquishVelocityCalculator:
    def __init__(self):
        self.__window = Tk()
        self.__window.title("Squish velocity calculator")

        Label(self.__window, text="Squish velocity calculator").grid(row=0, columnspan=5)
        Label(self.__window, text="Input data below").grid(row=1, columnspan=5)
        Label(self.__window, text="Bore (mm):").grid(row=2, column=0, sticky=W, padx=15)
        Label(self.__window, text="Stroke (mm):").grid(row=3, column=0, sticky=W, padx=15)
        Label(self.__window, text="Conrod length (mm):").grid(row=4, column=0, sticky=W, padx=15)
        Label(self.__window, text="RPM:").grid(row=5, column=0, sticky=W, padx=15)
        Label(self.__window, text="Exhaust timing (deg ATDC):").grid(row=6, column=0, sticky=W, padx=15)
        Label(self.__window, text="Compression ratio:").grid(row=7, column=0, sticky=W, padx=15)
        Label(self.__window, text="Squish area ratio (%):").grid(row=8, column=0, sticky=W, padx=15)
        Label(self.__window, text="Squish angle (deg):").grid(row=9, column=0, sticky=W, padx=15)
        Label(self.__window, text="Squish clearance (mm):").grid(row=10, column=0, sticky=W, padx=15)


        self.bore_entry = Entry(self.__window)
        self.bore_entry.grid(row=2,column=3,sticky=E, padx=15)

        self.stroke_entry = Entry(self.__window)
        self.stroke_entry.grid(row=3,column=3,sticky=E, padx=15)

        self.conrod_entry = Entry(self.__window)
        self.conrod_entry.grid(row=4,column=3,sticky=E, padx=15)

        self.rpm_entry = Entry(self.__window)
        self.rpm_entry.grid(row=5,column=3,sticky=E, padx=15)

        self.exh_timingEntry = Entry(self.__window)
        self.exh_timingEntry.grid(row=6,column=3,sticky=E, padx=15)

        self.cr_entry = Entry(self.__window)
        self.cr_entry.grid(row=7,column=3,sticky=E, padx=15)

        self.sqarea_entry = Entry(self.__window)
        self.sqarea_entry.grid(row=8,column=3,sticky=E, padx=15)

        self.sqangle_entry = Entry(self.__window)
        self.sqangle_entry.grid(row=9,column=3,sticky=E, padx=15)

        self.sqclearance_entry = Entry(self.__window)
        self.sqclearance_entry.grid(row=10,column=3,sticky=E, padx=15)

        self.calc_button = Button(self.__window, text="Calculate", command=self.initialize)
        self.calc_button.grid(row=11,column=3,sticky=E, padx=15, pady=15)
        self.read_data()

    def initialize(self):
        try:
            self.bore = float(self.bore_entry.get())
            self.stroke = float(self.stroke_entry.get())
            self.conrod = float(self.conrod_entry.get())
            self.rpm = float(self.rpm_entry.get())
            self.exh_timing = float(self.exh_timingEntry.get())
            self.cr = float(self.cr_entry.get())
            self.sqarea_ratio = float(self.sqarea_entry.get())/100
            self.sqangle = float(self.sqangle_entry.get())
            self.sqclearance = float(self.sqclearance_entry.get())

            self.boreMeters = self.bore/1000
            self.strokeMeters = self.stroke/1000
            self.conrodMeters = self.conrod/1000
            self.crank = self.stroke/2
            self.crankMeters = self.crank/1000
            self.squish_clearance_meters = self.sqclearance/1000

            self.piston_area = pi*(self.boreMeters**2)/4
            self.swept_volume = self.piston_area*self.strokeMeters

            self.save_info()
            self.calculate()
        except:
            mb.askretrycancel("Error", "Input numerical values only.", icon=mb.ERROR, type="ok")

    def save_info(self):
        infostring = "{};{};{};{};{};{};{};{};{}".format(
             self.bore, self.stroke, self.conrod, self.rpm, self.exh_timing,
             self.cr, self.sqarea_ratio*100, self.sqangle, self.sqclearance
        )
        with open('data.txt', 'w') as filehandle:
            filehandle.write(infostring)

    def piston_position(self, crank_angle):
        CT = self.strokeMeters / 2
        alpha = degrees(asin(CT * sin(radians(crank_angle)) / self.conrodMeters))
        x = self.conrodMeters + CT - cos(radians(alpha)) * self.conrodMeters - cos(radians(crank_angle)) * CT
        return x

    def calculate(self):
        height_exh_open_meters1 = self.piston_position(self.exh_timing)
        trapped_swept_volume = self.piston_area*height_exh_open_meters1
        clearance_volume = trapped_swept_volume/(self.cr-1)
        squish_perpendicular_area = self.sqarea_ratio*self.piston_area
        bowl_area = self.piston_area-squish_perpendicular_area
        bowl_diam = sqrt(4*bowl_area/pi)
        bowl_radius = bowl_diam/2 #pois

        squish_radial_radius = (self.boreMeters-bowl_diam)/2
        squish_cone_height = tan(radians(self.sqangle))*squish_radial_radius
        squish_cone_volume = 1/3*pi*squish_radial_radius**2*squish_cone_height
        squish_bowl_volume = self.squish_clearance_meters*bowl_area

        squish_band_volume = self.squish_clearance_meters*squish_perpendicular_area
        if self.sqangle>0:
            squish_band_volume += squish_cone_volume

        bowl_volume = clearance_volume-squish_band_volume-squish_bowl_volume

        vol_squish1 = height_exh_open_meters1*squish_perpendicular_area+squish_band_volume
        vol_bowl1 = height_exh_open_meters1*bowl_area+bowl_volume+squish_bowl_volume
        vol_cyl1 = height_exh_open_meters1*self.piston_area+clearance_volume
        trapped_vol = vol_cyl1

        pressure_trap = 101325
        temp_trap = 293

        mass_trapped = pressure_trap * trapped_vol / (GAS_R * temp_trap)

        temp_cyl1 = temp_trap
        temp_squish1 = temp_cyl1
        temp_bowl1 = temp_cyl1

        pressure_cyl1 = pressure_trap
        pressure_squish1 = pressure_cyl1
        pressure_bowl1 = pressure_cyl1

        # RHO = ratio of heat of...
        rho_squish1 = pressure_squish1 / (GAS_R * temp_squish1)
        rho_bowl1 = pressure_bowl1 / (GAS_R * temp_bowl1)

        mass_squish1 = mass_trapped * vol_squish1 / vol_cyl1
        mass_bowl1 = mass_trapped - mass_squish1 #turha(ko?)

        degree_step = 1  # step
        dt = degree_step / (6 * self.rpm)  # delta t

        angleDown = (360 - self.exh_timing)
        self.pressure_max = 0
        self.max_sqv = 0
        self.max_deg = 0
        self.sum_energy = 0

        self.crank_angle = []
        self.sqv_array = []
        self.kinetic_energy_array = []
        while angleDown <= 360:
            height_exh_open_meters2 = self.piston_position(angleDown)
            dh = height_exh_open_meters1 - height_exh_open_meters2

            vol_squish2 = height_exh_open_meters2 * squish_perpendicular_area + squish_band_volume
            vol_bowl2 = height_exh_open_meters2 * bowl_area + squish_bowl_volume + bowl_volume
            vol_cyl2 = height_exh_open_meters2 * self.piston_area + clearance_volume

            pressure_cyl2 = pressure_trap * (pressure_trap / vol_cyl2) ** GAMMA
            temp_cyl2 = pressure_cyl2 * vol_cyl2 / (mass_trapped * GAS_R)
            rho_cyl2 = pressure_cyl2 / (GAS_R * temp_cyl2)

            pressure_squish2 = pressure_squish1 * (vol_squish1 / vol_squish2) ** GAMMA
            pressure_bowl2 = pressure_bowl1 * (vol_bowl1 / vol_bowl2) ** GAMMA

            mass_squish2 = mass_trapped * vol_squish2 / vol_cyl2

            delms = mass_squish1 - mass_squish2

            hsq = height_exh_open_meters1 + (self.squish_clearance_meters) - 0.5 * dh
            if self.sqangle >= 0: hsq += squish_cone_height
            sql = pi * bowl_diam
            asv = hsq * sql
            sqv = delms / (rho_cyl2 * asv * dt)
            self.sqv_array.append(sqv)
            self.crank_angle.append(360 - angleDown)
            if sqv > self.max_sqv:
                self.max_sqv = sqv
                self.max_deg = 360 - angleDown

            pressure_ratio = pressure_squish2 / pressure_bowl2
            if pressure_ratio > self.pressure_max: self.pressure_max = pressure_ratio

            kinetic_energy = 0.5 * delms * sqv ** 2
            self.sum_energy += kinetic_energy
            self.kinetic_energy_array.append(kinetic_energy)

            height_exh_open_meters1 = height_exh_open_meters2
            vol_squish1 = vol_squish2
            vol_bowl1 = vol_bowl2
            vol_cyl1 = vol_cyl2
            pressure_cyl1 = pressure_cyl2
            temp_cyl1 = temp_cyl2
            mass_squish1 = mass_squish2
            pressure_squish1 = pressure_cyl2
            pressure_bowl1 = pressure_cyl2

            angleDown = angleDown + degree_step
        self.plot()

    def plot(self):
        fig = plt.figure(0)
        plt.plot(self.crank_angle, self.sqv_array, 'r-')
        plt.xlabel('Crankshaft angle (° BTDC)')
        plt.ylabel('Velocity (m/s)')
        plt.title('Squish velocity')
        plt.grid(True)
        plt.text(2, 2, 'Max sq. v: {:.2f}m/s @{:.2f}°BTDC'.format(self.max_sqv, self.max_deg))
        plt.text(2, 1, "Max squish pressure ratio: {:.4f}".format(self.pressure_max))
        plt.text(2, 0, "Total kinetic energy squished: {:.2f}mJ".format(self.sum_energy * 1000))
        fig.canvas.set_window_title('Squish velocity')
        plt.show()

    def read_data(self):
        with open('data.txt', 'r') as filehandle:
            data_string = filehandle.read()

        if len(data_string) > 0:
            data = data_string.split(";")
            self.bore_entry.insert(0, data[0])
            self.stroke_entry.insert(0, data[1])
            self.conrod_entry.insert(0, data[2])
            self.rpm_entry.insert(0, data[3])
            self.exh_timingEntry.insert(0, data[4])
            self.cr_entry.insert(0, data[5])
            self.sqarea_entry.insert(0, data[6])
            self.sqangle_entry.insert(0, data[7])
            self.sqclearance_entry.insert(0, data[8])


    def start(self):
        self.__window.mainloop()


ui = SquishVelocityCalculator()
ui.start()
