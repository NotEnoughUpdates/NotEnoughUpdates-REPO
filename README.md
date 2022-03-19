<!-- markdownlint-disable no-inline-html -->
<h1 align="center"> NotEnoughUpdates-REPO </h1>

<p align="center">
  <!-- lint -->
  <a href="https://github.com/NotEnoughUpdates/NotEnoughUpdates-REPO/actions" target="_blank">
    <img src="https://img.shields.io/github/workflow/status/NotEnoughUpdates/NotEnoughUpdates-REPO/JSON/master?label=lint&logo=github&logoColor=FFFFFF" alt="lint">
  </a>
  <!-- license -->
  <a href="https://github.com/NotEnoughUpdates/NotEnoughUpdates-REPO/blob/master/LICENSE" target="_blank">
    <img src="https://img.shields.io/github/license/NotEnoughUpdates/NotEnoughUpdates-REPO?color=success&logo=github&logoColor=FFFFFF" alt="license">
  </a>
  <!-- lines -->
  <a href="https://github.com/NotEnoughUpdates/NotEnoughUpdates-REPO">
    <img src="https://img.shields.io/tokei/lines/github/NotEnoughUpdates/NotEnoughUpdates-REPO?color=success&logo=github&logoColor=FFFFFF" alt="lines">
  </a>
  <!-- discord -->
  <a href="https://discord.gg/moulberry" target="_blank">
    <img src="https://img.shields.io/discord/516977525906341928?label=discord&color=success&logo=discord&logoColor=FFFFFF" alt="discord">
  </a>
</p>

This repository is used in order to store the various JSON files used for the Minecraft mod [NotEnoughUpdates](https://github.com/Moulberry/NotEnoughUpdates).

<h2 align="center"> How to contribute </h2>

In order to contribute to the item repo you should enable the item editor tools by editing your config, in your configNew.json (`.minecraft\config\notenoughupdates\configNew.json`) ensure the following values are set:

```json
"enableItemEditing": true,
"dev": true,
```

I would also highly recommend disabling auto update if you are in the middle of making changes otherwise they will be overwritten.

```json
"autoupdate": false,
```

Once you have these options enabled you can edit and add items in-game using the following keybinds:

- `k` - Opens the item editor.
  - TIP: typing 2 `&` converts into `§`
- `o` - While in an items recipe menu, add the recipe.
- `y` - Opens a pane on the left side of your inventory.
- left `ctrl` - Hold to show the NBT data of an item.
  - left `ctrl`+`h` - copies the nbt data to your clipboard.
- `n` - While viewing the essence guide, prints the essence costs to your log.

Once you have made the changes you would like you can find the files located in `.minecraft\config\notenoughupdates\repo`.

If you need further help on how to contribute feel free to join the [discord](https://discord.gg/moulberry) or contact `IRONM00N#0001` on discord.
