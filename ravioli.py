################################################
############# DIGITAL MANUFACTURING ############
## TEAM 4 - RAVIOLI REDEFINED - 3D PRINT CODE ##
################################################

## IMPORT BASIC PACKAGES
import math as m

# CONSTANTS
FR = 200 #mm/s DEFAULT FEEDRATE                                           //FIX LATER
EX = .5 #mm (?) DEFAULT EXTRUSION AMOUNT (DISTANCE PLUNGED (?), ASSUMED)  //FIX LATER
lines = [] # ARRAY TO HOLD GCODE TEXT
eol = "\n" # "END OF LINE" VARIABLE
dToR = m.pi/180 # DEGREE-TO-RADIAN CONVERSION
OFFSET = 50 # POSITIVE OFFSET (SO NO NEGATIVE VALUES)
### OFFSET DUE TO TOOL CHANGE NEEDS TO BE EXPERIMENTED WITH
height = 0 #mm, initial height
### BASED ON PRINTER (TYPICALLY)
xShiftTool = -17.75 #mm SHIFT DUE TO TOOL CHANGE (X-DISTANCE FROM T0 TO T1)


# FEEDRATES AND EXTRUSION AMOUNTS FOR BOTH MATERIALS (MAY DIFFER)
FR0 = FR
FR1 = 3*FR # CHANGE IF NECESSARY
EX0 = EX
EX1 = EX # CHANGE IF NECESSARY

#########################################
### FCT TO FILL ARRAY WITH GCODE TEXT ###
#########################################
def fillLines(height):

 # INPUT VALUES
 baseDiameter = float(input('Enter base diameter (mm) of print area: '))  #mm, DIAMETER OF BASE PRINT
 baseRadius = baseDiameter/2 #mm, RADIUS OF BASE PRINT
 petalRadius = float(input('Enter the radius (mm) for each petal: '))  #mm, RADIUS OF PETALS
 numPetals = int(input("Enter the number of petals for the base")) # NUMBER OF PETALS
 stepHeight = float(input('Enter height (mm) per layer: ')) #mm, HEIGHT PER LAYER
 ##print('Enter the distance (mm) decrement (nominal = .75) ') #mm, DECREASING SIZE OF BASE
 diamDecrement = float(input('For no decremental change, enter 0: ')) #mm
 baseLayers = int(input('Enter the number of layers for the base: ')) # BASE LAYER COUNT
 wallLayers = int(input('Enter the number of layers for the walls: ')) # WALL LAYER COUNT
 rot = int(input('Enter the degrees of rotation: ')) #deg, ROTATION
  # INITIALIZE GCODE SETUP
 lines.append("T0" + eol)  # SELECT EXTRUDER 1
 lines.append("G21"+ eol) # SET UNITS TO MM
 lines.append("G92 X0 Y0 Z0 E0" + eol) # SET CURRENT POS TO BE ORIGIN
 lines.append("G90"+ eol) # SET ABSOLUTE COORDINATES

 # PRIME NOZZLES
 lines.append(f"G0 X{baseRadius+125}" + eol) # MOVE > 1.5cm AWAY FROM TRIANGLE
 lines.append("G1 E0.25" + eol) # EXTRUDE SMALL AMOUNT (PRIME NOZZLE) FROM T0
 lines.append(f"G1 X{baseRadius+125} E0" + eol) # MAKE SURE EXTRUSION IS AWAY FROM PRINT
 lines.append("T1" + eol) # TOOL CHANGE TO T1
 lines.append("G1 E0.25" + eol) # EXTRUDE SMALL AMOUNT (PRIME NOZZLE) FROM T1
 lines.append(f"G1 X{baseRadius+125} E0" + eol) # MAKE SURE EXTRUSION IS AWAY FROM PRINT
 lines.append("T0" + eol) # TOOL CHANGE BACK TO T0
 lines.append(f"G0 X0 Y0 Z0 E0" + eol) # BACK TO ORIGIN

 # CALL FCTS TO PRINT
 height = basePrint(baseRadius, petalRadius, numPetals, baseLayers, stepHeight, EX0, FR0, height)
 height = wallPrint(baseRadius, petalRadius, numPetals, wallLayers, stepHeight, EX0, FR0, height, rot)
 height = fillingPrint(baseRadius, int(wallLayers * (5/10)), stepHeight, EX1, FR1, height)
 height = topPrint(baseRadius, baseLayers, stepHeight, EX0, FR0, height)
 # GOING BACK TO INITIAL POSITION TO SET UP SPIROGRAPH FUNCTION
 lines.append(f"G1 X{baseRadius + 55} Y{baseRadius + 55} Z15 E0" + eol)
 top_spiro(numPetals, baseRadius, petalRadius, height)
  # finish print
 lines.append("G91"+ eol) # CHANGE TO RELATIVE POSITION
 lines.append("T0" + eol)
 lines.append("G1 Z10 E-2 F200" + eol) # MOVE UP AND RETRACT PLUNGER A BIT
 lines.append("T1" + eol)
 lines.append("G1 E-2" + eol)
 lines.append(f"G1 X{baseRadius + 15} F400 " + eol) # MOVE AWAY FROM PRINT
 lines.append("G28") # HOME PRINTER


