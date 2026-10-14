# Mincheng Li: data projects

Source for [min-star-code.github.io](https://min-star-code.github.io/), a portfolio of four public-data projects. Each page is static HTML, CSS and JavaScript with no build step and no backend.

- `index.html`: home page with one switch per project.
- `projects/`: one interactive page per project, with filters that update every chart.
- `data/`: compact data files generated from each project's cleaned output.
- `assets/`: shared styles and the small cross-filter chart engine.
- `build_data.py`, `build_pages.py`: regenerate `data/` and `projects/`. They read the four project folders, which live in their own repositories.
- `DESIGN.md`: the design specification the pages follow.

The analyses are independent work on open data and are not endorsed by the Government of Ontario, the City of Toronto, the TTC or Microsoft.
