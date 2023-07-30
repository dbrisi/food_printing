#################################
##### DIGITAL MANUFACTURING #####
## TEAM 4 TWISTED TRIANGLE CODE #
#################################

## IMPORT BASIC PACKAGES
import math as m

# CONSTANTS
FR = 200 # mm/s FEEDRATE
EX = 0.5 # EXTRUSION
lines = [] # ARRAY TO HOLD GCODE TEXT
eol = "\n" # "END OF LINE" VARIABLE
dToR = m.pi/180 # DEGREE-TO-RADIAN CONVESION

############################################
### FCT TO FILL ARRAY WITH GCODE TEXT ###
############################################
def fillLines():

  # INPUT VALUES
  side = float(input('Enter initial side length: '))
  step_height = float(input('Enter height per layer: ')) # mm, HEIGHT PER LAYER
  side_change = float(input('Enter the side length change increment: ')) #mm, CHANGE IN SIDE LENGTH
  rot = float(input('Enter the degrees of rotation: ')) # deg, ROTATION
  singleOrDouble = "S"
  singleOrDouble = input("Single (S) or Double (D) Triangle? ").upper()

  # TRIANGLE PROPERTIES
  height = 0 # mm, INITIAL HEIGHT
  rad = side/m.sqrt(3) # mm, RADIUS FROM CENTER OF CIRCUMSCRIBED EQ. TRIANGLE
  th0_V1 = 210 # deg -- VERTEX 1 POLAR ANGLE
  th0_V2 = 330 # deg -- VERTEX 2 POLAR ANGLE
  th0_V3 = 90  # deg -- VERTEX 3 POLAR ANGLE

  # INITIALIZE GCODE SETUP
  lines.append("T0" + eol)  # SELECT EXTRUDER
  lines.append("G21"+ eol) # SET UNITS TO MM
  lines.append("G92 X0 Y0 Z0 E0" + eol) # SET CURRENT POS TO BE ORIGIN
  lines.append("G90"+ eol) # SET ABSOLUTE COORDINATES


  lines.append(f"G0 X{side+15}" + eol) # MOVE > 1.5cm AWAY FROM TRIANGLE
  lines.append("G1 E0.25" + eol) # EXTRUDE SMALL AMOUNT (PRIME NOZZLE)
  lines.append(f"G0 X0 Y0 Z0 E0" + eol) # BACK TO ORIGIN

  # CALL FCT TO PRINT SINGLE OR DOUBLE TRIANGLES
  if singleOrDouble == "S":
    singleTriangle(side, side_change, rot, height, step_height, rad, th0_V1, th0_V2, th0_V3, lines)
  elif singleOrDouble == "D":
    doubleTriangle(side, side_change, rot,height,step_height,rad,th0_V1,th0_V2,th0_V3,lines)
  else:
    print("You didn't choose a valid response. We'll run a double triangle version.")
    doubleTriangle(side,side_change,rot,height,step_height,rad,th0_V1,th0_V2,th0_V3,lines)

  # finish print
  lines.append("G91"+ eol) # CHANGE TO RELATIVE POSITION
  lines.append("G1 Z10 E-2 F200" + eol) # MOVE UP AND RETRACT PLUNGER A BIT
  lines.append(f"G1 X{side + 15} F400 " + eol) # MOVE AWAY FROM PRINT
  lines.append("G28") # HOME PRINTER

###########################
### SINGLE TRIANGLE FCT ###
###########################
def singleTriangle(side, side_change, rot, height, step_height, rad, v1, v2, v3, lines):
  verySmall = 1e-10 # FOR SCIENTIFIC NOTATION BUG
  area = m.sqrt(3)/4*side**2 # mm^2, INITIAL AREA OF (BASE) TRIANGLE

  while area > 230:

    ### VERTEX 1 ###
    v1 = float(v1 + rot)
    x1,y1 = float(rad*m.cos( v1*dToR ) ), float(rad*m.sin( v1*dToR ) )
    # FIXING FOR SCIENTIFIC NOTATION BUG
    if abs(x1) < abs(verySmall):
      x1 = 0
    if abs(y1) < abs(verySmall):
      y1 = 0

    ### VERTEX 2 ###
    v2 = float(v2 + rot)
    x2, y2 = float(rad*m.cos( v2*dToR ) ), float(rad*m.sin( v2*dToR ) )
    # FIXING FOR SCIENTIFIC NOTATION BUG
    if abs(x2) < abs(verySmall):
      x2 = 0
    if abs(y2) < abs(verySmall):
      y2 = 0

    ### VERTEX 3 ###
    v3 = float(v3 + rot)
    x3,y3 = float(rad*m.cos( v3*dToR ) ), float(rad*m.sin( v3*dToR ) )
    # FIXING FOR SCIENTIFIC NOTATION BUG
    if abs(x3) < abs(verySmall):
      x3 = 0
    if abs(y3) < abs(verySmall):
      y3 = 0

    # ADD VERTICE LINES TO GCODE
    lines.append(f"G1 X{x2} Y{y2} Z{height} E{EX} F{FR}" + eol)
    lines.append(f"G1 X{x1} Y{y1} Z{height} E{EX} F{FR}" + eol)
    lines.append(f"G1 X{x3} Y{y3} Z{height} E{EX} F{FR}" + eol)

    # INCREASE HEIGHT FOR NEXT LAYER --> NOT SURE ABOUT THIS -YL
    height += step_height # INCREASE HEIGHT
    # ADD LINE TO GCODE
    lines.append(f"G1 Z{height}" + eol) # GO UP WITHOUT EXTRUDING

    # UPDATE FOR NEW (SMALLER TRIANGLE)
    side -= side_change # DECREASE SIDE
    rad = side/m.sqrt(3) # DECREASE RADIUS OF CIRCUMSCRIBED CIRCLE
    area = m.sqrt(3)/4*side**2 # RECALCULATE AREA OF TRIANGLE