######################
### BASE PRINT FCT ###
######################
def basePrint(baseR, petalR, petalNum, layers, stepHeight, extr, feed, height):
 baseCircleExtrusion = 5 # EXTRUSION FOR OUTER CIRCLE
 petalExtrusion = .35 # EXTRUSION FOR EACH PETAL
 DECREMENT = 2 # nominally ~2 #mm, DECREMENT TO FILL BASE (NEEDS EXPERIMENTING)
 minPrintArea = m.pi # mm^2, SMALLEST ALLOWABLE PRINTED TRIANGLE (RADIUS OF 1 mm)
 petalAngle = 360/petalNum*dToR #radians, degrees between petals
  # PRINT X LAYERS OF BASE
 for i in range(layers):

   # LOOP AROUNT FOR CIRCLE BASE
   extr = baseCircleExtrusion # EXTRUSION FOR BASE CIRCLE
   rad = baseR # INITIALIZE RADIUS TO PRINT
   currentBaseArea = m.pi*rad**2 # CALCULATE INITIAL BASE AREA TO PRINT
   x,y = rad + OFFSET, 0 + OFFSET  # INITIALIZE STARTING X,Y

   # PRINT OUT BASE CONCENTRIC CIRCLES TO FILL PRINT AREA
   while currentBaseArea > minPrintArea:
     # OUTPUT GCODE LINES --> EXTRUDE ARC/CIRCLE(S)
     lines.append(f"G1 X{x} Y{y} Z{height}" + eol) #MOVE TO START POINT
     lines.append(f"G2 X{x} Y{y} I{-rad} J{0} Z{height} E{extr} F{feed}" + eol)

     # UPDATE BASE CIRCLE WHILE LOOP PARAMETERS
     x -= DECREMENT # DECREASE LOCATION (AND RESULTANT RADIUS)
     rad -= DECREMENT  # DECREASE THE RADIUS OF CIRCLE TO PRINT
     currentBaseArea = m.pi*rad**2 # RECALCULATE BASE AREA
     extr *= (rad - DECREMENT)/(rad) # DECREASE EXTRUSION AMOUNT

   # # MOVE BACK TO START POINT (ON THE RADIUS OF BASE CIRCLE)
   lines.append(f"G1 Z{height + 3}" + eol)
   lines.append(f"G1 X{baseR + OFFSET} Y{0 + OFFSET} Z{height + 3} E{.2}"  + eol)
   lines.append(f"G1 Z{height} E{.2}" + eol)

   # LOOP AROUND FOR PETALS
   extr = petalExtrusion # EXTRUSION AMOUNT FOR PETALS
   for i in range(petalNum + 1):
     if i != 0:
       # CALCULATE NEW X,Y POSITIONS FOR START/END OF PETAL
       x,y = baseR*m.cos(petalAngle * i), baseR*m.sin(petalAngle * i)
       # OUTPUT GCODE LINES --> EXTRUDE PETAL ARC(S)
       lines.append(f"G3 X{x + OFFSET} Y{y + OFFSET} R{petalR} Z{height} E{extr} F{feed}" + eol)

   # UPDATE HEIGHT PARAMETER AND RAISE PRINTHEAD
   height += stepHeight # INCREASE HEIGHT FOR NEXT LAYER
   # OUTPUT GCODE LINES --> GO UP WITHOUT EXTRUDING
   lines.append(f"G1 Z{height}" + eol)
  # RETURN "height" FOR SUBSEQUENT PRINTING
 return height

