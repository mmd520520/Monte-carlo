How do we know the simulation is right? Solve the same problem with a **completely different method** and see whether the answers agree.

Adding–doubling is a deterministic solution for a uniform slab: no random numbers, fully independent of Monte Carlo. Pick any slab below (air on both sides) and both methods run once. A difference within ±3 standard errors means they agree; the automated tests check four such slabs every time.
