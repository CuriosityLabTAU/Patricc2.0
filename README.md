# Patricc
Open source of the Particc Authoring Tool and Hardware

## Authoring Tool
The Authoring Tool enables to record behaviors and interaction into Particc.

### Prerequisites
Skeleton Markers package: for Kinect use. http://wiki.ros.org/skeleton_markers

Dynamixel package: for motor commands. https://github.com/HumaRobotics/dynamixel_hr_ros

RosSerial package: for arduino communication. http://wiki.ros.org/rosserial

## Folder structure
blocks/ Contains the recorded blocks
sounds/ Contains the sound files to be imported into the blocks

images/ Contains image files of the robots and props

flow/   Contains the flow txt files that the RunFlow.py runs

## Creating new blocks
1. For a new project, with project_name: 
2. Create the following directories:
2.1. sounds/project_name
2.2. blocks/project_name

3. Prepare sounds in .mp3 format
4. Copy the .mp3 files to sounds/project_name/

5. Run AuthoringTool.py

6. In the Robot/Name, set the directory name and press set.
This will bring all the *.mp3 and *csv from sounds/*/ into the lip/sound lists.

7. In RecordAnimationBlock/save as, write the name of the new block

To record:
a. Check the "block"" radio button
b. Press record, the following will happen:
--> sleep 4 seconds
--> says hello (for preparation)
--> sleep 2
--> starts recording
* if "after"": has a number > 0, then it stops recording after this number of seconds

To record head movements
a. In Motors box:
b. select motor 2
c. press "set motor"
d. In "record animation block" box
e. press "replay and record block" and use the left/right keys to move the robot's head
---comment - when writing a lesson flow notice to call the correct file (with the added ".new")

To add sound files to an existing block
a. Select the right .mp3 file next to "load sound"
b. Mark "load sound"
c. Press "replay & record block"

## Create the flow
Create a new project_flow.txt file in flow/
The header:

robot, fuzzy
path, demo
props, avocado banana lemon sheep fish
start, block, fuzzy_hello, 2

Then come the different options of flow:
Blocks:
Syntax: number, block, "the block name", the_next_number 
Example: 2, block, fuzzy_hello, 3

Interaction with RFID:
Syntax:
number, wait, correct:"-prop +prop", true:number_for_true, false:number_for_false, timeout:number_for_timeout", duration:"length_in_seconds"
Example: 2, wait, correct:-fish, true:3, false:3, timeout:3, duration:1
Explanation: 
-prop waits for picking a prop up, e.g. -fish, true=picked up fish
+prop waits for returing a prop, e.g. +fish, true=returned fish
true: where to go if condition met
false: where to fo if condition not met
timeout: where to go if duration has passed

## Run the flow
Run RunFlow.py

1. Press Prepare.
If everything works, "OK"

2. Select with flow text file to run
The robot and the props will be written

3. Place the correct props and press refresh
If everything works, "Run"