Monte Carlo light transport: many photons, one by one, randomly "travel a step, leave a little energy, change direction" in tissue; counting them gives the distribution of light and the dose. This section shows **where the method comes from, what we reproduce, and what the frontier is doing**.

- **Simulation**: two models (skin with vessel at 500 nm, knee at 980 nm); change the settings and see the result. Every result is **computed live** on the server from your settings, not prepared in advance.
- **Validation**: any uniform slab, this engine against the independent adding–doubling method.
- **How it works**: the algorithm flowchart, key formulas, CPU parallelism and GPU, optimization directions.
