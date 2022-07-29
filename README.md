# simple-slicer-comm

## Introduction

This simple 3D Slicer script module enables soft real time UDP communication. Normally, multi-thread tasks are handled by CLI modules in 3D Slicer, because the software is single-threaded by design. CLI modules can write a read files as data input and output to 3D Slicer, so that delay can be an issue. There might be other solutions using CLI modules. This repository however, can be modified to be an unblocking thread so that single-threaded 3D Slicer has additional tasks processed in parallel to the main process.

## Demo

Here are two demo videos of this module: https://github.com/bingogome/documents/tree/main/simple-slicer-comm