###########################
### DOUBLE TRIANGLE FCT ###
###########################
def doubleTriangle(side, side_change, rot, height, step_height, rad, v1, v2, v3, lines):
  verySmall = 1e-10 # FOR SCIENTIFIC NOTATION BUG
  minArea = 2 # mm^2, SMALLEST ALLOWABLE PRINTED TRIANGLE
  spacing = 1.5 # mm
  radSmall = rad - spacing
  sideSmall = radSmall*m.sqrt(3)
  areaSmall = m.sqrt(3)/4*sideSmall**2 # mm^2, INITIAL AREA OF (BASE) TRIANGLE

  while areaSmall > minArea:

    ### VERTEX 1 ###
    v1 = float(v1 + rot)
    x1,y1 = float(rad*m.cos( v1*dToR ) ), float(rad*m.sin( v1*dToR ) )
    x1Small,y1Small = float(radSmall*m.cos( v1*dToR ) ), float(radSmall*m.sin( v1*dToR ) )
    # FIXING FOR SCIENTIFIC NOTATION BUG
    if abs(x1) < abs(verySmall):
      x1 = 0
    if abs(y1) < abs(verySmall):
      y1 = 0
    if abs(x1) < abs(verySmall):
      x1Small = 0
    if abs(y1Small) < abs(verySmall):
      y1Small = 0

    ### VERTEX 2 ###
    v2 = float(v2 + rot)
    x2, y2 = float(rad*m.cos( v2*dToR ) ), float(rad*m.sin( v2*dToR ) )
    x2Small,y2Small = float(radSmall*m.cos( v2*dToR ) ), float(radSmall*m.sin( v2*dToR ) )
    # FIXING FOR SCIENTIFIC NOTATION BUG
    if abs(x2) < abs(verySmall):
      x2 = 0
    if abs(y2) < abs(verySmall):
      y2 = 0
    if abs(x2Small) < abs(verySmall):
      x2Small = 0
    if abs(y2Small) < abs(verySmall):
      y2Small = 0

    ### VERTEX 3 ###
    v3 = float(v3 + rot)
    x3,y3 = float(rad*m.cos( v3*dToR ) ), float(rad*m.sin( v3*dToR ) )
    x3Small,y3Small = float(radSmall*m.cos( v3*dToR ) ), float(radSmall*m.sin( v3*dToR ) )
    # FIXING FOR SCIENTIFIC NOTATION BUG
    if abs(x3) < abs(verySmall):
      x3 = 0
    if abs(y3) < abs(verySmall):
      y3 = 0
    if abs(x3Small) < abs(verySmall):
      x3Small = 0
    if abs(y3Small) < abs(verySmall):
      y3Small = 0

    # ADD VERTICE LINES TO GCODE
    lines.append(f"G1 X{x1} Y{y1} Z{height} E{EX} F{FR}" + eol)
    lines.append(f"G1 X{x2} Y{y2} Z{height} E{EX} F{FR}" + eol)
    lines.append(f"G1 X{x3} Y{y3} Z{height} E{EX} F{FR}" + eol)
    lines.append(f"G1 X{x1Small} Y{y1Small} Z{height} E{EX} F{FR}" + eol)
    lines.append(f"G1 X{x2Small} Y{y2Small} Z{height} E{EX} F{FR}" + eol)
    lines.append(f"G1 X{x3Small} Y{y3Small} Z{height} E{EX} F{FR}" + eol)

    # INCREASE HEIGHT FOR NEXT LAYER --> NOT SURE ABOUT THIS -YL
    height += step_height # INCREASE HEIGHT
    # ADD LINE TO GCODE
    lines.append(f"G1 Z{height}" + eol) # GO UP WITHOUT EXTRUDING

    # UPDATE FOR NEW (SMALLER) TRIANGLES
    side -= side_change # DECREASE SIDE
    rad = side/m.sqrt(3) # DECREASE RADIUS OF CIRCUMSCRIBED CIRCLE
    radSmall = rad - spacing # OFFSET SMALLER TRIANGLE
    sideSmall = radSmall*m.sqrt(3) # OFFSET SMALLER TRIANGLE
    areaSmall = m.sqrt(3)/4*side**2 # RECALCULATE AREA OF SMALLER TRIANGLE

##################################
### FCT TO WRITE GCODE TO FILE ###
##################################
def writeToFile():
  fileName = input('Enter a file name (no extension): ')
  fileName = fileName + ".gcode"
  with open(fileName, 'w') as f:
    f.writelines(lines)

################
### MAIN FCT ###
################
def main():

  fillLines()
  writeToFile()

main()
