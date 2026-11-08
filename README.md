



# NeuroEvolution-Racing
A Program where cars are trained to race on custom-built maps using the NEAT algorithm. The program includes a Map editor, simulation creator, and allows you to race along with the others!


## Premise
Evolve Neural Networks in order to race as fast as possible.

A level track can be created through running the "MapInterpreter.py" File
That track.

Cars in a NEAT simulation will continuously evolve to run the track in a visual manner. 

## Demo
<video src=https://github.com/user-attachments/assets/9c9280c3-5b13-4e62-b86b-020518af1734 controls width="100%">
</video>

## Usage

### RacingSim.py

This is the File where the simulation is being displayed and the NNs are being trained, aside from watching the cars run at a 30fps rate there are 3 modes of learning acceleration that you can toggle through by pressing the "a" key

#####1. Normal Mode (Default)
   Clock is locked to 30 fps, simulation runs for human view. Average generation time on a test map (100 generations,) is 20.867 seconds. I will call that the 'Normal Mode rate' which the other modes will be compared to.

#####2. Acceleration Mode (a%3 = 1)
   After Pressing 'a' once, the internal game clock is unlocked but the game will still display at 30fps. Average generation time on a test map (100 generations) was 0.598 seconds, being 3489% Faster than on Normal Mode

#####3. Hyper-Acceleration Mode (a%3 = 2)
   After Pressing 'a' twice, The display no longer updates with car positions and instead shows a stats overview screen at 10fps. Average generation time on a test map (100 generations) was 0.336 seconds, being 78% Faster than Acceleration Mode and 6104% faster than normal mode
