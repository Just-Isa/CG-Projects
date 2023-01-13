# RayTracer

## Necessary Libraries:
- numpy
- pillow
- multiprocessing
--- 

## Running Instructions:

1. Navigate into the ./RayTracer folder
2. Run python .\RayTracer.py width height [-mp]/[-squirrel] coreCount
    
    - -mp for multiprocessed rendering of the instanciated Scene
    - -squirrel for the multiprocessed rendering of the squirrel.obj

Examples:
    
    Example command for Normal rendering: python .\RayTracer.py 200 200 -mp 4
    Example command for Squirrel: python .\RayTracer.py 50 50 -squirrel 8

## Recommended Core count is > 4
## Recommended width/height of rendered image is < 500x500 (< 200x200 for squirrel)




