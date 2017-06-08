# Maya

## Remote Rendering/Processing

To send instances off to remote processing you can use the ```Processing Location``` tool to setup the renderlayers. You'll find the ```Processing Location``` tool under the ```pyblish-grill``` menu.

## Ftrack

When launching Maya from Ftrack there will be an initial setup of the scene, depending on the custom attributes that are available. These custom attributes will be queried from the parent entity of the task.

Description | Ftrack Attributes
--- | ---
First frame of frame range | fstart
Last frame of frame range | fend
Frame rate | fps
Resolution width | width
Resolution height | height

The resolution will only be set once, when initially launching Maya. You can force the settings to be applied on start up, by unchecking the attribute ```Ftrack Resolution Set``` on the ```defaultResolution``` node.

# [BACK](index.md)
