## To Do

- Run numberings 
- Menu + keyboard shortcuts for adding, cutting, moving cells 
- MILESTONE 2: Communicate with jupyter kernel backend
- VI modal navigation
    > some modal shit like having a 'normal mode', 'insert mode', for now.
- Allow code cell output to be scrollable 

## Doing

- MILESTONE 1: Import and render jupyter notebook
    > What does this involve? note: no images for now.
    * [x] Figure out how to make scrollable listbox
    * [x] how to parse ipynb
    * [x] classes for different cells
    * [ ] Basic navigation
    * [ ] run numberings
- Basic navigation
    * [ ] VI like modes: 'Normal', 'Insert'
    * [ ] Open files
    * [ ] cut and paste cells
    * [ ] vim-like footer with mode
    * [x] coloured 'focus' 
- Render markdown with pixcat for latex, images
    > Use pixcat to render images. Will likely involve a rehaul of lots of things. 

## Done

- Figure out how to make dynamic listbox
- Make classes for different notebook cells
    > e.g. for code cells, they should be a 'pile' i.e. have both a 'code editing' cell and a non-editable output cell
    * [x] Code
    * [x] Markdown
    * [x] Raw
- Figure out how to parse .ipynb
    * [x] some of the image data in cencus.ipynb not being processed properly
    * [x] -> ex: `export(tf.shade ...)` has multiple data : an image, and a text/plain. For rn im only displaying the text/plain
