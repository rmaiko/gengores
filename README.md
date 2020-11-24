# gengores

Tool to generate airship gore drawings from an airfoil shape

Rotationally-symmetric blimps can be built from a series of "slices" called *gores*. 
This tool will help you to get any airfoil shape from XFOIL and generate a drawing to
scale for you to start working in your own airship projects!

If you need a step-by-step guide on how to build a Mylar envelope for your blimp I
recommend you to follow this outstanding [tutorial](https://www.rcgroups.com/forums/showthread.php?489372-Making-Mylar-Envelopes)

## Getting started

Just download the project and fire python with:

```python
python3 gengores.py
```

There are some typical dependencies such as:
* numpy
* scipy
* svgwrite

If you want to make sure you have all the dependencies, just use pip:

```python
pip3 numpy scipy svgwrite
```

## Advanced features
All the configuration parameters can be found in the [gores_config.json](https://github.com/rmaiko/gengores/blob/main/gores_config.json) file