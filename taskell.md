## To Do

- Run numberings 
- Menu + keyboard shortcuts for adding, cutting, moving cells 
- MILESTONE 2: Communicate with jupyter kernel backend
- Allow code cell output to be scrollable 
- Split out into different files
- Use prompt toolkit / ptpython for editable cells
- When first opening notebook, first cell is not in focus (not coloured green)
- Vi-mode: buffers for `d`, `y` and other shit
- Render markdown with pixcat for latex, images
    > Use pixcat to render images. Will likely involve a rehaul of lots of things. 
- Some display data, turn into button and opens in `imv`
- Integrate with nbformat's ipynb library for easy saving

## Doing

- Experiment with the jupyter_client api
    > These are notes, not sub tasks.
    * [x] Threading > processing for zmq listeners, because they don't *really* need their own cpu/mem space (they're just listening)
    * [x] Use flags to stop listeners in threads
    * [x] Multiple listeners seems to share the same kernel client just fine
- Vi-mode: `:` for commands
    > priority for this should be bumped because it allows for easy testing of shit, especially threaded functions and shit Last thing i'm doing: configuring keypress for frame
    * [ ] open
    * [ ] write
    * [x] Just be able to type shit in
    * [x] Popup for feedback, etc
    * [x] exit

## Done

- Figure out how to make dynamic listbox
- MILESTONE 1: Make classes for different notebook cells
    > e.g. for code cells, they should be a 'pile' i.e. have both a 'code editing' cell and a non-editable output cell
    * [x] Code
    * [x] Markdown
    * [x] Raw
- MILESTONE 1: Figure out how to parse .ipynb
    * [x] some of the image data in cencus.ipynb not being processed properly
    * [x] -> ex: `export(tf.shade ...)` has multiple data : an image, and a text/plain. For rn im only displaying the text/plain
- MILESTONE 1: Vi-mode
    > Need to make a modal manager for 'nav' and 'insert' modes.
    * [x] Footer with current mode
    * [x] Manage keypress (hjkl, arrow move)
    * [x] Manage keypress `<Esc>` to return to 'normal' mode. 
    * [x] Manage keypress `i`, `a` `<Enter>` to enter 'insert' mode
- MILESTONE 1: Basic navigation
    * [x] VI like modes: 'Normal', 'Insert'
    * [x] vim-like footer with mode
    * [x] coloured 'focus' 
- MILESTONE 1: Import and render jupyter notebook
    > What does this involve? note: no images for now.
    * [x] Figure out how to make scrollable listbox
    * [x] how to parse ipynb
    * [x] classes for different cells
    * [x] Basic navigation
    * [x] run numberings
