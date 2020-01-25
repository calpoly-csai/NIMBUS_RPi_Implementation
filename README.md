# NIMBUS_RPi_Implementation

## Benchmarking Data For Determining Optimal CPU

![alt text](https://raw.githubusercontent.com/calpoly-csai/NIMBUS_RPi_Implementation/master/Misc/Benchmarking_Output.png)

Based on the time for feature extraction and prediction for each wake word, it was determined that the Raspberry Pi 4 with 4 GB of RAM is the current optimal solution.
Each wake word buffer takes about 128 ms per prediction so the CPU will need to accomplish each prediction in less than that time.
