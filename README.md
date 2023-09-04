life.py

Simple example I put together when someone asked me about rendering 3D realtime in python for a 3D game of life they were trying to get running.  This is not the game of life update, just something I made up to update the RGB colors of a 3D point cloud.

This example renders a point cloud, so it's just putting up a simple ploygon camera-facing for each point in the point cloud.  A true solution may do a complex iso-surafce detection and rendering in each cube of the desired 3D space.  Well beyond the scope here.  This does do async keyboard events and rotate/zoom independent of the update loop (which runs much slower).

