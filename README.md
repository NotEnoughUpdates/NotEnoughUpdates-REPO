<!-- markdownlint-disable no-inline-html -->
<h1 align="center"> NotEnoughUpdates-REPO </h1>

<p align="center">
  <!-- lint -->
  <a href="https://github.com/NotEnoughUpdates/NotEnoughUpdates-REPO/actions" target="_blank">
    <img src="https://img.shields.io/github/actions/workflow/status/NotEnoughUpdates/NotEnoughUpdates-REPO/NotEnoughUpdates-REPO-Workflow.yml?label=lint&logo=github&logoColor=FFFFFF&branch=master" alt="lint">
  </a>
  <!-- license -->
  <a href="https://github.com/NotEnoughUpdates/NotEnoughUpdates-REPO/blob/master/LICENSE" target="_blank">
    <img src="https://img.shields.io/github/license/NotEnoughUpdates/NotEnoughUpdates-REPO?color=success&logo=github&logoColor=FFFFFF" alt="license">
  </a>
  <!-- lines -->
  <a href="https://github.com/NotEnoughUpdates/NotEnoughUpdates-REPO">
    <img src="https://tokei.rs/b1/github/NotEnoughUpdates/NotEnoughUpdates-REPO" alt="lines">
  </a>
  <!-- discord -->
  <a href="https://discord.gg/moulberry" target="_blank">
    <img src="https://img.shields.io/discord/516977525906341928?label=discord&color=success&logo=discord&logoColor=FFFFFF" alt="discord">
  </a>
</p>

This repository is used in order to store the various JSON files used for the Minecraft mod [NotEnoughUpdates](https://github.com/Moulberry/NotEnoughUpdates) and many more.

<h2 align="center"> How to contribute </h2>

To contribute to the item repo, you should use the tools provided by [Firmament](https://modrinth.com/mod/firmament) or [NEU](https://modrinth.com/mod/notenoughupdates).  
*(Using the NEU tools is no longer recommended due to the missing layer for SNBT files.)*

<h3 align="center"> How to enable and use item repo tools </h3>

### Firmament

1. Open the config menu with `/firm`
2. Go to the **Developer & Debug** section
3. Open the **Power Users** category
4. Set a keybind for **Export Item Stack** / **Export Recipe Data** / **Export NPC Location**

Once you’ve made changes, you can find them in your Minecraft folder under `.minecraft/.firmament/repo`.

> [!NOTE]  
> On some operating systems, folder starting with a period are hidden by default. To view the folder you have to enable hidden folders. (On how to do that please use your best friend in life called Google.)

<details>
<summary><b>How do I add missing items to the repo?</b></summary>
<br>

1. Press your keybind for **Export Item Stack**  
2. Open your Minecraft folder  
3. Upload the newly created `.json` and `.snbt` files to your own fork of the NEU-Repo  
   - JSON files can be found under `.firmament/repo/items`  
   - SNBT files can be found under `.firmament/repo/itemsOverlay/(Note 1)`  
     - **Note 1:** You may find more than one folder here. The numbers represent the Minecraft Data Version in which the item was exported.  
       Example: The data version for Minecraft `1.21.5` is `4325` (see the Minecraft Wiki: <https://minecraft.wiki/w/Data_version>).  
       If you encounter a data version that does not exist in the original NEU-Repo, don’t worry—just commit the new folder with your changes.
4. Make a pull request to the NEU-Repo  
5. Wait for it to be merged  

</details>

<details>
<summary><b>If I made changes outside of Minecraft, how do I make them appear in-game?</b></summary>

There are two ways to do this:  

1. Restart your Minecraft client  
2. Use the in-game Firmament command: `/firm repo reload`  

*Tip: Since you may need to do this more than once, you can set up a keybind with `/firm macros`.*  


**WARNING**  
If you made changes to an item’s lore, you need to re-sync the `nbttag` to make it correct again.  
*(Otherwise, our GitHub workflow will yell at you.)*  
To do this, run:  

```bash
/firm dev reexportlore <itemID>
```  

 Example: `/firm dev reexportlore WARDEN_HELMET`

</details>

### NotEnoughUpdates

1. Open the config menu with `/neu`  
2. Go to the **IQ Test** section and solve the test. *(If you can’t solve it, please stop trying to add anything.)*  
3. Go to the **APIs** section  
4. Open the **Repository** category  
5. Enable the **Edit Mode** toggle  
6. Set a keybind for **Instant Edit Keybind** (this is the equivalent of **Export Item Stack** in Firmament)  

> [!WARNING]  
> Even though this may cause your repository to become outdated, it is recommended to disable auto-updates for the repo.  
> To do this, open the **Repository** category again and toggle **Automatically Update Repository**.

Once these options are enabled, you can edit and add items in-game using the following keybinds:

- `k` - Opens the item editor.
  - TIP: typing 2 `&` converts into `§`
- `o` - While in an items recipe menu, add the recipe.
- `y` - Opens a pane on the left side of your inventory.
- left `ctrl` - Hold to show the NBT data of an item.
  - left `ctrl`+`h` - copies the nbt data to your clipboard.
- `b` - While viewing the essence guide of an item, add the essence to the essencecost.json.

Once you have made the changes you would like you can find the files located in `.minecraft\config\notenoughupdates\repo`.

If you need further help on how to contribute feel free to join the [discord](https://discord.gg/moulberry).
