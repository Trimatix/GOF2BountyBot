README UNFINISHED

# GOF2BountyBot
A relatively small yet ambitious discord bot written in python, recreating some of the features of Galaxy on Fire 2. Currently, the standout features are the bounty hunting system, and the items/loadout/trading/dueling system.

# Architecture
The bot's code is essentially contained within `bountybot.py`, which uses the other sub-packages for data management.

## bbConfig
This package purely contains configuration data for the bot and, where possible, should provide data in a raw format without accessing non-standard libraries (including BB classes).

### \_\_init\_\_.py
This is the only module in which external library classes are acceptable. Currently, the script propogates databases in `bbConfig.bbConfig` with BountyBot's pseudo-constant objects. For example; it creates a dictionary of `bbObjects.items.weapon`s to be referenced by user `bbObjects.items.ship`s when *equipping*.
