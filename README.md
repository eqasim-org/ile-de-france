# An open synthetic population of Île-de-France

![Via Île-de-France](docs/via.png "Via Île-de-France")

This repository contains the code to create an open data synthetic population
of the Île-de-France region around in Paris.

- [How to use this pipeline to create your own scenario](docs/howto.md)
- [How to run a MATSim transport simulation for Île-de-France](docs/howto.md)

## Main reference

The main research reference for the synthetic population of Île-de-France is:

> Hörl, S. and M. Balac (2020) Reproducible scenarios for agent-based transport simulation: A case study for Paris and Île-de-France, Preprint, IVT, ETH Zurich, Zurich.

## What is this?

This repository contains the code to create an open data synthetic population
of the Île-de-France region around in Paris.
It takes as input several publicly
available data sources to create a data set that closely represents the
socio-demographic attributes of persons and households in the region, as well
as their daily mobility patterns. Those mobility patterns consist of activities
which are performed at certain locations (like work, education, shopping, ...)
and which are connected by trips with a certain mode of transport. It is known
when and where these activities happen.

Such a synthetic population is useful for many research and planning applications.
Most notably, such a synthetic population serves as input to agent-based
**transport simulations**, which simulate the daily mobility behaviour of people
on a spatially and temporally detailed scale. Moreover, such data has been used
to study the **spreading of diseases**, or the **placement of services** and facilities.

The synthetic population for Île-de-France can be generated from scratch by
everybody who has basic knowledge in using Python. Detailed [instructions
on how to generate a synthetic population with this repository](docs/howto.md) are available.

Although the synthetic population is independent of the downstream application
or simulation tool, we provide the means to create an input population for the
agent- and activity-based transport simulation framework [MATSim](https://matsim.org/).

This pipeline has been adapted to many other regions and cities around the world
and is under constant development. It is released under the GPL license, so feel free
to make adaptations, contributions or forks as long as you keep your code open
as well!

## Publications

- Hörl, S. and M. Balac (2020) Reproducible scenarios for agent-based transport simulation: A case study for Paris and Île-de-France, Preprint, IVT, ETH Zurich, Zurich.
- Hörl, S., Balac, M. and Axhausen, K.W. (2019) [Dynamic demand estimation for an AMoD system in Paris](https://ieeexplore.ieee.org/document/8814051),
paper presented at the 30th IEEE Intelligent Vehicles Symposium, Paris, June 2019.
- Hörl, S. (2019) [An agent-based model of Île-de-France: Overview and first results](https://slides.com/sebastianhorl/matsim-paris), presentation at Institut Paris Region, September 2019.
