'''
Copyright 2020 Ricardo Entz

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#!/usr/bin/env python3

import argparse
import numpy as np
from scipy import interpolate
from datetime import date
import svgwrite
import json

def write_default_config_file(tofile = True):
    conf = {
        "airfoil_input" : "naca0012.dat",
        "output_file"   : "gores.svg",
        "airfoil_name"  : "NACA0012",
        "envelope_length_m" : 1.1,
        "truncation_point_fraction" : 0.95,
        "n_points_render" : 250,
        "bunching_factor" : 3,
        "draw_base_airfoil" : True,
        "nb_gores"          : 4,
        "nb_gores_drawing"  : 3,
        "drawing_info"    : ["ELEMENTAL GmbH",
                             "Axisymmetric gore calculation tool v.1",
                             "Drawing generated on " + str(date.today()),
                             "Scale 1:1, Paper size: A0"],
        "text_box_width"  : 331,
        "text_box_height" : 59,
        "paper_width_mm"  : 841,
        "paper_height_mm" : 1189,
        "paper_margin_mm" : 10,
        "draw_margins"    : True,
        "draw_text_box"   : True,
        "cutting_clearance_mm" : 7.5,
        "draw_airfoil_name"         : True,
        "name_font_size"            : 20,
        "draw_centerline"           : True,
        "draw_length_lines"         : True,
        "length_lines_pitch_mm"     : 100,
        "construction_lines_width"  : 0.1,
        "solid_lines_width"         : 0.5,
        "solid_lines_color"         : "black"}
    
    if tofile:
        with open("gores_config.json","w") as fp:
            json.dump(conf, fp, indent = 4)
    else:
        return conf
        
def read_config_file(fname):
    with open(fname,"r") as fp:
        return json.load(fp)

def read_xfoil(filename):
    foil = np.genfromtxt(filename, skip_header=1)
    foil[foil[:,1] > 0, 0] *= -1
    foil[:,1] *= -1
    return foil


    
def setup_page(conf):
    w = conf["paper_width_mm"]
    h = conf["paper_height_mm"]
    m = conf["paper_margin_mm"]
    bw = conf["text_box_width"]
    bh = conf["text_box_height"]
    txt = conf["drawing_info"]
    
    dwg = svgwrite.Drawing(conf["output_file"], 
                           size=('{:d}mm'.format(w), '{:d}mm'.format(h)), 
                           viewBox=('0 0 {:d} {:d}'.format(w,h)))
    
    if conf["draw_margins"]:
        # Overall margin
        dwg.add(dwg.rect(insert = (m,m), 
                         size = (w-2*m,h-2*m),
                         fill="none",
                         stroke="black",
                         stroke_width=1))
    
    if conf["draw_text_box"]:
        dwg.add(dwg.rect(insert = (w-m-bw,h-m-bh), 
                         size = (bw,bh),fill="none",
                         stroke="black",
                         stroke_width=1))
        
        hook_y = h-m-bh+12
        for line in txt:
            dwg.add(dwg.text(line,
                             style = "font-size: 8pt;font-family:monospace",
                             insert = (w-m-bw+5,hook_y)))
            hook_y += 12
    
    return dwg
        
        
def plot_airfoil(dwg, X, Y,
                 le_position = (110,50),
                 airfoil_name = "BASE AIRFOIL",
                 font_size_mm = 20,
                 color = "black",
                 draw_centerline = True,
                 draw_length_lines = True,
                 draw_airfoil_name = True,
                 length_lines_pitch_mm = 100,
                 construction_lines_width = 0.1,
                 solid_lines_width = 0.5):
    # Draw airfoil
    centerline   = le_position[0]
    le_offset    = le_position[1]
    centerpoint  = le_offset + np.max(X) / 2
    

    w = 2.1 * np.max(Y)
    
    # Draw horizontal lines along length of the airfoil
    if draw_length_lines:
        ylist = list(np.arange(0,np.max(X),length_lines_pitch_mm))
        ylist.append(np.max(X))
        
        for y in ylist:
            dwg.add(dwg.line(start = (centerline - w/2, y + le_offset),
                             end =   (centerline + w/2, y + le_offset),
                             stroke = "grey",
                             stroke_width = construction_lines_width).dasharray([3,3]))
    if draw_centerline:    
        dwg.add(dwg.line(start        = (centerline, le_offset - 5),
                         end          = (centerline, le_offset + np.max(X) + 5),
                         stroke       = "grey",
                         stroke_width = construction_lines_width).dasharray([3,3]))
    
    # We draw the base shape as two halves
    pts = np.transpose(np.vstack((centerline+Y,le_offset+X)))
    dwg.add(dwg.polyline(pts, 
                         stroke = color, 
                         fill   = 'none',
                         stroke_width = solid_lines_width))
    pts = np.transpose(np.vstack((centerline-Y,le_offset+X)))
    dwg.add(dwg.polyline(pts, 
                         stroke = color, 
                         fill   = 'none',
                         stroke_width = solid_lines_width))
    if draw_airfoil_name:
        dwg.add(dwg.text(airfoil_name,
                         style = "font-size: {:f}m;font-family:Helvetica".format(
                                    font_size_mm/1000),
                         insert = (centerline+font_size_mm/2,centerpoint),
                         fill = color,
                         transform = "rotate(-90,{:f},{:f})".format(
                                    centerline+font_size_mm/2, centerpoint)))
        
def generate_airfoil_data(conf, airfoil_data):
    y_tilde = interpolate.InterpolatedUnivariateSpline(
                airfoil_data[:,0], airfoil_data[:,1])

    x = np.linspace(0,
                    conf["truncation_point_fraction"]**(1/conf["bunching_factor"]),
                    conf["n_points_render"])**conf["bunching_factor"]

    scale = conf["envelope_length_m"]
    
    X = x * scale * 1e3
    Y = y_tilde(x) * scale * 1e3
    L = 2 * np.pi * Y
    
    t = np.cumsum(np.sqrt(np.diff(X)**2 + np.diff(Y)**2))
    t = np.hstack((0,t))
    
    return X, Y, t, L

def cmd_arguments():
    parser = argparse.ArgumentParser(description="Generate airship gores based on an XFOIL shape")
    
    parser.add_argument('-c','--config', 
                        action="store",
                        default="gores_config.json",
                        help="Config file name and path")
    
    parser.add_argument('--confgen', 
                        action="store_true",
                        default=False,
                        help="Generates a neutral config file with all options")
    
    parser.add_argument('--confshow', 
                        action="store_true",
                        default=False,
                        help="Prints configuration before generating file")
    
    parser.add_argument('-o','--output', 
                        action="store",
                        default=None,
                        help="Output file name (overrides config file option)")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = cmd_arguments()
    
    if args.confgen:
        write_default_config_file()  
        exit()
        
    # Gets complete config to prevent KeyError and updated with user conf
    conf = write_default_config_file(tofile = False)
    conf.update(read_config_file(args.config))
    if args.output:
        conf["output_file"] = args.output
    if args.confshow:
        print(json.dumps(conf,indent=4))
    
    
    airfoil_data = read_xfoil(conf["airfoil_input"])
    
    X, Y, t, L = generate_airfoil_data(conf, airfoil_data)
    
    dwg = setup_page(conf)
    
    hook_x = conf["paper_margin_mm"] + conf["cutting_clearance_mm"]
    hook_y = conf["paper_margin_mm"] + conf["cutting_clearance_mm"]
    
    if conf["draw_base_airfoil"]:
        hook_x += np.max(Y)
        plot_airfoil(dwg, X, Y,
                     le_position            = (hook_x, hook_y),
                     airfoil_name           = conf["airfoil_name"],
                     font_size_mm           = conf["name_font_size"],
                     color                  = conf["solid_lines_color"],
                     draw_centerline        = conf["draw_centerline"],
                     draw_length_lines      = conf["draw_length_lines"],
                     draw_airfoil_name      = conf["draw_airfoil_name"],
                     length_lines_pitch_mm  = conf["length_lines_pitch_mm"],
                     construction_lines_width = conf["construction_lines_width"],
                     solid_lines_width      = conf["solid_lines_width"])
        hook_x += np.max(Y) + conf["cutting_clearance_mm"]

    for n_gores in conf["nb_gores_drawing"] * [conf["nb_gores"]]:
        hook_x += np.max(L / (2*n_gores))
        plot_airfoil(dwg, t, L/(2*n_gores),
             le_position              = (hook_x, hook_y),
             color                    = conf["solid_lines_color"],
             draw_centerline          = conf["draw_centerline"],
             draw_length_lines        = conf["draw_length_lines"],
             draw_airfoil_name        = False,
             length_lines_pitch_mm    = conf["length_lines_pitch_mm"],
             construction_lines_width = conf["construction_lines_width"],
             solid_lines_width        = conf["solid_lines_width"])
        hook_x += np.max(L / (2*n_gores)) + conf["cutting_clearance_mm"]
        
    dwg.save()