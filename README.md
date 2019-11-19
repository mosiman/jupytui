# Jupytui

A terminal client for Jupyter notebooks. 

The goal is to eventually be able to have a terminal client that modifies notebooks and connects to the kernel. Images and other graphics are possibly feasible using Kitty's [terminal graphics protocol](https://sw.kovidgoyal.net/kitty/graphics-protocol.html). 

## Stack

- urwid 
- python 3.7+
- Maybe Kitty

## Demo 

A most recent demo, reading the [census notebook](https://anaconda.org/jbednar/census/notebook)

So far, it's reading and navigating the JSON only. Not connected to any kernel. 

![Demo as of 2019-11-19](demo-2019-11-19.gif)


