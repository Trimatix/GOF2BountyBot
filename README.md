This repository is in the process of being ported onto the [BASED](https://github.com/Trimatix/BASED) platform. The new repository can be found here: [GOF2BountyBot](https://github.com/GOF2BountyBot/GOF2BountyBot)

---

# GOF2BountyBot
An ambitious discord bot written in python, recreating some of the features of Galaxy on Fire 2. Currently, the standout features are the bounty hunting system, and the items/loadout/trading/dueling system.

# Architecture
The 'main' file is `BB.bountybot`, which defines regular behaviour with `discord.Client.event`s.
Command definitions are located in the various modules of the `commands` package.

## bbConfig
This package purely contains configuration data for the bot and, where possible, should provide data in a raw format without accessing non-standard libraries (including BB classes). bbData configures objects contained within the game world, and bbConfig configures the game itself. Both are in the process of being replaced with JSON configuration files.

## bbDatabases
This package provides various database classes for the storage and management of game objects; commands,  bounties, guilds, users, and reaction menus.

## bbObjects
Contains definitions for all *game objects* - representing the players of the game (`bbGuild`, `bbUser`), items useable by the players (`bbInventory`, `bbInventorListing`, `items`) and playing functionality of the game itself (`bbShop`, `bounties`, `battles`). This package contains the useful `bbAliasable` abstract base class, which can be extended to define objects which can be referenced by a list of string names.

### bbObjects.battles
This is a draft package containing work-in-progress code for an upcoming overhaul of the duels system. Currently, the outcome of a duel is decided purely as a comparison if ship statistics. The new model proposed in this package is intended to more closely represent a real fight, by simulating a series of time quanta at which players have the opportunity to make use of their items.

### bbObjects.bounties
Defines classes necessary for the game's bounty hunting minigame; criminals, solar systems (used for pathfinding), bounties associating the two. Also contains bountyBoards, which are discord channels listing a guild's active bounties. `bbGlobals` maintains the game state, containing various databases managing the discord client, game objects and task scheduling. The `logging` module contains a simplified string event logger, capable of saving time-sorted event logs and exception traces to file.

### bbObjects.items
These modules define all objects that may be contained in a player's inventory. Note that all classes within this package inherit from the `bbItem` class, which in turn inherits from `bbAliasable`. Items have many descriptive attributes (e.g wiki link, manufacturer, emoji, icon), as well as functional attributes (e.g tech level, shop spawn rate, value). The `tools` package contains a new type of item with some 'use' function, that changes the game state in some way. Normal items do not have any inherent effect on the game state.

## commands
This is a new package containing concrete definitions of the concept of a commands module. Upon importing them, commands modules register bot commands to the **package** attribute, `commandsDB`. Commands modules are not automatically imported upon import of the package, which allows for conditional importing and enabling of groups of commands. Which commands modules are imported is decided by an attribute in `bbConfig`, a list of commands module names called `includedCommandModules`.

## lib
A package mostly independant from the game classes, defining a range of classes and functions useful in various cases throughout the bot. Of note is the `emojis` module, containing the `dumbEmoji` class. This class represents a union over discord custom emojis and unicode emojis.

## reactionMenus
Defines a variety of useful classes for automatically creating and managing reaction menus. Reaction menus are not guaranteed to be saveable by default, due to the highly generic nature of menu option behaviour. Reaction menus are provided in two groups of implementations, useful in different situations: menus inheriting directly from the `ReactionMenu` class are 'passive' reaction menus, and those inheriting from `SingleUserReactionMenu` are 'inline' menus.
* 'Inline' menus are designed to yield the calling thread until the menu is complete, allowing the calling code to proceed only once the results of the menu are present.
* 'Passive' menus are designed to be completely independant from the calling command, allowing it proceed in execution and triggering further behaviour upon events that occur within the menu using `TimedTask` expiry functions and menu option behaviour. For example, the command thread creating a `ReactionRoleMenu` need not remain in the event loop after creation of the menu.

## scheduling
Contains the generic `TimedTask` class, and `TimedTask` manager/scheduler `TimedTaskHeap`. `TimedTask` at its core, simply tracks when a requested amount of time has passed. Using an expiryFunction, a function call (whether synchronous or asynchronous), optionally with provided arguments, may be delayed by a given amount of time. Using autoRescheduling, this class can also be used to easily schedule reoccurring tasks. `TimedTaskHeap` maintains a min-heap of `TimedTask`s, sorted by their predicted expiration time. This allows efficient regular calling of the heap, by only testing the closest-expiring `TimedTask` for expiry.

## shipRenderer
At its base, `_render.py `implements calls to [blender](https://www.blender.org/) to render a named model with a named texture file. `shipRenderer.py` makes use of this, passing renderer arguments to blender through the `render_args` plaintext file. `shipRenderer` is capable of compositing multiple textures according to image masks,using the `Pillow` library. All of this behaviour can be called asynchronously to render a given `bbShip` with a series of texture files according to the ship's textureRegion masks, by using the `shipRenderer.renderShip` coroutine.

## userAlerts
Defines the versitile `UABase` class, which can be used to assign boolean alert subscriptions to alert behaviour, to be called upon certain events. For example, a guild may defined a `UA_Shop_Refresh` alert, corresponding to a role within the guild. Users may then subscribe to this alert, granting them the role. The shop refreshing `TimedTask` expiry function is directed to check for the existence of such an alert in guilds, and ping the alerting role.
