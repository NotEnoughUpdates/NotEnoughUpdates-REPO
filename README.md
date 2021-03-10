<h1 align="center"> NotEnoughUpdates-REPO </h1>

<p align="center">
  <a href="https://discord.gg/moulberry" target="_blank">
    <img src="https://img.shields.io/discord/516977525906341928?label=discord&style=plastic" alt="discord">
  </a>
  <a href="https://github.com/Moulberry/NotEnoughUpdates-REPO/actions" target="_blank">
    <img src="https://img.shields.io/github/workflow/status/Moulberry/NotEnoughUpdates-REPO/JSON/master?label=lint&style=plastic" alt="lint">
  </a>
  <a href="https://github.com/Moulberry/NotEnoughUpdates-REPO/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/Moulberry/NotEnoughUpdates-REPO?style=plastic&color=44CC11" alt="license">
  </a>
  <a>
    <img src="https://img.shields.io/tokei/lines/github/Moulberry/NotEnoughUpdates-REPO?color=44CC11&style=plastic" alt="lines">
  </a>
</p>

This repository is used in order to store the various JSON files used for the Minecraft mod [NotEnoughUpdates](https://github.com/Moulberry/NotEnoughUpdates).

<h2 align="center"> How to contribute </h2>

In order to contribute to the item repo you should enable the item editor tools by editing your config, in your configNew.json (`.minecraft\config\notenoughupdates\configNew.json`) ensure the following values are set:

```json
"enableItemEditing": true,
"dev": true,
```

I would also highly recommend disabling auto update if you are in the middle of making changed otherwise they will be overwritten.

```json
"autoupdate": false,
```

Once you have these options enabled you can edit and add items in-game using the following keybinds:

* `k` - Open the item editor.
* `o` - While in an items recipe menu, add the recipe.
* `y` - Opens a pane on the right side of your inventory.
* `left ctrl` - Hold to show the NBT data of an item. 

Once you have made the changes you would like you can find the files located in `.minecraft\config\notenoughupdates\repo`.

If you need further help on how to contribute feel free to join the [discord](https://discord.gg/moulberry) or contact `IRONM00N#0001`.
