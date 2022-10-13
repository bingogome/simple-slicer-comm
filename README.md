# simple-slicer-comm

## Introduction

This simple 3D Slicer script module enables soft real time UDP communication. Normally, multi-thread tasks are handled by CLI modules in 3D Slicer, because the software is single-threaded by design. CLI modules can write a read files as data input and output to 3D Slicer, so that delay can be an issue. There might be other solutions using CLI modules. This repository however, can be modified to be an unblocking thread so that single-threaded 3D Slicer has additional tasks processed in parallel to the main process.

## Demo

Here are two demo videos of this module: https://github.com/bingogome/documents/tree/main/simple-slicer-comm

## Citation

Please consider to cite the following paper in which this module was first used in published work.

@inproceedings{liu2022inside,
  title={Inside-out tracking and projection mapping for robot-assisted transcranial magnetic stimulation},
  author={Liu, Yihao and Liu, Shuya Joshua and Sefati, Shahriar and Jing, Tian and Kheradmand, Amir and Armand, Mehran},
  booktitle={Optical Architectures for Displays and Sensing in Augmented, Virtual, and Mixed Reality (AR, VR, MR) III},
  volume={11931},
  pages={57--70},
  year={2022},
  organization={SPIE}
}

Liu, Y., Liu, S. J., Sefati, S., Jing, T., Kheradmand, A., & Armand, M. (2022, March). Inside-out tracking and projection mapping for robot-assisted transcranial magnetic stimulation. In Optical Architectures for Displays and Sensing in Augmented, Virtual, and Mixed Reality (AR, VR, MR) III (Vol. 11931, pp. 57-70). SPIE.