######################
### WALL PRINT FCT ###
######################
def wallPrint(baseR, petalR, petalNum, layers, stepHeight, extr, feed, height, rot):
 baseCircleExtrusion = 5 # EXTRUSION FOR OUTER CIRCLE
 petalExtrusion = .35 # EXTRUSION FOR PETALS
 DECREMENT = 2 # nominally ~2 #mm, DECREMENT TO FILL BASE (NEEDS EXPERIMENTING)
 minPrintArea = m.pi # mm^2, SMALLEST ALLOWABLE PRINTED TRIANGLE (RADIUS OF 1 mm)
  # PRINT X LAYERS OF WALL(S)
 for i in range(layers):
   # CALCULATE PETAL ANGLE (FOR NEW X,Y LOCATIONS OF EACH ARC)
   petalAngle = 360/petalNum*dToR #radians, degrees between petals

   # MOVE TO START POINT (ON THE RADIUS OF BASE CIRCLE)
   extr = baseCircleExtrusion # EXTRUSION FOR OUTER CIRCLE
   lines.append(f"G1 X{baseR + OFFSET} Y{0 + OFFSET} Z{height}" + eol)
   lines.append(f"G2 X{baseR + OFFSET} Y{0 + OFFSET} I{-baseR} J{0} Z{height} E{extr} F{feed}" + eol)

   # PRINT PETALS
   extr = petalExtrusion # EXTRUSION FOR PETALS
   for j in range(petalNum + 1):
     # if j != 0:
       # CALCULATE NEW X,Y POSITIONS FOR START/END OF PETAL
       x = baseR*m.cos( (petalAngle * (j+1) ) + (i * rot * dToR) )
       y = baseR*m.sin( (petalAngle * (j+1) ) + (i * rot * dToR) )
       # OUTPUT GCODE LINES --> EXTRUDE PETAL ARC(S)
       lines.append(f"G3 X{x + OFFSET} Y{y + OFFSET} R{petalR} Z{height} E{extr} F{feed}" + eol)

   # UPDATE HEIGHT PARAMETER AND RAISE PRINTHEAD
   height += stepHeight # INCREASE HEIGHT FOR NEXT LAYER
   # OUTPUT GCODE LINES --> GO UP WITHOUT EXTRUDING
   lines.append(f"G1 Z{height}" + eol)

   # GO OUT A BIT FOR OPTION TO SWAP SYRINGES
   lines.append(f"G1 X{baseR*1.5 + OFFSET} Y{0 + OFFSET} Z{height}" + eol)

 # RETURN "height" FOR SUBSEQUENT PRINTING
 return height

######################
### FILL PRINT FCT ###
######################
def fillingPrint(baseR, layers, stepHeight, extr, feed, height):
 baseCircleExtrusion = 5 # EXTRUSION FOR BASE CIRCLE
 DECREMENT = 2 # nominally ~2 #mm, DECREMENT TO FILL BASE (NEEDS EXPERIMENTING)
 minPrintArea = m.pi # mm^2, SMALLEST ALLOWABLE PRINTED TRIANGLE (RADIUS OF 1 mm)
  lines.append("T1" + eol) # TOOL CHANGE

 # PRINT X LAYERS OF BASE
 for i in range(layers):

   # LOOP AROUNT FOR CIRCLE BASE
   extr = baseCircleExtrusion # EXTRUSION FOR BASE CIRCLE
   fillRad = baseR # UPDATE RADIUS FOR FILLING
   # DECREASE RADIUS AND EXTRUSION AMOUNT (4 DECREMENTS)
   for i in range(4):
     fillRad -= DECREMENT
     extr *= ( (fillRad - DECREMENT)/(fillRad) )
   currentBaseArea = m.pi*fillRad**2 # CALCULATE INITIAL BASE AREA TO PRINT
   x,y = fillRad + OFFSET, 0 + OFFSET  # INITIALIZE STARTING X,Y

   # PRINT OUT BASE CONCENTRIC CIRCLES TO FILL PRINT AREA
   while currentBaseArea > minPrintArea:
     # OUTPUT GCODE LINES --> EXTRUDE ARC/CIRCLE(S)
     lines.append(f"G1 X{x + xShiftTool} Y{y} Z{height}" + eol) #MOVE TO START POINT
     lines.append(f"G2 X{x + xShiftTool} Y{y} I{-fillRad} J{0} Z{height} E{extr} F{feed}" + eol)

     # UPDATE BASE CIRCLE WHILE LOOP PARAMETERS
     x -= DECREMENT # DECREASE LOCATION (AND RESULTANT RADIUS)
     fillRad -= DECREMENT  # DECREASE THE RADIUS OF CIRCLE TO PRINT
     currentBaseArea = m.pi*fillRad**2 # RECALCULATE BASE AREA
     extr *= (fillRad - DECREMENT)/(fillRad) # DECREASE EXTRUSION AMOUNT
  lines.append("T0" + eol)

 # RETURN "height" FOR SUBSEQUENT PRINTING
 return height

#####################
### TOP PRINT FCT ###
#####################
def topPrint(baseR, layers, stepHeight, extr, feed, height):
 baseCircleExtrusion = 5 # EXTRUSION AMOUNT FOR BASE CIRCLE
 DECREMENT = 2 # nominally ~2 #mm, DECREMENT TO FILL BASE (NEEDS EXPERIMENTING)
 minPrintArea = m.pi # mm^2, SMALLEST ALLOWABLE PRINTED TRIANGLE (RADIUS OF 1 mm)
  # PRINT X LAYERS OF TOP
 for i in range(layers):

   # LOOP AROUNT FOR CIRCLE BASE
   extr = baseCircleExtrusion # EXTRUSION AMOUNT FOR BASE CIRCLE
   rad = baseR # INITIALIZE RADIUS TO PRINT
   currentBaseArea = m.pi*rad**2 # CALCULATE INITIAL BASE AREA TO PRINT
   x,y = rad + OFFSET, 0 + OFFSET  # INITIALIZE STARTING X,Y

   # PRINT OUT BASE CONCENTRIC CIRCLES TO FILL PRINT AREA
   while currentBaseArea > minPrintArea:
     # OUTPUT GCODE LINES --> EXTRUDE ARC/CIRCLE(S)
     lines.append(f"G1 X{x} Y{y} Z{height}" + eol) #MOVE TO START POINT
     lines.append(f"G2 X{x} Y{y} I{-rad} J{0} Z{height} E{extr} F{feed}" + eol)

     # UPDATE BASE CIRCLE WHILE LOOP PARAMETERS
     x -= DECREMENT # DECREASE LOCATION (AND RESULTANT RADIUS)
     rad -= DECREMENT  # DECREASE THE RADIUS OF CIRCLE TO PRINT
     currentBaseArea = m.pi*rad**2 # RECALCULATE BASE AREA
     extr *= (rad - DECREMENT)/(rad) # DECREASE EXRUSION AMOUNT

   # # MOVE BACK TO START POINT (ON THE RADIUS OF BASE CIRCLE)
   lines.append(f"G1 Z{height + 3}" + eol)
   if (baseR + OFFSET) != 75.0 and (0 + OFFSET) != 50.0 and (height + 3) != 14:
     lines.append(f"G1 X{baseR + OFFSET} Y{0 + OFFSET} Z{height + 3} E{.2}"  + eol)
     lines.append(f"G1 Z{height} E{.2}" + eol)

   # UPDATE HEIGHT PARAMETER AND RAISE PRINTHEAD
   height += stepHeight # INCREASE HEIGHT FOR NEXT LAYER
   # OUTPUT GCODE LINES --> GO UP WITHOUT EXTRUDING
   lines.append(f"G1 Z{height}" + eol)
  # RETURN "height" FOR SUBSEQUENT PRINTING
 return height

def top_spiro(petalNum, baseR, petalR, height):
 feed = 200 # FEED RATE FOR TOP SPIROGRAPH PRINT
 baseCircleExtrusion = 5 # EXTRUSION AMOUNT FOR BASE CIRCLE
 petalExtrusion = .35 # EXTRUSION AMOUNT FOR PETALS
  petalAngle = 360/petalNum*dToR #radians, degrees between petals

 extr = petalExtrusion # EXTRUSION AMOUNT FOR BASE CIRCLE
 for q in range(2):
   for i in range(petalNum + 2):
     # CALCULATE NEW X,Y POSITIONS FOR START/END OF PETAL
     x,y = baseR*m.cos(petalAngle * i + 25*q), baseR*m.sin(petalAngle * i + 25*q)
     # OUTPUT GCODE LINES --> EXTRUDE PETAL ARC(S)
     lines.append(f"G2 X{x + OFFSET} Y{y + OFFSET} R{-petalR} Z{height} E{extr} F{feed}" + eol)

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
  fillLines(height)
  writeToFile()

main()
